
import time
import numpy as np

class GameState:
    def __init__(self):
        self.frame_id = 0 # Identificador único para cada frame processado
        self.timestamp = time.time() # Timestamp da última atualização do estado
        self._elixir = 0
        self._player_cards = []  # Lista de cartas disponíveis na mão com bbox e nome
        self._player_troops = []  # Lista de tropas do jogador no campo com bbox, nome, etc.
        self._enemy_troops = []   # Lista de tropas inimigas no campo com bbox, nome, etc.
        self._player_towers = {"king": {"hp": 0, "bbox": None}, "left_princess": {"hp": 0, "bbox": None}, "right_princess": {"hp": 0, "bbox": None}}
        self._enemy_towers = {"king": {"hp": 0, "bbox": None}, "left_princess": {"hp": 0, "bbox": None}, "right_princess": {"hp": 0, "bbox": None}}
        self._game_phase = "loading" # loading, menu, in_game, game_over
        self._last_action = None
        self._last_reward = 0

    def update_state(self, detected_objects, frame_id):
        self.frame_id = frame_id
        self.timestamp = time.time()
        
        # Resetar estados que são dinâmicos por frame
        self._player_cards = []
        self._player_troops = []
        self._enemy_troops = []
        # Não resetar HP das torres para manter o estado, a menos que uma detecção de HP seja implementada

        current_elixir_detected = False
        current_game_phase_detected = False

        for obj in detected_objects:
            name = obj["name"]
            bbox = obj["bbox"] # [x, y, w, h]

            if "elixir" in name: # Ex: "elixir_1", "elixir_2", ..., "elixir_10"
                try:
                    self._elixir = int(name.split("_")[1])
                    current_elixir_detected = True
                except (ValueError, IndexError):
                    pass 
            elif "card" in name: # Ex: "card_knight", "card_archers"
                self._player_cards.append({"name": name, "bbox": bbox})
            elif "player_troop" in name:
                self._player_troops.append({"name": name, "bbox": bbox})
            elif "enemy_troop" in name:
                self._enemy_troops.append({"name": name, "bbox": bbox})
            elif "player_king_tower" == name:
                self._player_towers["king"]["hp"] = self._player_towers["king"].get("hp", 100) # Manter HP se já existir
                self._player_towers["king"]["bbox"] = bbox
            elif "player_princess_tower_left" == name:
                self._player_towers["left_princess"]["hp"] = self._player_towers["left_princess"].get("hp", 100)
                self._player_towers["left_princess"]["bbox"] = bbox
            elif "player_princess_tower_right" == name:
                self._player_towers["right_princess"]["hp"] = self._player_towers["right_princess"].get("hp", 100)
                self._player_towers["right_princess"]["bbox"] = bbox
            elif "enemy_king_tower" == name:
                self._enemy_towers["king"]["hp"] = self._enemy_towers["king"].get("hp", 100)
                self._enemy_towers["king"]["bbox"] = bbox
            elif "enemy_princess_tower_left" == name:
                self._enemy_towers["left_princess"]["hp"] = self._enemy_towers["left_princess"].get("hp", 100)
                self._enemy_towers["left_princess"]["bbox"] = bbox
            elif "enemy_princess_tower_right" == name:
                self._enemy_towers["right_princess"]["hp"] = self._enemy_towers["right_princess"].get("hp", 100)
                self._enemy_towers["right_princess"]["bbox"] = bbox
            elif "battle_button" == name:
                self._game_phase = "menu"
                current_game_phase_detected = True
            elif "play_again_button" == name:
                self._game_phase = "game_over"
                current_game_phase_detected = True

        # Inferir fase do jogo se não foi explicitamente detectada
        if not current_game_phase_detected:
            if current_elixir_detected and (self._player_troops or self._enemy_troops):
                self._game_phase = "in_game"
            elif not current_elixir_detected and not self._player_troops and not self._enemy_troops:
                # Se não há elixir nem tropas, e não há botão de menu/game_over, pode ser loading ou game_over sem botão
                # Lógica mais robusta necessária para game_over
                self._game_phase = "loading"

    # Getters
    def get_elixir(self) -> int:
        return self._elixir

    def get_hand_cards(self) -> list:
        return list(self._player_cards) # Retorna uma cópia para evitar modificações externas

    def get_player_troops(self) -> list:
        return list(self._player_troops)

    def get_enemy_troops(self) -> list:
        return list(self._enemy_troops)

    def get_player_towers(self) -> dict:
        return {k: v.copy() for k, v in self._player_towers.items()} # Retorna cópia

    def get_enemy_towers(self) -> dict:
        return {k: v.copy() for k, v in self._enemy_towers.items()} # Retorna cópia

    def get_game_phase(self) -> str:
        return self._game_phase
    
    def get_last_reward(self) -> float:
        return self._last_reward

    def set_last_reward(self, reward: float):
        self._last_reward = reward

    def get_vector_representation(self):
        # Criar uma representação vetorial do estado para o agente de RL
        # Esta é uma implementação simplificada e precisa ser expandida
        vector = []
        vector.append(self._elixir)
        # Adicionar informações sobre cartas, tropas, torres, etc.
        # Normalizar os valores é crucial para o bom desempenho do agente
        # Ex: Posições das tropas normalizadas pela resolução da tela
        # Ex: Contagem de cada tipo de tropa
        return np.array(vector, dtype=np.float32)

    def __str__(self):
        return f"Frame ID: {self.frame_id}, Timestamp: {self.timestamp:.2f}, Elixir: {self._elixir}, " \
               f"Cards: {[c["name"] for c in self._player_cards]}, " \
               f"Player Troops: {len(self._player_troops)}, Enemy Troops: {len(self._enemy_troops)}, " \
               f"Phase: {self._game_phase}"

