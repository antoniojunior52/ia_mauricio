import os
import requests
from flask import Flask, render_template, request, redirect, url_for
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures

# ----- CONFIGURAÇÃO -----
# Carregue suas chaves e endpoints (Vou explicar como obtê-los na Parte 2)
# É uma boa prática usar variáveis de ambiente
try:
    TRANSLATOR_KEY = os.environ.get("TRANSLATOR_KEY")
    TRANSLATOR_ENDPOINT = os.environ.get("TRANSLATOR_ENDPOINT")
    TRANSLATOR_REGION = os.environ.get("TRANSLATOR_REGION") # Ex: "eastus"

    VISION_KEY = os.environ.get("VISION_KEY")
    VISION_ENDPOINT = os.environ.get("VISION_ENDPOINT")
except Exception as e:
    print(f"Erro ao carregar variáveis de ambiente: {e}")
    print("Certifique-se de configurar suas chaves e endpoints.")

# Inicializa o app Flask
app = Flask(__name__)

# ----- PÁGINA INICIAL -----
@app.route('/')
def index():
    """Página inicial que leva às novas ferramentas."""
    return render_template('index.html')

# ----- RECURSO 1: TRADUTOR DE TEXTO -----
@app.route('/translate', methods=['GET', 'POST'])
def translate():
    """Página para o Tradutor de IA do Azure."""
    translated_text = ""
    if request.method == 'POST':
        try:
            # Pega o texto e o idioma do formulário
            text_to_translate = request.form['text']
            target_language = request.form['language']

            # Configura o cliente do Tradutor
            client = TextTranslationClient(
                endpoint=TRANSLATOR_ENDPOINT,
                credential=AzureKeyCredential(TRANSLATOR_KEY)
            )

            # Chama a API de Tradução
            response = client.translate(
                content=[text_to_translate],
                to_language=[target_language],
                from_language='pt' # Assumindo que a origem é Português
            )
            
            translated_text = response[0].translations[0].text

        except Exception as e:
            translated_text = f"Erro ao traduzir: {e}"

    return render_template('translate.html', translated_text=translated_text)

# ----- RECURSO 2: VISÃO (ANÁLISE DE IMAGEM) -----
@app.route('/vision', methods=['GET', 'POST'])
def vision():
    """Página para Análise de Imagem da IA do Azure."""
    analysis_result = None
    image_url = ""
    if request.method == 'POST':
        try:
            image_url = request.form['image_url']
            
            # Configura o cliente de Visão
            client = ImageAnalysisClient(
                endpoint=VISION_ENDPOINT,
                credential=AzureKeyCredential(VISION_KEY)
            )
            
            # Seleciona as features que queremos analisar
            features = [
                VisualFeatures.CAPTION, # Uma descrição da imagem
                VisualFeatures.TAGS,    # Tags de conteúdo
                VisualFeatures.OBJECTS  # Objetos detectados
            ]

            # Chama a API de Análise de Imagem a partir de uma URL
            result = client.analyze_from_url(
                image_url=image_url,
                visual_features=features,
                gender_neutral_caption=True # Para legendas neutras
            )
            
            analysis_result = result # Passa o objeto de resultado completo para o template

        except Exception as e:
            analysis_result = f"Erro ao analisar a imagem: {e}"

    return render_template('vision.html', result=analysis_result, image_url=image_url)

# ----- INICIA O SERVIDOR -----
if __name__ == '__main__':
    app.run(debug=True)