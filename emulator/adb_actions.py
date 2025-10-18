
import subprocess
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AdbActions:
    def __init__(self, adb_path="adb", device_id=None, screen_resolution=(1920, 1080), game_resolution=(1920, 1080), dry_run=False, tap_delay_ms=100, timeout=5):
        self.adb_path = adb_path
        self.device_id = device_id
        self.screen_width, self.screen_height = screen_resolution
        self.game_width, self.game_height = game_resolution
        self.dry_run = dry_run
        self.tap_delay_ms = tap_delay_ms
        self.timeout = timeout

    def _execute_adb_command(self, command, retries=2):
        if self.dry_run:
            logging.info(f"[DRYRUN] Comando ADB: {" ".join(command)}")
            return True

        cmd = [self.adb_path] + ([ "-s", self.device_id ] if self.device_id else []) + command
        for i in range(retries):
            try:
                subprocess.run(cmd, check=True, timeout=self.timeout, capture_output=True)
                return True
            except subprocess.TimeoutExpired:
                logging.warning(f"Comando ADB timeout (tentativa {i+1}/{retries}): {" ".join(cmd)}")
            except subprocess.CalledProcessError as e:
                logging.warning(f"Erro ADB (tentativa {i+1}/{retries}): {e.stderr.decode().strip()} - Comando: {" ".join(cmd)}")
            except FileNotFoundError:
                logging.error(f"ADB não encontrado em \'{self.adb_path}\'. Certifique-se de que está instalado e no PATH.")
                return False
            time.sleep(0.1) # Pequeno delay entre retries
        logging.error(f"Falha ao executar comando ADB após {retries} tentativas: {" ".join(cmd)}")
        return False

    def to_screen_coords(self, game_x, game_y):
        """Converte coordenadas lógicas do jogo para coordenadas de tela reais."""
        if self.game_width == 0 or self.game_height == 0:
            logging.warning("Resolução lógica do jogo não definida ou zero. Usando proporção 1:1.")
            scale_x = 1
            scale_y = 1
        else:
            scale_x = self.screen_width / self.game_width
            scale_y = self.screen_height / self.game_height

        screen_x = int(game_x * scale_x)
        screen_y = int(game_y * scale_y)
        return screen_x, screen_y

    def tap(self, game_x, game_y):
        """Simula um toque na tela nas coordenadas lógicas do jogo (game_x, game_y)."""
        screen_x, screen_y = self.to_screen_coords(game_x, game_y)
        logging.info(f"ADB: Tocando em coordenadas de jogo ({game_x}, {game_y}) -> tela ({screen_x}, {screen_y})")
        success = self._execute_adb_command(["shell", "input", "tap", str(screen_x), str(screen_y)])
        if success:
            time.sleep(self.tap_delay_ms / 1000.0) # Converter ms para segundos
        return success

    def swipe(self, game_x1, game_y1, game_x2, game_y2, duration_ms=200):
        """Simula um arrastar na tela de coordenadas lógicas do jogo.
        duration_ms: duração do swipe em milissegundos."""
        screen_x1, screen_y1 = self.to_screen_coords(game_x1, game_y1)
        screen_x2, screen_y2 = self.to_screen_coords(game_x2, game_y2)
        logging.info(f"ADB: Arrastando de jogo ({game_x1}, {game_y1}) para ({game_x2}, {game_y2}) -> tela ({screen_x1}, {screen_y1}) para ({screen_x2}, {screen_y2}) com duração {duration_ms}ms")
        success = self._execute_adb_command(["shell", "input", "swipe", str(screen_x1), str(screen_y1), str(screen_x2), str(screen_y2), str(duration_ms)])
        if success:
            time.sleep(self.tap_delay_ms / 1000.0) # Pequena pausa após o swipe
        return success

    def play_card(self, card_game_coords, target_game_coords):
        """Simula o ato de jogar uma carta do deck para o campo de batalha via swipe."""
        logging.info(f"ADB: Jogando carta de jogo {card_game_coords} para {target_game_coords}")
        # A duração do swipe pode ser ajustada para simular um movimento mais natural
        return self.swipe(card_game_coords[0], card_game_coords[1], target_game_coords[0], target_game_coords[1], duration_ms=250)


if __name__ == "__main__":
    # Exemplo de uso:
    # Certifique-se de que um dispositivo BlueStacks (ou outro emulador/dispositivo Android) esteja conectado via ADB.
    # Use `adb devices` para listar os dispositivos e obter o device_id.
    
    # Simular uma resolução de tela e jogo para teste
    test_screen_res = (1920, 1080) # Resolução do monitor onde o BlueStacks está rodando
    test_game_res = (1920, 1080) # Resolução lógica interna do jogo no BlueStacks

    adb_actions = AdbActions(screen_resolution=test_screen_res, game_resolution=test_game_res, dry_run=True)
    logging.info("Testando ações ADB em modo DRY RUN. Nenhuma ação será executada no dispositivo.")
    
    # Tente tocar no centro da tela (assumindo 1920x1080)
    adb_actions.tap(960, 540)
    
    # Tente arrastar do canto inferior esquerdo para o centro
    adb_actions.swipe(100, 900, 960, 540, duration_ms=500)
    
    logging.info("Testes DRY RUN concluídos. Para testar ações reais, defina dry_run=False.")
    
    # Exemplo de uso real (descomente para testar)
    # adb_actions_real = AdbActions(device_id="emulator-5554", screen_resolution=(1920, 1080), game_resolution=(1920, 1080), dry_run=False)
    # adb_actions_real.tap(960, 540)

