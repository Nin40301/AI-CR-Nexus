
import time
import cv2
import yaml
import os
import logging
import argparse
from threading import Thread, Event
from queue import Queue, Empty

from emulator.adb_capture import AdbCapture
from emulator.adb_actions import AdbActions
from vision.object_detection import ObjectDetector
from ai.game_state import GameState
from ai.decision_system import DecisionSystem

def setup_logging(log_file_path):
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    logging.basicConfig(filename=log_file_path, level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)

class BotCoordinator:
    def __init__(self, config, dry_run=False):
        self.config = config
        self.dry_run = dry_run

        # Inicializar módulos
        self.adb_capture = AdbCapture(adb_path=config["emulator"]["adb_path"],
                                      device_id=config["emulator"]["device_id"],
                                      timeout=config["emulator"].get("adb_command_timeout", 5))
        
        # Obter resolução do dispositivo
        self.screen_resolution = self.adb_capture.get_device_resolution()
        if not self.screen_resolution:
            raise RuntimeError("Não foi possível obter a resolução do dispositivo ADB. Verifique a conexão.")

        self.game_resolution_width = config["emulator"].get("resolution_width", 1920)
        self.game_resolution_height = config["emulator"].get("resolution_height", 1080)
        self.game_resolution = (self.game_resolution_width, self.game_resolution_height)

        self.adb_actions = AdbActions(adb_path=config["emulator"]["adb_path"],
                                      device_id=config["emulator"]["device_id"],
                                      screen_resolution=self.screen_resolution,
                                      game_resolution=self.game_resolution,
                                      dry_run=self.dry_run,
                                      tap_delay_ms=config["main_loop"].get("tap_delay_ms", 100),
                                      timeout=config["emulator"].get("adb_command_timeout", 5))
        
        self.object_detector = ObjectDetector(config_path="config.yaml")
        self.game_state = GameState()
        self.decision_system = DecisionSystem(self.game_state, config)

        # Filas para comunicação entre threads
        self.frame_queue = Queue(maxsize=1) # Frame raw da captura
        self.processed_frame_queue = Queue(maxsize=1) # Frame com detecções para display
        self.decision_queue = Queue(maxsize=1) # Decisões do agente

        self.stop_event = Event()
        self.frame_id_counter = 0

        logging.info(f"Resolução do dispositivo ADB: {self.screen_resolution[0]}x{self.screen_resolution[1]}")
        logging.info(f"Resolução lógica do jogo para mapeamento: {self.game_resolution_width}x{self.game_resolution_height}")
        if self.dry_run:
            logging.info("Modo DRY RUN ativado. Nenhuma ação será executada no dispositivo real.")

    def _capture_thread(self):
        while not self.stop_event.is_set():
            start_time = time.time()
            try:
                frame = self.adb_capture.screencap()
                if frame is not None: # Verifica se o frame não é None
                    if not self.frame_queue.full(): # Evita bloquear se a fila estiver cheia
                        self.frame_queue.put((frame, self.frame_id_counter, start_time))
                        self.frame_id_counter += 1
                else:
                    logging.warning("Frame ADB vazio. Ignorando.")
            except RuntimeError as e:
                logging.error(f"Erro na captura ADB: {e}")
            
            # Controlar a taxa de captura para não sobrecarregar o sistema
            elapsed_time = time.time() - start_time
            capture_delay = self.config["main_loop"].get("capture_delay_sec", 0.05) # Novo config para delay de captura
            if elapsed_time < capture_delay:
                time.sleep(capture_delay - elapsed_time)

    def _vision_thread(self):
        while not self.stop_event.is_set():
            try:
                frame, frame_id, capture_time = self.frame_queue.get(timeout=0.1) # Pequeno timeout para não bloquear
                detection_start_time = time.time()
                detected_objects = self.object_detector.detect_objects(frame)
                detection_end_time = time.time()

                # Preparar frame para display e colocar na fila
                frame_display = frame.copy()
                for obj in detected_objects:
                    x, y, w, h = obj["bbox"]
                    cv2.rectangle(frame_display, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame_display, obj["name"], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                if not self.processed_frame_queue.full():
                    self.processed_frame_queue.put((frame_display, frame_id, capture_time, detection_start_time, detection_end_time, detected_objects))

            except Empty:
                pass # Nenhuma nova imagem na fila, continua
            except Exception as e:
                logging.error(f"Erro na thread de visão: {e}")
            
            time.sleep(self.config["main_loop"].get("vision_delay_sec", 0.05)) # Novo config para delay de visão

    def _decision_action_thread(self):
        while not self.stop_event.is_set():
            try:
                # Obter o frame processado mais recente para a decisão
                frame_display, frame_id, capture_time, detection_start_time, detection_end_time, detected_objects = self.processed_frame_queue.get(timeout=0.1)

                # Atualização do Estado do Jogo
                self.game_state.update_state(detected_objects, frame_id) # Passa frame_id para o GameState

                # Decisão
                decision_start_time = time.time()
                decision = self.decision_system.make_decision() # Decisão já inclui o agente
                decision_end_time = time.time()

                # Execução da Ação
                action_start_time = time.time()
                if decision["action"] == "click":
                    game_x, game_y = decision["coords"]
                    self.adb_actions.tap(game_x, game_y)
                elif decision["action"] == "play_card":
                    card_name = decision.get("card_name") 
                    card_index = decision.get("card_index")
                    target_coords = decision["coords"]
                    
                    card_bbox = None
                    if card_name:
                        for card in self.game_state.get_hand_cards():
                            if card["name"] == card_name:
                                card_bbox = card["bbox"]
                                break
                    elif card_index is not None and len(self.game_state.get_hand_cards()) > card_index:
                        card_bbox = self.game_state.get_hand_cards()[card_index]["bbox"]

                    if card_bbox:
                        card_center_x = card_bbox[0] + card_bbox[2] // 2
                        card_center_y = card_bbox[1] + card_bbox[3] // 2
                        self.adb_actions.play_card((card_center_x, card_center_y), target_coords)
                    else:
                        logging.warning(f"Carta para jogar não encontrada (nome: {card_name}, índice: {card_index}).")
                elif decision["action"] == "wait":
                    pass # Nenhuma ação física, apenas espera
                action_end_time = time.time()

                # Logs de Desempenho
                total_cycle_time = action_end_time - capture_time # Tempo total desde a captura
                fps = 1 / total_cycle_time if total_cycle_time > 0 else 0

                if self.config["main_loop"]["log_performance"]:
                    logging.info(f"Frame ID: {frame_id} | Cycle Time: {total_cycle_time:.4f}s | FPS: {fps:.2f} | Det. Time: {detection_end_time - detection_start_time:.4f}s | Dec. Time: {decision_end_time - decision_start_time:.4f}s")

                # Adicionar estado do jogo e logs ao frame para visualização
                cv2.putText(frame_display, f"Elixir: {self.game_state.get_elixir()}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame_display, f"Phase: {self.game_state.get_game_phase()}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame_display, f"Last Reward: {self.game_state.get_last_reward():.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame_display, f"FPS: {fps:.2f}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # Salvar frame de debug se configurado
                if self.config["main_loop"].get("debug_screenshots_path") and self.config["main_loop"].get("save_debug_screenshots", False):
                    debug_path = os.path.join(self.config["main_loop"]["debug_screenshots_path"], f"debug_frame_{frame_id}_{int(time.time())}.png")
                    os.makedirs(os.path.dirname(debug_path), exist_ok=True)
                    cv2.imwrite(debug_path, frame_display)

                # Colocar frame para display na fila principal
                if not self.processed_frame_queue.full(): # Usar a mesma fila para display
                     # A fila processed_frame_queue já contém o frame_display
                     pass # Não precisa colocar novamente, apenas o main loop vai pegar

            except Empty:
                pass # Nenhuma nova detecção na fila, continua
            except Exception as e:
                logging.error(f"Erro na thread de decisão/ação: {e}")
            
            time.sleep(self.config["main_loop"].get("decision_delay_sec", 0.05)) # Novo config para delay de decisão

    def run(self):
        logging.info("Iniciando threads do bot...")
        capture_t = Thread(target=self._capture_thread, daemon=True)
        vision_t = Thread(target=self._vision_thread, daemon=True)
        decision_action_t = Thread(target=self._decision_action_thread, daemon=True)

        capture_t.start()
        vision_t.start()
        decision_action_t.start()

        # Loop principal para visualização (deve rodar no thread principal)
        logging.info("Bot iniciado. Pressione 'q' na janela de visualização para sair.")
        while not self.stop_event.is_set():
            try:
                # Tenta pegar o frame processado mais recente para display
                frame_to_display, _, _, _, _, _ = self.processed_frame_queue.get(timeout=0.01) # Pequeno timeout
                cv2.imshow("Clash Royale Bot - Detecção e Decisão", frame_to_display)
            except Empty:
                pass # Nenhuma nova imagem para exibir
            except Exception as e:
                logging.error(f"Erro na visualização do OpenCV: {e}")

            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.stop_event.set()
            
            time.sleep(0.01) # Pequeno delay para não consumir CPU desnecessariamente

        self.stop_event.set() # Garante que todas as threads serão paradas
        capture_t.join(timeout=1.0) # Espera pelas threads terminarem
        vision_t.join(timeout=1.0)
        decision_action_t.join(timeout=1.0)
        
        cv2.destroyAllWindows()
        logging.info("Bot encerrado.")

def main():
    parser = argparse.ArgumentParser(description="Clash Royale AI Bot")
    parser.add_argument("--config", type=str, default="config.yaml", help="Caminho para o arquivo de configuração.")
    parser.add_argument("--dry-run", action="store_true", help="Executar o bot em modo de simulação (sem ações reais).")
    args = parser.parse_args()

    # 1. Carregar configurações
    try:
        with open(args.config, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"Arquivo de configuração não encontrado: {args.config}. Criando um de exemplo.")
        config = {
            "emulator": {
                "adb_path": "adb",
                "device_id": "localhost:5555",
                "resolution_width": 1920,
                "resolution_height": 1080,
                "adb_command_timeout": 10
            },
            "vision": {
                "model_type": "YOLOv8", 
                "yolov8_model_path": "vision/yolov8n.pt",
                "confidence_threshold": 0.5,
                "iou_threshold": 0.7
            },
            "ai": {
                "agent_type": "RuleBased", 
                "model_save_path": "./ai/models/dqn_model.pth",
                "training_mode": False,
                "offline_training_data_path": "./ai/training_data",
                "transition_log_path": "./ai/transitions.csv",
                "batch_size": 32,
                "replay_buffer_size": 1000,
                "epsilon_start": 1.0,
                "epsilon_decay": 0.995,
                "epsilon_min": 0.01,
                "gamma": 0.99,
                "target_update_freq": 10
            },
            "main_loop": {
                "capture_delay_sec": 0.05, # Delay entre capturas (aprox. 20 FPS)
                "vision_delay_sec": 0.05, # Delay entre processamentos de visão
                "decision_delay_sec": 0.05, # Delay entre decisões
                "log_performance": True,
                "log_file_path": "./logs/performance.log",
                "save_debug_screenshots": False, # Salvar screenshots de debug
                "debug_screenshots_path": "./debug_screenshots"
            }
        }
        with open(args.config, "w") as f:
            yaml.dump(config, f)
        logging.info("config.yaml de exemplo criado. Ajuste conforme sua configuração.")

    if config["main_loop"]["log_performance"]:
        setup_logging(config["main_loop"]["log_file_path"])
    else:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    logging.info("Inicializando o bot de Clash Royale...")

    # Baixar modelo YOLOv8 para teste se não existir
    if config["vision"]["model_type"] == "YOLOv8" and not os.path.exists(config["vision"]["yolov8_model_path"]):
        try:
            from ultralytics import YOLO
            model_name = os.path.basename(config["vision"]["yolov8_model_path"])
            # Tenta carregar o modelo. Se não existir localmente, ultralytics tenta baixar.
            YOLO(model_name) 
            # Garante que o modelo está no caminho especificado no config
            if not os.path.exists(config["vision"]["yolov8_model_path"]):
                # ultralytics baixa para o diretório de trabalho, movemos para o diretório vision/
                if os.path.exists(model_name):
                    os.makedirs(os.path.dirname(config["vision"]["yolov8_model_path"]), exist_ok=True)
                    os.rename(model_name, config["vision"]["yolov8_model_path"])
                    logging.info(f"Modelo {model_name} baixado e movido para {config["vision"]["yolov8_model_path"]}.")
                else:
                    logging.error(f"Modelo {model_name} não encontrado após tentativa de download. Por favor, baixe-o manualmente e coloque em {config["vision"]["yolov8_model_path"]}.")
            else:
                logging.info(f"Modelo {model_name} já existe em {config["vision"]["yolov8_model_path"]}.")
        except Exception as e:
            logging.error(f"Erro ao baixar/carregar YOLOv8: {e}. Verifique sua conexão ou baixe-o manualmente.")

    try:
        coordinator = BotCoordinator(config, dry_run=args.dry_run)
        coordinator.run()
    except RuntimeError as e:
        logging.critical(f"Erro crítico na inicialização do bot: {e}")

if __name__ == "__main__":
    main()

