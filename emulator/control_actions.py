
import pyautogui
import time
import cv2
import numpy as np

class ActionController:
    def __init__(self):
        pyautogui.FAILSAFE = True # Ativa o failsafe para mover o mouse para o canto superior esquerdo para parar
        self.bluestacks_game_area = None # (left, top, width, height) da área de jogo dentro do BlueStacks

    def set_bluestacks_game_area(self, bluestacks_window_rect):
        # Esta função deve ser chamada após a detecção da janela do BlueStacks.
        # Assume que o Clash Royale ocupa uma área específica dentro da janela do BlueStacks.
        # Estas são coordenadas aproximadas para BlueStacks 5 com Clash Royale em tela cheia na proporção 16:9.
        # Pode ser necessário ajustar com base na resolução do monitor e configurações do BlueStacks.
        
        # Exemplo: Se a janela do BlueStacks for 1920x1080 (largura x altura)
        # e o jogo ocupa uma área centralizada ou com barras laterais/superiores.
        
        # Para uma janela típica do BlueStacks, a área de jogo pode ser um pouco menor.
        # Uma abordagem mais robusta envolveria a detecção de elementos da UI do jogo
        # para determinar a área exata.
        
        # Placeholder: vamos assumir que a área de jogo é a maior parte da janela,
        # ajustando ligeiramente para compensar bordas ou barras de título.
        
        # Ajuste manual para uma janela de 1920x1080 (exemplo)
        # bluestacks_window_rect = (left, top, right, bottom)
        window_width = bluestacks_window_rect.right - bluestacks_window_rect.left
        window_height = bluestacks_window_rect.bottom - bluestacks_window_rect.top

        # Estes valores são heurísticos e podem precisar de ajuste fino.
        # Por exemplo, se a janela do BlueStacks tem uma barra de título de ~30px e bordas de ~5px.
        # E o jogo tem uma proporção específica que não preenche a janela completamente.

        # Para BlueStacks 5, a área de jogo geralmente preenche a maior parte da janela.
        # Vamos definir uma área de jogo relativa ao tamanho da janela detectada.
        # Assumindo uma proporção 9:16 (vertical) para Clash Royale em um emulador horizontal
        # ou 16:9 (horizontal) se o emulador estiver configurado para paisagem.
        
        # Considerando que o Clash Royale é um jogo vertical, mas o BlueStacks pode estar em modo paisagem.
        # Precisamos de uma forma de identificar a área de jogo vertical dentro da janela horizontal.
        
        # Uma abordagem mais prática é definir uma proporção esperada para a área de jogo
        # e centralizá-la ou alinhá-la.
        
        # Por simplicidade, vamos assumir que a área de jogo é a janela inteira por agora,
        # e o usuário deve garantir que o Clash Royale esteja maximizado dentro do BlueStacks.
        self.bluestacks_game_area = {
            "left": bluestacks_window_rect.left,
            "top": bluestacks_window_rect.top,
            "width": window_width,
            "height": window_height
        }
        print(f"Área de jogo do BlueStacks definida para: {self.bluestacks_game_area}")

    def game_coords_to_screen_coords(self, game_x, game_y, game_width=1920, game_height=1080):
        """Converte coordenadas lógicas do jogo (ex: 0-1920, 0-1080) para coordenadas de tela.
        game_width e game_height devem corresponder à resolução lógica do jogo Clash Royale.
        """
        if not self.bluestacks_game_area:
            raise ValueError("A área de jogo do BlueStacks não foi definida. Chame set_bluestacks_game_area primeiro.")

        scale_x = self.bluestacks_game_area["width"] / game_width
        scale_y = self.bluestacks_game_area["height"] / game_height

        screen_x = int(self.bluestacks_game_area["left"] + game_x * scale_x)
        screen_y = int(self.bluestacks_game_area["top"] + game_y * scale_y)
        return screen_x, screen_y

    def click(self, game_x, game_y, duration=0.1):
        """Simula um clique do mouse nas coordenadas lógicas do jogo (game_x, game_y)."""
        screen_x, screen_y = self.game_coords_to_screen_coords(game_x, game_y)
        print(f"Simulando clique em coordenadas de jogo: ({game_x}, {game_y}) -> tela: ({screen_x}, {screen_y})")
        pyautogui.moveTo(screen_x, screen_y, duration=duration)
        pyautogui.click(screen_x, screen_y)
        time.sleep(0.5) # Pequena pausa para a ação ser registrada pelo jogo

    def drag_and_drop(self, game_start_x, game_start_y, game_end_x, game_end_y, duration=0.5):
        """Simula um arrastar e soltar do mouse de coordenadas lógicas do jogo.
        de (game_start_x, game_start_y) para (game_end_x, game_end_y)."""
        screen_start_x, screen_start_y = self.game_coords_to_screen_coords(game_start_x, game_start_y)
        screen_end_x, screen_end_y = self.game_coords_to_screen_coords(game_end_x, game_end_y)
        print(f"Simulando arrastar de jogo: ({game_start_x}, {game_start_y}) para ({game_end_x}, {game_end_y}) -> tela: ({screen_start_x}, {screen_start_y}) para ({screen_end_x}, {screen_end_y})")
        pyautogui.moveTo(screen_start_x, screen_start_y, duration=duration)
        pyautogui.dragTo(screen_end_x, screen_end_y, duration=duration)
        time.sleep(0.5) # Pequena pausa para a ação ser registrada pelo jogo

    def play_card(self, card_game_coords, target_game_coords):
        """Simula o ato de jogar uma carta do deck para o campo de batalha.
        card_game_coords: (x, y) lógicas da carta na mão.
        target_game_coords: (x, y) lógicas do local onde jogar no campo."""
        print(f"Jogando carta de jogo {card_game_coords} para {target_game_coords}")
        self.drag_and_drop(card_game_coords[0], card_game_coords[1], target_game_coords[0], target_game_coords[1])


