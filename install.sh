
#!/bin/bash

echo "Iniciando a instalação das dependências do Clash Royale AI Bot..."

# Instalar dependências Python
echo "Instalando dependências Python via pip..."
pip install -r requirements.txt

# Instalar ADB (Android Debug Bridge)
echo "\n--- Instalação do ADB ---"
echo "Para o bot funcionar, você precisa ter o Android Debug Bridge (ADB) instalado e configurado no seu sistema."
echo "No Windows, você pode baixar as Platform Tools do Android SDK: https://developer.android.com/studio/releases/platform-tools"
echo "Após baixar, extraia o conteúdo e adicione o caminho da pasta `platform-tools` às variáveis de ambiente do sistema (PATH)."
echo "No Linux/macOS, você pode instalar via gerenciador de pacotes:"
echo "  Linux: sudo apt-get update && sudo apt-get install -y adb"
echo "  macOS: brew install android-platform-tools (com Homebrew)"
echo "Certifique-se de que o comando `adb` está acessível no seu terminal."

# Instalar Tesseract OCR
echo "\n--- Instalação do Tesseract OCR ---"
echo "Para a funcionalidade de OCR (leitura de texto em imagens), você precisa instalar o Tesseract OCR."
echo "No Windows, baixe o instalador em: https://tesseract-ocr.github.io/tessdoc/Installation.html"
echo "No Linux, instale via gerenciador de pacotes: sudo apt-get update && sudo apt-get install -y tesseract-ocr"
echo "No macOS, instale via Homebrew: brew install tesseract"
echo "Após a instalação, verifique se o comando `tesseract` está acessível no seu terminal."

# Baixar modelo YOLOv8 (se não existir)
echo "\n--- Verificando e baixando modelo YOLOv8 ---"
if [ ! -f vision/yolov8n.pt ]; then
    echo "Modelo yolov8n.pt não encontrado em vision/. Tentando baixar..."
    python -c "from ultralytics import YOLO; YOLO('yolov8n.pt').export(format='torchscript', filename='vision/yolov8n.pt')" || \
    echo "Erro ao baixar yolov8n.pt. Por favor, baixe-o manualmente e coloque-o em vision/yolov8n.pt."
else
    echo "Modelo yolov8n.pt já existe em vision/."
fi

echo "\nInstalação concluída. Lembre-se de configurar o arquivo config.yaml antes de executar o bot."

