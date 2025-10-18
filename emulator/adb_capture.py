
import subprocess
import numpy as np
import cv2
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AdbCapture:
    def __init__(self, adb_path="adb", device_id=None, timeout=5):
        self.adb_path = adb_path
        self.device_id = device_id
        self.timeout = timeout
        self.resolution = None # (width, height)

    def _execute_adb_command(self, command, check=True, text=True):
        cmd = [self.adb_path] + ([ "-s", self.device_id ] if self.device_id else []) + command
        try:
            result = subprocess.run(cmd, capture_output=True, text=text, check=check, timeout=self.timeout)
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            logging.error(f"Comando ADB timeout: {' '.join(cmd)}")
            raise RuntimeError("ADB command timeout")
        except subprocess.CalledProcessError as e:
            logging.error(f"Erro ao executar comando ADB: {' '.join(cmd)}\nStderr: {e.stderr}")
            raise RuntimeError(f"ADB error: {e.stderr}")
        except FileNotFoundError:
            logging.error(f"ADB não encontrado em \'{self.adb_path}\'. Certifique-se de que está instalado e no PATH.")
            raise RuntimeError("ADB not found")
        except Exception as e:
            logging.error(f"Erro inesperado ao executar comando ADB: {e}")
            raise RuntimeError(f"Unexpected ADB error: {e}")

    def get_device_resolution(self):
        if self.resolution:
            return self.resolution
        
        try:
            output = self._execute_adb_command(["shell", "wm", "size"])
            match = re.search(r'Physical size: (\d+)x(\d+)', output)
            if match:
                width = int(match.group(1))
                height = int(match.group(2))
                self.resolution = (width, height)
                logging.info(f"Resolução do dispositivo ADB detectada: {width}x{height}")
                return self.resolution
            else:
                logging.warning("Não foi possível detectar a resolução do dispositivo ADB. Formato inesperado.")
        except RuntimeError as e:
            logging.error(f"Falha ao obter resolução do dispositivo: {e}")
        return None

    def screencap(self):
        cmd = [self.adb_path] + ([ "-s", self.device_id ] if self.device_id else []) + ["exec-out", "screencap", "-p"]
        try:
            # Usar subprocess.run para capturar a saída binária diretamente
            p = subprocess.run(cmd, capture_output=True, timeout=self.timeout, check=True)
            data = p.stdout

            # ADB screencap emite um cabeçalho \r\n em alguns sistemas (Windows), precisa ser removido
            if data.startswith(b'\r\n'):
                data = data[2:]

            img = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                logging.error("cv2.imdecode retornou None. Imagem corrompida ou formato inválido.")
                return None
            return img  # BGR OpenCV
        except subprocess.TimeoutExpired:
            logging.error("ADB screencap timeout.")
            return None
        except subprocess.CalledProcessError as e:
            logging.error(f"Erro ao capturar tela via ADB: {e.stderr.decode()}")
            return None
        except Exception as e:
            logging.error(f"Erro inesperado durante a captura de tela ADB: {e}")
            return None

if __name__ == "__main__":
    # Exemplo de uso:
    # Certifique-se de que um dispositivo BlueStacks (ou outro emulador/dispositivo Android) esteja conectado via ADB.
    # Use `adb devices` para listar os dispositivos e obter o device_id.
    # Ex: adb_capture = AdbCapture(device_id="emulator-5554")
    
    adb_capture = AdbCapture()
    logging.info("Tentando capturar tela via ADB... Pressione 'q' para sair.")
    
    try:
        resolution = adb_capture.get_device_resolution()
        if not resolution:
            logging.error("Não foi possível obter a resolução do dispositivo. Verifique a conexão ADB.")
        
        while True:
            frame = adb_capture.screencap()
            if frame is not None:
                cv2.imshow("ADB Screen", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                logging.warning("Não foi possível capturar a tela. Tentando novamente...")
                time.sleep(1) # Espera antes de tentar novamente
        cv2.destroyAllWindows()
        logging.info("Captura ADB encerrada.")
    except RuntimeError as e:
        logging.error(f"Erro crítico: {e}")



