
import cv2
import os
import time
import yaml
import logging
from emulator.adb_capture import AdbCapture
from vision.object_detection import ObjectDetector

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DatasetCollector:
    def __init__(self, config_path="config.yaml"):
        self.config = self._load_config(config_path)
        self.adb_capture = AdbCapture(adb_path=self.config["emulator"]["adb_path"],
                                      device_id=self.config["emulator"]["device_id"])
        self.object_detector = ObjectDetector(config_path=config_path) # Usar o detector para pré-anotação

        self.output_dir = self.config["dataset_collector"]["output_directory"]
        self.images_dir = os.path.join(self.output_dir, "images")
        self.labels_dir = os.path.join(self.output_dir, "labels")
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.labels_dir, exist_ok=True)

        self.auto_annotate = self.config["dataset_collector"].get("auto_annotate", False)
        self.annotation_format = self.config["dataset_collector"].get("annotation_format", "yolo")

        self.class_mapping = self.config["dataset_collector"].get("class_mapping", {})
        self.reverse_class_mapping = {v: k for k, v in self.class_mapping.items()}
        if not self.class_mapping:
            logging.warning("Nenhum mapeamento de classes encontrado em config.yaml. As classes serão salvas como detectadas.")

        logging.info(f"Coletor de Dataset inicializado. Saída em: {self.output_dir}")
        logging.info(f"Auto-anotação: {self.auto_annotate}, Formato: {self.annotation_format}")

    def _load_config(self, config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def _convert_bbox_to_yolo(self, bbox, img_width, img_height):
        # bbox: [x, y, w, h]
        x_center = (bbox[0] + bbox[2] / 2) / img_width
        y_center = (bbox[1] + bbox[3] / 2) / img_height
        width = bbox[2] / img_width
        height = bbox[3] / img_height
        return x_center, y_center, width, height

    def collect_data(self, num_screenshots=1, delay_sec=1):
        logging.info(f"Iniciando coleta de {num_screenshots} screenshots com delay de {delay_sec}s...")
        for i in range(num_screenshots):
            timestamp = int(time.time())
            image_filename = os.path.join(self.images_dir, f"screenshot_{timestamp}.png")
            label_filename = os.path.join(self.labels_dir, f"screenshot_{timestamp}.txt")

            screenshot = self.adb_capture.screencap()
            if screenshot is None:
                logging.error("Falha na captura de tela. Verifique a conexão ADB.")
                continue

            cv2.imwrite(image_filename, screenshot)
            logging.info(f"Screenshot salvo: {image_filename}")

            if self.auto_annotate:
                detected_objects = self.object_detector.detect_objects(screenshot)
                img_height, img_width, _ = screenshot.shape

                with open(label_filename, "w") as f:
                    for obj in detected_objects:
                        class_name = obj["name"]
                        # Mapear nome da classe para um ID numérico
                        class_id = self.class_mapping.get(class_name, -1) # -1 se não mapeado
                        if class_id == -1:
                            logging.warning(f"Classe '{class_name}' não encontrada no mapeamento. Ignorando anotação.")
                            continue

                        bbox = obj["bbox"]
                        if self.annotation_format == "yolo":
                            x_center, y_center, width, height = self._convert_bbox_to_yolo(bbox, img_width, img_height)
                            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
                        # Outros formatos de anotação (COCO, Pascal VOC) podem ser adicionados aqui
                logging.info(f"Anotações salvas para {image_filename} em {label_filename}")

            time.sleep(delay_sec)
        logging.info("Coleta de dados concluída.")

if __name__ == "__main__":
    # Exemplo de uso
    # Certifique-se de que config.yaml existe e está configurado
    if not os.path.exists("config.yaml"):
        sample_config = {
            "emulator": {
                "adb_path": "adb",
                "device_id": "localhost:5555"
            },
            "vision": {
                "detection_pipeline": [
                    {"type": "YOLOv8"}
                ],
                "yolov8_model_path": "vision/yolov8n.pt",
                "confidence_threshold": 0.5,
                "iou_threshold": 0.7
            },
            "dataset_collector": {
                "output_directory": "./dataset/clash_royale",
                "auto_annotate": True,
                "annotation_format": "yolo",
                "class_mapping": {
                    "card_knight": 0,
                    "card_archers": 1,
                    "elixir_bar": 2,
                    "player_king_tower": 3,
                    "enemy_king_tower": 4
                }
            }
        }
        os.makedirs("vision", exist_ok=True)
        os.makedirs("dataset/clash_royale", exist_ok=True)
        with open("config.yaml", "w") as f:
            yaml.dump(sample_config, f)
        logging.info("config.yaml de exemplo para dataset_collector criado.")
    
    collector = DatasetCollector()
    collector.collect_data(num_screenshots=5, delay_sec=2)

    logging.info("\nPara treinar um modelo YOLOv8 com os dados coletados:")
    logging.info("1. Crie um arquivo `data.yaml` no formato YOLO que aponte para seus diretórios de imagens e labels.")
    logging.info("2. Use o comando `yolo train model=yolov8n.pt data=data.yaml epochs=100` (ajuste conforme necessário).")

