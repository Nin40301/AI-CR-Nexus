
# Projeto de IA Jogadora para Clash Royale com BlueStacks 5 (Atualizado)

## 1. Visão Geral

Este projeto é uma implementação avançada de um bot de Inteligência Artificial para o jogo Clash Royale, projetado para fins educacionais e de pesquisa em IA e automação de jogos. Ele foi reconstruído do zero com uma arquitetura modular, visando maior inteligência, flexibilidade e compatibilidade aprimorada com o emulador BlueStacks 5 através da integração com **ADB (Android Debug Bridge)**, **YOLOv8**, **OCR (Optical Character Recognition)** e **Template Matching** para visão computacional.

O objetivo principal é demonstrar como técnicas de visão computacional, aprendizado por reforço e automação podem ser aplicadas para criar um agente autônomo e inteligente em um ambiente de jogo complexo. O projeto agora inclui um sistema de fallback de visão, coleta automática de screenshots para dataset, um sistema de decisão aprimorado com prioridade de ações e delays realistas, e um modo de simulação para o agente de Reinforcement Learning.

**Aviso Importante:** Este projeto é estritamente para fins educacionais e de pesquisa. O uso de bots pode violar os Termos de Serviço de jogos e plataformas. Utilize por sua conta e risco e **NUNCA** em contas principais ou para obter vantagem competitiva injusta.

## 2. Arquitetura do Sistema

A arquitetura do bot é modular, dividida nos seguintes componentes principais, organizados em subpastas para melhor organização:

| Módulo/Subpasta | Descrição | Tecnologias Principais |
| :--- | :--- | :--- |
| **`emulator/adb_capture.py`** | Captura frames da tela do BlueStacks 5 via ADB, com detecção automática da resolução do dispositivo e suporte a múltiplas resoluções. | ADB, `subprocess`, `OpenCV` |
| **`emulator/adb_actions.py`** | Executa ações no BlueStacks 5 (toques, swipes) via comandos ADB, com dry-run, retries, delays configuráveis e ajuste dinâmico de coordenadas. | ADB, `subprocess` |
| **`vision/object_detection.py`** | Processa os frames capturados para identificar elementos do jogo (cartas, tropas, torres, elixir) usando um pipeline configurável com YOLOv8, OCR e Template Matching como fallback. | `YOLOv8 (ultralytics)`, `OpenCV`, `NumPy`, `Pytesseract` |
| **`ai/game_state.py`** | Mantém uma representação interna do estado atual do jogo com base nas detecções, incluindo elixir, cartas na mão, tropas no campo e vida das torres, com `frame_id` e `timestamp`. É a única fonte de verdade para o estado do jogo. | Python puro, estruturas de dados |
| **`ai/decision_system.py`** | O "cérebro" do bot, que analisa o `GameState` e decide a próxima ação a ser tomada, utilizando um agente modular (RuleBased ou Reinforcement Learning como DQN). Inclui API para treino offline e modo de simulação. | `PyTorch`, `NumPy`, `collections.deque` |
| **`main_bot.py`** | O script principal que orquestra a execução de todos os módulos em um loop contínuo (Captura → Detecção → Atualização do estado → Decisão → Ação) usando threads e filas para processamento paralelo. Inclui logs de desempenho, delays ajustáveis e logs visuais de debug. | Python puro, `yaml`, `logging`, `threading`, `queue` |
| **`config.yaml`** | Arquivo de configuração centralizado para resolução, pipeline de detecção, parâmetros do agente de IA, delays do loop principal, e configurações de debug visual. | YAML |
| **`requirements.txt`** | Lista de todas as dependências Python necessárias para o projeto. | Pip |
| **`install.sh`** | Script auxiliar para automatizar a instalação das dependências Python, e fornecer instruções para ADB e Tesseract OCR. | Bash |
| **`utils/dataset_collector.py`** | Ferramenta para coletar automaticamente screenshots e gerar anotações em formato YOLO, facilitando a criação de datasets para treinamento de modelos de visão. | `OpenCV`, `NumPy`, `YOLOv8` |

## 3. Instalação e Configuração

### 3.1. Pré-requisitos

Para executar este projeto, você precisará dos seguintes itens:

*   **Python 3.8+:** Recomenda-se Python 3.8 ou superior.
*   **Android Debug Bridge (ADB):** Instalado e configurado no seu sistema. Você pode baixá-lo como parte das Android SDK Platform Tools. Certifique-se de que o executável `adb` esteja no seu PATH ou especifique o caminho completo no `config.yaml`.
    *   **No Windows:** Baixe as Platform Tools do Android SDK: [https://developer.android.com/studio/releases/platform-tools](https://developer.android.com/studio/releases/platform-tools). Após baixar, extraia o conteúdo e adicione o caminho da pasta `platform-tools` às variáveis de ambiente do sistema (PATH).
    *   **No Linux:** `sudo apt-get update && sudo apt-get install -y adb`
    *   **No macOS:** `brew install android-platform-tools` (com Homebrew)
    *   Verifique a instalação executando `adb version` no terminal.
*   **Tesseract OCR:** Instalado no seu sistema para a funcionalidade de OCR (leitura de texto, como o elixir). Verifique a instalação executando `tesseract --version` no terminal.
    *   **No Windows:** Baixe o instalador em: [https://tesseract-ocr.github.io/tessdoc/Installation.html](https://tesseract-ocr.github.io/tessdoc/Installation.html)
    *   **No Linux:** `sudo apt-get update && sudo apt-get install -y tesseract-ocr`
    *   **No macOS:** `brew install tesseract` (com Homebrew)
*   **BlueStacks 5:** O emulador deve estar instalado e configurado para rodar o Clash Royale.
    *   **Conecte o BlueStacks ao ADB:** Abra o BlueStacks e, em um terminal, execute `adb connect localhost:5555` (a porta pode variar, verifique nas configurações do BlueStacks ou com `adb devices`).
    *   Certifique-se de que o Clash Royale esteja instalado e aberto no BlueStacks.
*   **Modelos de Visão:**
    *   **Modelo YOLOv8 Treinado:** Para detecção de objetos eficaz, você precisará de um modelo YOLOv8 treinado para Clash Royale (cartas, tropas, torres, barra de elixir, etc.). Um modelo `yolov8n.pt` pré-treinado será baixado automaticamente para o diretório `vision/` se não for encontrado, mas para detecções específicas do jogo, um modelo personalizado é altamente recomendado.
    *   **Templates para Template Matching:** Para o sistema de fallback, coloque imagens PNG/JPG precisas dos elementos do jogo (cartas, torres, etc.) no diretório `templates/clash_royale/`.

### 3.2. Instalação das Dependências Python

Abra um terminal na raiz do projeto e execute o script de instalação:

```bash
chmod +x install.sh
./install.sh
```

Este script instalará as bibliotecas Python listadas em `requirements.txt` e tentará baixar o modelo `yolov8n.pt` para a pasta `vision/` se ele não existir.

### 3.3. Estrutura do Projeto

Certifique-se de que a estrutura de pastas esteja organizada da seguinte forma:

```
. (raiz do projeto)
├── config.yaml
├── main_bot.py
├── README.md
├── requirements.txt
├── install.sh
├── ai/
│   ├── __init__.py
│   ├── game_state.py
│   └── decision_system.py
├── emulator/
│   ├── __init__.py
│   ├── adb_capture.py
│   └── adb_actions.py
├── vision/
│   ├── __init__.py
│   ├── object_detection.py
│   └── yolov8n.pt  # Será baixado automaticamente ou coloque seu modelo treinado aqui
├── utils/
│   ├── __init__.py
│   └── dataset_collector.py # Ferramenta para coletar dataset
├── logs/             # Diretório para logs de desempenho
├── debug_screenshots/ # Diretório para screenshots de debug (se ativado)
└── templates/clash_royale/ # Diretório para templates de Template Matching
    └── *.png / *.jpg # Seus arquivos de template
```

### 3.4. Configuração do `config.yaml`

Edite o arquivo `config.yaml` na raiz do projeto para ajustar as configurações conforme seu ambiente e preferências. Preste atenção especial à seção `vision.detection_pipeline` para configurar a ordem e os parâmetros dos detectores.

```yaml
# config.yaml

# Configurações do Emulador (BlueStacks 5 via ADB)
emulator:
  adb_path: "adb" # Caminho para o executável ADB. Pode ser "adb" se estiver no PATH.
  device_id: "localhost:5555" # ID do dispositivo ADB. Use `adb devices` para listar.
  resolution_width: 1920 # Largura da resolução lógica do jogo Clash Royale. Usado para mapeamento.
  resolution_height: 1080 # Altura da resolução lógica do jogo Clash Royale. Usado para mapeamento.
  adb_command_timeout: 10 # Tempo limite para comandos ADB em segundos

# Configurações de Visão (Object Detection)
vision:
  # A pipeline de detecção define a ordem e os tipos de detectores a serem usados.
  # Cada entrada é um dicionário com \'type\' (YOLOv8, OCR, TemplateMatching) e configurações específicas.
  # \'stop_on_success\': Se True, a pipeline para após o primeiro detector encontrar detecções.
  detection_pipeline:
    - type: "YOLOv8" # Tenta YOLOv8 primeiro
      yolov8_model_path: "vision/yolov8n.pt" # Caminho para o modelo YOLOv8 (ex: yolov8n.pt, best.pt)
      stop_on_success: False # Pode ser True se o YOLOv8 for muito confiável
    - type: "OCR" # Depois OCR para elixir e outros textos
      ocr_rois: # Regiões de Interesse para OCR no formato [x, y, w, h] da resolução lógica
        elixir_bar: [700, 1000, 500, 80] # Exemplo de ROI para a barra de elixir
        # Adicione outras ROIs de texto aqui, como nomes de cartas, pontuação, etc.
      stop_on_success: False
    - type: "TemplateMatching" # Por último Template Matching para fallback
      templates_dir: "templates/clash_royale" # Diretório onde os templates PNG/JPG estão
      stop_on_success: False

  # Configurações gerais de detecção, aplicáveis a YOLOv8 e TemplateMatching
  confidence_threshold: 0.5 # Limiar de confiança para detecções
  iou_threshold: 0.7 # Limiar de IoU para Non-Maximum Suppression (apenas YOLOv8)
  roboflow_api_key: "" # Chave da API Roboflow, se usar Roboflow (não implementado totalmente)
  roboflow_project_id: "" # ID do projeto Roboflow
  roboflow_model_version: "" # Versão do modelo Roboflow

# Configurações do Agente de IA (Reinforcement Learning)
ai:
  agent_type: "RuleBased" # Ou "DQN", "PPO" (DQN implementado de forma básica)
  model_save_path: "./ai/models/dqn_model.pth" # Caminho para salvar o modelo do agente
  training_mode: False # True para modo de treino, False para modo de inferência
  offline_training_data_path: "./ai/training_data" # Caminho para dados de treino offline
  transition_log_path: "./ai/transitions.csv" # Caminho para log de transições do RL
  batch_size: 32 # Tamanho do batch para treino do DQN
  replay_buffer_size: 10000 # Tamanho do replay buffer para DQN
  epsilon_start: 1.0 # Epsilon inicial para exploração DQN
  epsilon_decay: 0.995 # Fator de decaimento do epsilon DQN
  epsilon_min: 0.01 # Epsilon mínimo DQN
  gamma: 0.99 # Fator de desconto DQN
  target_update_freq: 10 # Frequência de atualização da target network DQN

# Configurações do Loop Principal
main_loop:
  capture_delay_sec: 0.05 # Delay entre capturas (aprox. 20 FPS)
  vision_delay_sec: 0.05 # Delay entre processamentos de visão
  decision_delay_sec: 0.05 # Delay entre decisões
  tap_delay_ms: 100 # Delay em milissegundos após um tap/swipe ADB
  log_performance: True # Registrar logs de desempenho
  log_file_path: "./logs/performance.log" # Caminho para o arquivo de log
  save_debug_screenshots: False # Salvar screenshots de debug com bounding boxes
  debug_screenshots_path: "./debug_screenshots" # Caminho para salvar screenshots de debug

# Configurações da Interface de Usuário (Opcional)
ui:
  enable_fastapi_panel: False # Habilitar painel FastAPI
  fastapi_port: 8000

# Configurações para Coleta de Dataset
dataset_collector:
  output_directory: "./dataset/clash_royale" # Diretório onde as imagens e anotações serão salvas
  auto_annotate: True # Se True, tentará pré-anotar as imagens com o detector atual
  annotation_format: "yolo" # Formato das anotações (atualmente suporta \'yolo\')
  class_mapping: # Mapeamento de nomes de classes para IDs numéricos (necessário para YOLO)
    card_knight: 0
    card_archers: 1
    elixir_bar: 2
    player_king_tower: 3
    enemy_king_tower: 4
    # Adicione aqui todas as classes que seu modelo YOLOv8 ou Template Matching detecta
```

**Atenção:**
*   Para `device_id`, use `adb devices` para listar seus dispositivos e encontrar o ID correto (ex: `localhost:5555` para BlueStacks).
*   O `yolov8_model_path` deve apontar para o seu modelo treinado. Se você treinar seu próprio modelo, atualize este caminho. O modelo `yolov8n.pt` será baixado automaticamente para `vision/` se não existir.
*   Para usar o agente DQN, mude `agent_type` para `DQN` e ajuste os parâmetros de treino em `ai/decision_system.py` e `config.yaml`.

## 4. Como Executar

1.  Certifique-se de que o BlueStacks 5 com Clash Royale esteja aberto e conectado ao ADB (`adb connect localhost:5555`).
2.  Certifique-se de que o `config.yaml` esteja configurado corretamente.
3.  Abra um terminal na raiz do projeto.
4.  Execute o script de instalação para garantir que todas as dependências estejam instaladas:
    ```bash
    chmod +x install.sh
    ./install.sh
    ```
5.  Execute o script principal:

    ```bash
    python3.11 main_bot.py
    ```

    Você também pode executar em modo `dry-run` para testar a detecção e decisão sem executar ações reais no BlueStacks:
    ```bash
    python3.11 main_bot.py --dry-run
    ```

O bot iniciará a captura da tela do BlueStacks, exibirá uma janela com a detecção de objetos em tempo real e começará a tomar decisões e executar ações (se não estiver em `dry-run`) no jogo. Pressione a tecla `q` na janela de visualização do OpenCV para encerrar o bot.

### 4.1. Coleta de Dataset

Para coletar screenshots e gerar anotações automaticamente para treinar seu próprio modelo YOLOv8, você pode usar o `dataset_collector.py`:

1.  Configure a seção `dataset_collector` em `config.yaml`.
2.  Execute o script:
    ```bash
    python3.11 utils/dataset_collector.py
    ```
    Você pode passar argumentos para o número de screenshots e o delay:
    ```bash
    python3.11 utils/dataset_collector.py --num_screenshots 100 --delay_sec 5
    ```

## 5. Detalhes dos Módulos e Melhorias

### `emulator/adb_capture.py`

Agora utiliza `adb exec-out screencap -p` para capturar a tela, o que é mais eficiente e robusto para BlueStacks 5. Inclui detecção automática da resolução do dispositivo via `adb shell wm size` e um `timeout` configurável para os comandos ADB. A resolução detectada é usada para ajustar dinamicamente as coordenadas.

### `emulator/adb_actions.py`

Implementa `adb shell input tap x y` para cliques e `adb shell input swipe x1 y1 x2 y2 duration` para arrastar. As coordenadas são automaticamente ajustadas da resolução lógica do jogo (definida em `config.yaml`) para a resolução real do dispositivo detectada pelo `adb_capture`. Inclui funcionalidade de `dry-run`, `retries` para comandos falhos e `tap_delay_ms` para simular um comportamento mais humano e delays realistas.

### `vision/object_detection.py`

Foi atualizado para integrar um **pipeline de detecção configurável** em `config.yaml`. Ele pode usar:
*   **YOLOv8:** Carrega um modelo `.pt` (como `yolov8n.pt`) e o utiliza para detectar objetos. As detecções incluem nome da classe, confiança e bounding box.
*   **OCR (Optical Character Recognition):** Usa `pytesseract` para detecção de texto em Regiões de Interesse (ROIs) configuráveis, como o valor do elixir. Inclui pré-processamento de imagem aprimorado para OCR de elixir.
*   **Template Matching:** Utiliza `cv2.matchTemplate` com templates PNG/JPG para detecção de objetos, servindo como um sistema de fallback robusto para quando o YOLOv8 não estiver treinado ou falhar. Suporta templates com canal alfa para máscaras.

O pipeline permite definir a ordem de execução dos detectores e se deve parar após a primeira detecção bem-sucedida.

### `ai/game_state.py`

A classe `GameState` foi aprimorada para ser a **única fonte de verdade** do estado do jogo. Ela armazena informações mais detalhadas e com um `frame_id` e `timestamp` para cada atualização. A lógica de `update_state` agora espera os rótulos de classes dos detectores (YOLOv8, OCR, Template Matching) para preencher o estado do jogo (elixir, cartas, tropas, torres). Possui `getters` claros para acessar os dados do estado.

### `ai/decision_system.py`

Este módulo agora inclui um esqueleto para um **Agente de Reinforcement Learning (DQN)** usando `PyTorch`, com classes modulares `Agent`, `RuleBasedAgent` e `DQN_Agent`. Ele define um `RLEnvironment` simplificado que permite um **modo de simulação** para o agente de RL. O agente pode operar em `training_mode` (para explorar e aprender) ou em modo de inferência. Um modo `RuleBased` simples é mantido como alternativa, com **prioridade de ações e delays realistas** configuráveis. O treino offline é simulado, e um log de transições (`transitions.csv`) é mantido para facilitar o treinamento e análise. Parâmetros como `epsilon_decay`, `gamma`, `batch_size` e `replay_buffer_size` são configuráveis via `config.yaml`.

### `main_bot.py`

O loop principal foi redesenhado para usar **threads e filas (`Queue`)** para processamento paralelo, garantindo que a captura, visão, decisão e ação ocorram de forma assíncrona e eficiente. Inclui logging de desempenho (tempo por ciclo, FPS real) e `delay_between_cycles_sec`, `capture_delay_sec`, `vision_delay_sec`, `decision_delay_sec` configuráveis para controlar a velocidade do bot. Adicionado suporte para **logs visuais de debug** e **gerenciamento de diretórios** para salvar screenshots com bounding boxes (`debug_screenshots/`). A visualização OpenCV agora é manipulada no thread principal para evitar problemas de GUI.

### `utils/dataset_collector.py`

Um novo módulo para coletar automaticamente screenshots do BlueStacks e gerar arquivos de anotação no formato YOLO. Isso facilita a criação de datasets personalizados para treinar modelos YOLOv8 específicos para o Clash Royale. Permite pré-anotação automática usando os detectores configurados no `object_detection.py`.

## 6. Próximos Passos e Extensões

*   **Treinamento YOLOv8 Customizado:** Treine seu próprio modelo YOLOv8 com um dataset de imagens do Clash Royale para detecção precisa de cartas, tropas, elixir e elementos da UI. Isso é crucial para o desempenho do bot.
*   **Refinamento do Agente de RL:** Expanda o `RLEnvironment` para uma representação mais rica do estado do jogo e uma função de recompensa mais significativa. Implemente um loop de treino offline robusto ou considere a integração com frameworks de RL como `Stable Baselines3` para treinamento online.
*   **Interface de Usuário (Opcional):** Desenvolva um painel de controle com FastAPI (ou outra tecnologia) para monitoramento em tempo real e controle do bot.
*   **Gerenciamento de Decks:** Adicione suporte para múltiplos perfis de decks e estratégias associadas.
*   **Análise de Partidas:** Implemente um sistema para registrar e analisar o desempenho do bot ao longo do tempo (vitórias/derrotas, estatísticas de jogo).
*   **OCR Avançado:** Melhore a detecção de elixir e outros textos usando técnicas de pré-processamento de imagem mais avançadas e ajuste fino do Tesseract.

## 7. Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para fazer um fork do repositório, implementar melhorias e enviar Pull Requests. Sugestões e relatórios de bugs também são muito apreciados.

## 8. Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

