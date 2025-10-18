## Arquitetura e Especificações Técnicas: IA para Clash Royale

### 1. Visão Geral da Arquitetura

A arquitetura do sistema será dividida em módulos independentes e coesos, cada um com uma responsabilidade clara e bem definida. Essa abordagem modular facilitará o desenvolvimento, a manutenção e a expansão do projeto. A comunicação entre os módulos será realizada por meio de interfaces claras e, sempre que possível, de forma assíncrona para garantir o desempenho e a responsividade do sistema.

A seguir, apresentamos os principais módulos do sistema:

| Módulo | Descrição | Tecnologias Sugeridas |
| :--- | :--- | :--- |
| **Captura de Tela** | Responsável por capturar a tela do emulador BlueStacks 5 de forma eficiente e contínua. | `pygetwindow`, `Pillow`, `NumPy` |
| **Detecção de Objetos** | Utilizará modelos de visão computacional para identificar e localizar elementos do jogo na tela capturada, como tropas, cartas, elixir e torres. | `OpenCV`, `TensorFlow`/`PyTorch` |
| **Estado do Jogo** | Manterá uma representação interna do estado atual do jogo com base nas informações fornecidas pelo módulo de Detecção de Objetos. | Estruturas de dados em Python |
| **Sistema de Decisão** | O "cérebro" da IA. Com base no estado do jogo, decidirá qual a próxima ação a ser tomada (ex: jogar uma carta, esperar, etc.). | Aprendizado por Reforço (ex: DQN, PPO), árvores de decisão, ou algoritmos genéticos. |
| **Controle de Ações** | Traduzirá as decisões do Sistema de Decisão em ações concretas no emulador, como cliques e movimentos do mouse. | `PyAutoGUI` |
| **Interface de Usuário (Opcional)** | Uma interface gráfica para facilitar a configuração, o monitoramento e o controle do bot. | `Tkinter`, `PyQt`, ou uma interface web com `Flask`/`FastAPI`. |

### 2. Especificações Técnicas

#### 2.1. Módulo de Captura de Tela

*   **Funcionalidade:** Capturar a janela do BlueStacks 5 em uma taxa de quadros (framerate) configurável.
*   **Requisitos:**
    *   Identificar a janela do BlueStacks 5 pelo título.
    *   Permitir a configuração da região de captura (para otimizar o desempenho).
    *   Converter a imagem capturada para um formato adequado para o módulo de Detecção de Objetos (ex: array NumPy).

#### 2.2. Módulo de Detecção de Objetos

*   **Funcionalidade:** Processar os frames recebidos do módulo de Captura de Tela e identificar os elementos do jogo.
*   **Requisitos:**
    *   Treinar modelos de detecção de objetos para reconhecer as diferentes cartas, tropas e elementos da arena do Clash Royale.
    *   Retornar as coordenadas e os rótulos dos objetos detectados em cada frame.
    *   Otimizar os modelos para inferência em tempo real.

#### 2.3. Módulo de Estado do Jogo

*   **Funcionalidade:** Consolidar as informações da Detecção de Objetos em uma estrutura de dados que represente o estado atual da partida.
*   **Requisitos:**
    *   Manter o controle do elixir atual.
    *   Rastrear a posição das tropas aliadas e inimigas.
    *   Manter o estado das torres (HP).
    *   Conhecer as cartas disponíveis na mão do jogador.

#### 2.4. Módulo de Sistema de Decisão

*   **Funcionalidade:** Implementar a lógica de jogo da IA.
*   **Requisitos:**
    *   Receber o estado do jogo como entrada.
    *   Implementar um algoritmo de tomada de decisão (a ser definido, com possibilidade de múltiplas estratégias).
    *   Retornar a ação a ser executada (ex: `JOGAR_CARTA`, `POSICAO_X`, `POSICAO_Y`).

#### 2.5. Módulo de Controle de Ações

*   **Funcionalidade:** Executar as ações decididas pelo Sistema de Decisão no emulador.
*   **Requisitos:**
    *   Mapear as coordenadas do jogo para as coordenadas da tela do emulador.
    *   Simular cliques do mouse para selecionar e jogar cartas.
    *   Garantir que as ações sejam executadas de forma precisa e confiável.

### 3. Próximos Passos

Com a arquitetura e as especificações definidas, o próximo passo é a implementação de cada um dos módulos, começando pelo Módulo de Captura de Tela e, em seguida, pelo Módulo de Detecção de Objetos. Esses dois módulos são a base para a percepção da IA sobre o ambiente do jogo.

