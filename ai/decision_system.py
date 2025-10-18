
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import os
import logging
import csv
import time # Adicionado para delays realistas

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Interface Base para Agentes --- 
class Agent:
    def __init__(self, config, action_map):
        self.config = config
        self.action_map = action_map
        self.transition_log_path = self.config["ai"].get("transition_log_path", "./ai/transitions.csv")
        self._init_transition_log()

    def _init_transition_log(self):
        os.makedirs(os.path.dirname(self.transition_log_path), exist_ok=True)
        if not os.path.exists(self.transition_log_path):
            with open(self.transition_log_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "frame_id", "state", "action", "reward", "next_state", "done"])

    def record_transition(self, timestamp, frame_id, state, action, reward, next_state, done):
        with open(self.transition_log_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, frame_id, state.tolist(), action, reward, next_state.tolist(), done])

    def select_action(self, game_state, current_frame_id):
        raise NotImplementedError

    def learn(self, state, action, reward, next_state, done):
        pass # Opcional, para agentes que aprendem online


# --- Agente Baseado em Regras --- 
class RuleBasedAgent(Agent):
    def __init__(self, config, action_map):
        super().__init__(config, action_map)
        logging.info("Agente RuleBased inicializado.")

    def select_action(self, game_state, current_frame_id):
        # Lógica de regras fixas com prioridade

        # 1. Ações de Menu/Fim de Jogo (Alta Prioridade)
        if game_state.get_game_phase() == "menu":
            logging.info("Decisão (RuleBased): Clicar no botão de batalha.")
            return {"action": "click", "target": "battle_button", "coords": (960, 850), "delay_after": 1.0}
        elif game_state.get_game_phase() == "game_over":
            logging.info("Decisão (RuleBased): Jogo terminou, esperar por nova partida ou retornar ao menu.")
            # Poderíamos adicionar lógica para clicar em 'Play Again' ou 'Home'
            return {"action": "wait", "delay_after": 2.0}

        # 2. Ações em Jogo (Média Prioridade)
        if game_state.get_game_phase() == "in_game":
            # Lógica para jogar cartas
            if game_state.get_elixir() >= 4 and game_state.get_hand_cards():
                # Exemplo: Priorizar jogar uma carta específica ou em uma posição estratégica
                # Por enquanto, pega a primeira carta disponível e joga em uma posição padrão
                card_to_play = game_state.get_hand_cards()[0]
                play_position = (960, 700) # Posição padrão no meio inferior
                logging.info(f"Decisão (RuleBased): Jogar carta {card_to_play["name"]} em {play_position}.")
                return {"action": "play_card", "card_name": card_to_play["name"], "coords": play_position, "delay_after": 0.5}
            
            # Se não pode jogar carta, esperar
            logging.info("Decisão (RuleBased): Esperar (elixir baixo ou sem cartas).")
            return {"action": "wait", "delay_after": 0.1}

        # 3. Default: Esperar (Baixa Prioridade)
        return {"action": "wait", "delay_after": 0.1}


# --- Placeholder para o Ambiente de RL --- 
class RLEnvironment:
    def __init__(self, game_state_instance, config):
        self.game_state = game_state_instance
        self.config = config
        
        # Definir espaço de observação e ação
        # Exemplo: Observação pode ser um vetor do estado do jogo
        # O tamanho real dependerá da representação vetorial do GameState
        self.observation_space_size = 2 # Exemplo: [elixir, tem_carta_na_mao]
        # Ações: 0: Esperar, 1: Clicar Botão Batalha, 2: Jogar Carta 1 Pos A
        self.action_space_size = 3 

    def get_observation(self):
        elixir = self.game_state.get_elixir() / 10.0 
        has_card = 1.0 if self.game_state.get_hand_cards() else 0.0
        return np.array([elixir, has_card], dtype=np.float32)

    def get_reward(self, action):
        # Recompensa simplificada para o placeholder
        reward = 0
        if action == 2 and self.game_state.get_hand_cards() and self.game_state.get_elixir() >= 4: 
            reward += 0.1 
        if action == 0 and self.game_state.get_elixir() == 10 and self.game_state.get_hand_cards():
            reward -= 0.05
        return reward

    def is_done(self):
        return self.game_state.get_game_phase() == "game_over"

    def reset(self):
        # Resetar o ambiente para um novo episódio (simulação)
        self.game_state._elixir = random.randint(0, 10)
        self.game_state._player_cards = []
        if random.random() < 0.7: 
            self.game_state._player_cards = [{
                "name": "card_random",
                "bbox": [0,0,0,0]
            }]
        self.game_state._game_phase = "in_game"
        self.game_state._last_reward = 0
        self.game_state._enemy_towers = {"king": {"hp": 100, "bbox": None}}
        self.game_state._player_towers = {"king": {"hp": 100, "bbox": None}}
        self.game_state.frame_id = 0
        return self.get_observation()

    def step(self, action):
        # Simular a transição de estado após uma ação
        # Isso é onde a lógica do jogo real seria simulada
        reward = self.get_reward(action)
        self.game_state.set_last_reward(reward)

        # Simular mudança de estado
        self.game_state._elixir = random.randint(0, 10)
        if random.random() < 0.7: 
            self.game_state._player_cards = [{
                "name": "card_random",
                "bbox": [0,0,0,0]
            }]
        else:
            self.game_state._player_cards = []
        
        if random.random() < 0.01: # 1% de chance de game over
            self.game_state._game_phase = "game_over"
        else:
            self.game_state._game_phase = "in_game"

        done = self.is_done()
        next_state = self.get_observation()
        return next_state, reward, done, {}


# --- Rede Neural do DQN --- 
class DQN(nn.Module):
    def __init__(self, observation_space_size, action_space_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(observation_space_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_space_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)


# --- Agente de Reinforcement Learning (DQN) --- 
class DQN_Agent(Agent):
    def __init__(self, config, action_map, game_state_instance):
        super().__init__(config, action_map)
        self.env = RLEnvironment(game_state_instance, config) # Passar config para o ambiente
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.policy_net = DQN(self.env.observation_space_size, self.env.action_space_size).to(self.device)
        self.target_net = DQN(self.env.observation_space_size, self.env.action_space_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=0.001)
        self.memory = deque(maxlen=config["ai"].get("replay_buffer_size", 10000)) # Replay Buffer

        self.epsilon = config["ai"].get("epsilon_start", 1.0) # Para exploração vs explotação
        self.epsilon_decay = config["ai"].get("epsilon_decay", 0.995)
        self.epsilon_min = config["ai"].get("epsilon_min", 0.01)
        self.gamma = config["ai"].get("gamma", 0.99) # Fator de desconto
        self.batch_size = config["ai"].get("batch_size", 32)
        self.target_update_freq = config["ai"].get("target_update_freq", 10)
        self.learn_step_counter = 0

        self._load_model()
        logging.info("Agente DQN inicializado.")

    def _load_model(self):
        model_path = self.config["ai"]["model_save_path"]
        if os.path.exists(model_path):
            logging.info(f"Carregando modelo do agente DQN de: {model_path}")
            self.policy_net.load_state_dict(torch.load(model_path, map_location=self.device))
            self.target_net.load_state_dict(self.policy_net.state_dict())
            self.target_net.eval()
        else:
            logging.warning("Nenhum modelo DQN encontrado. Iniciando com modelo aleatório.")

    def save_model(self):
        model_path = self.config["ai"]["model_save_path"]
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        torch.save(self.policy_net.state_dict(), model_path)
        logging.info(f"Modelo do agente DQN salvo em: {model_path}")

    def select_action(self, game_state, current_frame_id):
        state_observation = self.env.get_observation()
        if self.config["ai"]["training_mode"] and random.random() < self.epsilon:
            action_index = random.randrange(self.env.action_space_size) # Exploração
        else:
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state_observation).unsqueeze(0).to(self.device)
                action_index = self.policy_net(state_tensor).argmax(1).item() # Explotação
        
        decision = self.action_map.get(action_index, {"action": "wait"})
        decision["action_index"] = action_index # Adiciona o action_index para uso no learn
        logging.info(f"Decisão (DQN): {decision}")
        return decision

    def learn(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        if len(self.memory) < self.batch_size:
            return

        self.optimize_model()
        self.learn_step_counter += 1
        if self.learn_step_counter % self.target_update_freq == 0:
            self.update_target_network()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def optimize_model(self):
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.FloatTensor(np.array(states)).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(np.array(next_states)).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        current_q_values = self.policy_net(states).gather(1, actions)
        next_q_values = self.target_net(next_states).max(1)[0].detach()
        expected_q_values = rewards + (self.gamma * next_q_values * (1 - dones))

        loss = nn.functional.mse_loss(current_q_values, expected_q_values.unsqueeze(1))
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def update_target_network(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())


# --- Sistema de Decisão Principal --- 
class DecisionSystem:
    def __init__(self, game_state_instance, config):
        self.config = config
        self.game_state = game_state_instance

        # Mapeamento de ações do agente para ações do jogo
        # As coordenadas são lógicas do jogo (ex: 1920x1080)
        self.action_map = {
            0: {"action": "wait", "delay_after": 0.1},
            1: {"action": "click", "target": "battle_button", "coords": (960, 850), "delay_after": 1.0}, 
            2: {"action": "play_card", "card_index": 0, "coords": (960, 700), "delay_after": 0.5}, # Jogar 1ª carta disponível
            # Adicionar mais ações conforme a necessidade (ex: jogar em diferentes posições, outras cartas)
        }

        agent_type = self.config["ai"]["agent_type"]
        if agent_type == "RuleBased":
            self.agent = RuleBasedAgent(config, self.action_map)
        elif agent_type == "DQN":
            self.agent = DQN_Agent(config, self.action_map, game_state_instance)
        else:
            raise ValueError(f"Tipo de agente \'{agent_type}\' não suportado.")

    def make_decision(self):
        # O estado atual para o agente de RL é obtido dentro do método select_action do agente
        decision = self.agent.select_action(self.game_state, self.game_state.frame_id)
        
        # Lógica de recompensa e treino (se training_mode for True e for um agente RL)
        if self.config["ai"]["training_mode"] and isinstance(self.agent, DQN_Agent):
            # A recompensa real só é conhecida após a execução da ação e observação do próximo estado
            # Para o treino offline/simulação, o ambiente RLEnvironment já simula isso
            # current_state_vec = self.agent.env.get_observation() # Já obtido em select_action
            # action_index = decision.get("action_index")
            # next_state_vec, reward, done, _ = self.agent.env.step(action_index) # Simula o próximo passo
            
            # No loop principal, o `learn` será chamado com o estado real, recompensa e próximo estado
            # Aqui, apenas atualizamos a recompensa para o GameState para fins de log/display
            # reward = self.agent.env.get_reward(decision.get("action_index")) # Recompensa baseada na ação e estado atual
            # self.game_state.set_last_reward(reward) # Atualizar recompensa no estado do jogo
            pass # A lógica de learn e record_transition será movida para o main_bot.py

        return decision


if __name__ == "__main__":
    # Exemplo de uso e treino offline simplificado
    import yaml
    from ai.game_state import GameState # Importar GameState real para simulação

    # Criar um config.yaml de exemplo se não existir
    if not os.path.exists("config.yaml"):
        sample_config = {
            "ai": {
                "agent_type": "DQN", # Mude para "RuleBased" para testar o agente baseado em regras
                "model_save_path": "./ai/models/dqn_model.pth",
                "training_mode": True,
                "offline_training_data_path": "./ai/training_data",
                "transition_log_path": "./ai/transitions.csv",
                "batch_size": 32,
                "replay_buffer_size": 1000,
                "epsilon_start": 1.0,
                "epsilon_decay": 0.995,
                "epsilon_min": 0.01,
                "gamma": 0.99,
                "target_update_freq": 10
            }
        }
        os.makedirs("./ai/models", exist_ok=True)
        with open("config.yaml", "w") as f:
            yaml.dump(sample_config, f)
        logging.info("config.yaml de exemplo criado para teste do agente de RL.")

    # Usar GameState real para o ambiente de simulação
    game_state_instance = GameState()
    
    # Carregar configuração
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    decision_maker = DecisionSystem(game_state_instance, config)

    logging.info(f"\n--- Teste do Agente ({config["ai"]["agent_type"]}) em modo de simulação ---")
    
    num_episodes = 5 # Número de episódios de simulação
    for episode in range(num_episodes):
        logging.info(f"Iniciando Episódio {episode + 1}")
        state_vec = decision_maker.agent.env.reset() # Resetar o ambiente para um novo episódio
        done = False
        total_reward = 0
        step = 0

        while not done and step < 200: # Limitar passos por episódio
            game_state_instance.frame_id = step # Simular frame_id
            
            # Selecionar ação
            decision = decision_maker.agent.select_action(game_state_instance, game_state_instance.frame_id)
            action_index = decision.get("action_index", 0)

            # Simular o passo no ambiente
            next_state_vec, reward, done, _ = decision_maker.agent.env.step(action_index)
            total_reward += reward

            # Aprender e registrar transição (se for DQN em modo de treino)
            if isinstance(decision_maker.agent, DQN_Agent) and config["ai"]["training_mode"]:
                decision_maker.agent.learn(state_vec, action_index, reward, next_state_vec, done)
                decision_maker.agent.record_transition(time.time(), game_state_instance.frame_id, state_vec, action_index, reward, next_state_vec, done)

            state_vec = next_state_vec
            step += 1

            if isinstance(decision_maker.agent, DQN_Agent) and decision_maker.agent.learn_step_counter % decision_maker.agent.target_update_freq == 0:
                decision_maker.agent.update_target_network()
                logging.info(f"  Episódio {episode + 1}, Passo {step}: Epsilon = {decision_maker.agent.epsilon:.2f}")
        
        logging.info(f"Episódio {episode + 1} terminado. Recompensa Total: {total_reward:.2f}, Passos: {step}")

    if isinstance(decision_maker.agent, DQN_Agent):
        decision_maker.agent.save_model()
    logging.info("\nTreino offline/simulação concluído.")
    logging.info("Para um treino offline completo, você precisará de um ambiente de simulação mais detalhado e coleta de dados realistas.")


