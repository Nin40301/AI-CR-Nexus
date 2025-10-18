
import cv2
import numpy as np
import os
import yaml
import logging
from ultralytics import YOLO
import pytesseract
from PIL import Image

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ObjectDetector:
    def __init__(self, config_path="config.yaml"):
        self.config = self._load_config(config_path)
        self.detection_pipeline = self.config["vision"]["detection_pipeline"]
        self.confidence_threshold = self.config["vision"]["confidence_threshold"]
        self.iou_threshold = self.config["vision"]["iou_threshold"]
        self.models = {}

        for model_config in self.detection_pipeline:
            model_type = model_config["type"]
            if model_type == "YOLOv8":
                try:
                    model_path = model_config.get("yolov8_model_path", self.config["vision"]["yolov8_model_path"])
                    self.models["YOLOv8"] = YOLO(model_path)
                    logging.info(f"Modelo YOLOv8 carregado: {model_path}")
                except Exception as e:
                    logging.error(f"Erro ao carregar modelo YOLOv8: {e}. Verifique o caminho e o arquivo do modelo.")
                    raise
            elif model_type == "OCR":
                self.models["OCR"] = True # Apenas um marcador, OCR é chamado diretamente
                self.ocr_rois = model_config.get("ocr_rois", {}) # ROIs específicas para OCR
                logging.info("Detector configurado para OCR (pytesseract).")
            elif model_type == "TemplateMatching":
                self.templates_dir = model_config.get("templates_dir", "templates/clash_royale")
                self.models["TemplateMatching"] = self._load_templates(self.templates_dir)
                logging.info("Detector de objetos configurado para Template Matching.")
            else:
                logging.warning(f"Tipo de modelo \'{model_type}\' não suportado na pipeline. Ignorando.")

    def _load_config(self, config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def _load_templates(self, templates_dir):
        templates = {}
        if not os.path.exists(templates_dir):
            logging.warning(f"Diretório de templates não encontrado: {templates_dir}")
            return templates
        for filename in os.listdir(templates_dir):
            if filename.endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(templates_dir, filename)
                template = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if template is not None:
                    if template.shape[2] == 4:
                        b, g, r, a = cv2.split(template)
                        rgb = cv2.merge([b, g, r])
                        templates[filename] = {"image": rgb, "mask": a}
                    else:
                        templates[filename] = {"image": template, "mask": None}
                else:
                    logging.warning(f"Erro ao carregar o template: {path}")
        return templates

    def _run_yolov8_detection(self, image):
        detections = []
        if "YOLOv8" in self.models:
            results = self.models["YOLOv8"](image, conf=self.confidence_threshold, iou=self.iou_threshold, verbose=False)
            for r in results:
                for *xyxy, conf, cls in r.boxes.data:
                    x1, y1, x2, y2 = map(int, xyxy)
                    label = self.models["YOLOv8"].names[int(cls)]
                    detections.append({
                        "name": label,
                        "confidence": float(conf),
                        "bbox": [x1, y1, x2 - x1, y2 - y1]
                    })
        return detections

    def _run_ocr_detection(self, image):
        detections = []
        if "OCR" in self.models:
            for roi_name, roi_coords in self.ocr_rois.items():
                x, y, w, h = roi_coords
                roi_image = image[y:y+h, x:x+w]
                if roi_image.size == 0: # Evitar ROIs vazias
                    continue

                # Pré-processamento específico para OCR de elixir
                if "elixir" in roi_name.lower():
                    gray_roi = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
                    # Aplicar um threshold para isolar os números do elixir
                    _, thresh_roi = cv2.threshold(gray_roi, 180, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                    # Aumentar o contraste ou dilatar para melhorar a leitura
                    kernel = np.ones((1,1),np.uint8)
                    thresh_roi = cv2.dilate(thresh_roi, kernel, iterations=1)
                    thresh_roi = cv2.erode(thresh_roi, kernel, iterations=1)
                    
                    elixir_text = pytesseract.image_to_string(Image.fromarray(thresh_roi), config='--psm 7 outputbase digits').strip()
                    try:
                        elixir_value = int(elixir_text) if elixir_text.isdigit() else 0
                        if 0 <= elixir_value <= 10: # Elixir vai de 0 a 10
                            detections.append({"name": f"elixir_{elixir_value}", "confidence": 1.0, "bbox": [x, y, w, h]})
                    except ValueError:
                        logging.debug(f"OCR não conseguiu ler elixir na ROI {roi_name}: {elixir_text}")
                else:
                    # OCR genérico para outras ROIs
                    text = pytesseract.image_to_string(Image.fromarray(roi_image)).strip()
                    if text:
                        detections.append({"name": f"ocr_{roi_name}_{text}", "confidence": 0.9, "bbox": [x, y, w, h]})
        return detections

    def _run_template_matching_detection(self, image):
        detections = []
        if "TemplateMatching" in self.models and self.models["TemplateMatching"]:
            templates = self.models["TemplateMatching"]
            for name, template_data in templates.items():
                template_image = template_data["image"]
                template_mask = template_data["mask"]

                if template_image.shape[0] > image.shape[0] or template_image.shape[1] > image.shape[1]:
                    continue

                if template_mask is not None:
                    result = cv2.matchTemplate(image, template_image, cv2.TM_CCOEFF_NORMED, mask=template_mask)
                else:
                    result = cv2.matchTemplate(image, template_image, cv2.TM_CCOEFF_NORMED)

                loc = np.where(result >= self.confidence_threshold)
                for pt in zip(*loc[::-1]):
                    overlap = False
                    for existing_detection in detections:
                        ex, ey, ew, eh = existing_detection["bbox"]
                        x, y = pt
                        w, h = template_image.shape[1], template_image.shape[0]

                        intersection_x = max(ex, x)
                        intersection_y = max(ey, y)
                        intersection_w = min(ex + ew, x + w) - intersection_x
                        intersection_h = min(ey + eh, y + h) - intersection_y

                        if intersection_w > 0 and intersection_h > 0:
                            overlap = True
                            break
                    
                    if not overlap:
                        detections.append({
                            "name": name.replace(".png", ""),
                            "confidence": float(result[pt[1], pt[0]]),
                            "bbox": [pt[0], pt[1], template_image.shape[1], template_image.shape[0]]
                        })
        return detections

    def detect_objects(self, screenshot):
        all_detections = []
        
        for model_config in self.detection_pipeline:
            model_type = model_config["type"]
            current_detections = []

            if model_type == "YOLOv8":
                current_detections = self._run_yolov8_detection(screenshot)
            elif model_type == "OCR":
                current_detections = self._run_ocr_detection(screenshot)
            elif model_type == "TemplateMatching":
                current_detections = self._run_template_matching_detection(screenshot)
            
            if current_detections:
                all_detections.extend(current_detections)
                # Se a configuração permitir, podemos parar após a primeira detecção bem-sucedida
                if model_config.get("stop_on_success", False):
                    logging.debug(f"Detecções encontradas com {model_type}. Parando pipeline de detecção.")
                    break
        
        # Aplicar NMS (Non-Maximum Suppression) se houver sobreposição entre diferentes tipos de detectores
        # Isso pode ser complexo e pode ser feito de forma mais simples se os detectores forem para classes distintas
        # Por enquanto, apenas retorna todas as detecções.

        return all_detections

if __name__ == "__main__":
    # Exemplo de uso com pipeline de detecção
    # Criar um config.yaml de exemplo se não existir
    if not os.path.exists("config.yaml"):
        sample_config = {
            "vision": {
                "detection_pipeline": [
                    {"type": "YOLOv8", "stop_on_success": True}, # Tenta YOLOv8 primeiro
                    {"type": "OCR", "ocr_rois": {"elixir_bar": [700, 1000, 500, 80]}}, # Depois OCR
                    {"type": "TemplateMatching", "templates_dir": "templates/clash_royale"} # Por último Template Matching
                ],
                "yolov8_model_path": "vision/yolov8n.pt",
                "confidence_threshold": 0.5,
                "iou_threshold": 0.7
            }
        }
        os.makedirs("vision", exist_ok=True)
        os.makedirs("templates/clash_royale", exist_ok=True)
        with open("config.yaml", "w") as f:
            yaml.dump(sample_config, f)
        logging.info("config.yaml de exemplo criado. Baixe yolov8n.pt e coloque-o em vision/.")
        try:
            from ultralytics import YOLO
            YOLO("yolov8n.pt").export(format="torchscript", filename="vision/yolov8n.pt") # Garante que o modelo é salvo localmente
            logging.info("Modelo yolov8n.pt baixado com sucesso para vision/.")
        except Exception as e:
            logging.error(f"Erro ao baixar yolov8n.pt: {e}. Por favor, baixe-o manualmente e coloque em vision/.")

        # Criar um template de exemplo para TemplateMatching
        dummy_template = np.zeros((50, 50, 3), dtype=np.uint8)
        cv2.putText(dummy_template, "Card", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.imwrite("templates/clash_royale/dummy_card.png", dummy_template)
        logging.info("Template de exemplo 'dummy_card.png' criado em templates/clash_royale/.")

    detector = ObjectDetector()

    # Criar uma imagem de teste (preta com um retângulo branco e texto)
    test_screenshot = np.zeros((1080, 1920, 3), dtype=np.uint8)
    cv2.rectangle(test_screenshot, (500, 300), (800, 600), (255, 255, 255), -1)
    cv2.putText(test_screenshot, "Test Object", (500, 290), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(test_screenshot, "10", (750, 1050), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3) # Simular elixir
    cv2.rectangle(test_screenshot, (100, 850), (200, 950), (0, 0, 255), -1) # Simular uma carta para template matching
    
    # Salvar para visualização
    cv2.imwrite("test_screenshot.png", test_screenshot)

    logging.info(f"Detectando objetos na imagem de teste com pipeline configurado...")
    detected_objects = detector.detect_objects(test_screenshot)

    if detected_objects:
        logging.info("Objetos detectados:")
        for obj in detected_objects:
            logging.info(f"  Nome: {obj["name"]}, Confiança: {obj["confidence"]:.2f}, Bounding Box: {obj["bbox"]}")
            x, y, w, h = obj["bbox"]
            cv2.rectangle(test_screenshot, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(test_screenshot, obj["name"], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow("Detections", test_screenshot)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        logging.info("Nenhum objeto detectado.")

    logging.info("\nPara usar este módulo efetivamente:")
    logging.info("1. Configure a `detection_pipeline` em `config.yaml` com a ordem desejada dos detectores (YOLOv8, OCR, TemplateMatching).")
    logging.info("2. Para YOLOv8, treine um modelo com um dataset de imagens do Clash Royale e atualize `yolov8_model_path`.")
    logging.info("3. Para OCR, ajuste as `ocr_rois` em `config.yaml` para as regiões de interesse do texto (ex: elixir, nomes de cartas).")
    logging.info("4. Para Template Matching, coloque imagens PNG/JPG dos elementos que deseja detectar no diretório especificado por `templates_dir`.")

