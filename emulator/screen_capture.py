
import numpy as np
import cv2
import pygetwindow as gw
from PIL import ImageGrab

class ScreenCapture:
    def __init__(self, window_title="BlueStacks 5"):
        self.window_title = window_title
        self.window = None

    def find_bluestacks_window(self):
        try:
            self.window = gw.getWindowsWithTitle(self.window_title)[0]
            print(f"Janela '{self.window_title}' encontrada.")
            return True
        except IndexError:
            print(f"Janela '{self.window_title}' não encontrada. Certifique-se de que o BlueStacks está aberto.")
            self.window = None
            return False

    def capture_screenshot(self):
        if not self.window:
            if not self.find_bluestacks_window():
                return None

        # Ativar a janela para garantir que ela esteja em primeiro plano (pode ser necessário para algumas configurações)
        # self.window.activate()

        bbox = (self.window.left, self.window.top, self.window.right, self.window.bottom)
        screenshot = ImageGrab.grab(bbox)
        screenshot_np = np.array(screenshot)
        # Converter de RGB para BGR para OpenCV
        frame = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        return frame

if __name__ == "__main__":
    # Exemplo de uso:
    capture = ScreenCapture()
    if capture.find_bluestacks_window():
        print("Capturando tela do BlueStacks... Pressione 'q' para sair.")
        while True:
            frame = capture.capture_screenshot()
            if frame is not None:
                cv2.imshow("BlueStacks Screen", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("Não foi possível capturar a tela. Verifique se o BlueStacks está aberto e com o título correto.")
                break
        cv2.destroyAllWindows()
    else:
        print("Não foi possível iniciar a captura de tela.")

