# Chatbot Universitário, desenvolvido por: Denilson, Bruna, Igor, Guilherme Lara e Nathan
import ollama
import gradio as gr
import fitz
import Interface
import os
from faster_whisper import WhisperModel
transcriber = WhisperModel("base")

# Persoanalização visual do chatbot
custom_chatbot = gr.Chatbot(
    label="Sua IA Pessoal",
    type="messages",
    show_copy_button=True,
    allow_file_downloads=True,
    height=500
)

# Interage com um modelo Ollama através de uma interface Gradio
def stream_chat(message, history):
    """
    Transmite a resposta do modelo Ollama e a envia para a interface Gradio.
    
    Args:
        message (str): A mensagem de entrada do usuário.
        history (list): Uma lista das mensagens anteriores da conversa.
        
    Yields:
        str: A resposta do chatbot, enviada em chunks.
    """

    processed_files = []
    pdf_contexts = []
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')

    # Garante que todos os arquivos enviados sejam processados, independente do formato
    all_files = []
    user_text = ""

    if isinstance(message, dict):
        files = message.get("files", [])
        if not isinstance(files, list):
            files = [files]
        all_files.extend(files)
        user_text = message.get("text", "")
    else:
        user_text = str(message)
    # Se houver arquivos duplicados, remove
    all_files = list(dict.fromkeys(all_files))

    text_from_files = []
    for file in all_files:
        filepath = file['path'] if isinstance(file, dict) and 'path' in file else file
        if isinstance(filepath, str):
            filename = os.path.basename(filepath)
            # Caso o usuario envie um txt
            if filepath.lower().endswith('.txt'):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        formatted = f"[Começo do arquivo {filename}: ]\n{content.strip()}\n[Fim do arquivo {filename}]\n"
                        text_from_files.append(formatted)
                except Exception:
                    pass  # ignora arquivos inválidos
                # Caso o usuario envie PDFs
            elif filepath.lower().endswith('.pdf'):
                try:
                    with fitz.open(filepath) as pdf:
                        pdf_text = "".join([page.get_text() for page in pdf])
                        formatted = f"[Começo do arquivo {filename}: ]\n{pdf_text.strip()}\n[Fim do arquivo {filename}]\n"
                        pdf_contexts.append(formatted)
                except Exception as e:
                    pass
                # Caso o usuario envie audios
            elif filepath.lower().endswith(('.mp3', '.wav')):
                try:
                    # Transcreve o áudio com Whisper, sempre assumindo português brasileiro
                    segments, _ = transcriber.transcribe(filepath, language="pt")
                    transcribed_text = " ".join(segment.text.strip() for segment in segments)
                    if transcribed_text:
                        print(f"Transcrição do áudio: {transcribed_text}\n")
                        text_from_files.append(f"[Conteúdo do áudio {filename}]: {transcribed_text} [Fim da transcrição]\n")
                except Exception as e:
                    print("Erro ao transcrever:", e)
                    # Caso o usuario envie imagens
            elif filepath.lower().endswith(image_extensions):
                try:
                    processed_files.append(filepath)
                except Exception as e:
                    pass
    
    # Extrai o texto digitado pelo usuário
    base_user_text = message["text"] if isinstance(message, dict) else str(message)

    # Adiciona mensagem do usuário ao histórico
    if text_from_files:
        user_text = base_user_text + "\n\n" + "\n\n".join(text_from_files)
    else:
        user_text = base_user_text
    history.append({"role": "user", "content": user_text, "images": processed_files})

    model_messages = [
        {"role": msg["role"], "content": str(msg["content"])}
        for msg in history if "role" in msg and "content" in msg
    ]

    # Junta PDFs e .txts em um único contexto
    combined_contexts = pdf_contexts + text_from_files
    if combined_contexts:
        all_context = "\n\n".join(combined_contexts)
        model_messages.insert(0, {
            "role": "system",
            "content": f"Responda sempre em português do Brasil. Os textos a seguir são documentos enviados pelo usuário para dar contexto à próxima pergunta. Use apenas como referência, não repita nem cite explicitamente: {all_context}"
        })
    else:
        # Força o modelo a responder em português
        model_messages.insert(0, {
            "role": "system",
            "content": "Responda sempre em português do Brasil."
        })

    stream = ollama.chat(
        model='llama3.2-vision', # Define que modelo sera utilizado, idealmente llama3.2-vision
        messages=model_messages,
        stream=True,
    )

    response_text = ""
    for chunk in stream:
        content = chunk['message']['content']
        response_text += content
        yield response_text

    # Salva resposta do modelo no histórico    
    history.append({"role": "assistant", "content": response_text})

# Cria uma textbox personalizada que permite envio de múltiplos arquivos simultaneos
multimodal_textbox = gr.MultimodalTextbox(
    file_types=[".pdf", ".txt", ".png", ".jpg", ".jpeg", ".webp", ".wav", ".mp3"],
    file_count="multiple",
    placeholder="Digite sua pergunta...",
    stop_btn=True,
    label=None,
    sources=["microphone", "upload"],
    max_plain_text_length=50000
)

# Cria uma interface Gradio ChatInterface
chat = Interface.ChatInterface(
    fn=stream_chat,
    title="Chatbot Universitário",
    description="by Denilson, Bruna, Igor, Guilherme Lara e Nathan",
    type="messages",
    examples=[{"text": "Me de ideis de prompts para te testar"}, {"text": "Quais os prospectos futuros da IA para o mercado"}, {"text": "Me explique as limitações do seu modelo de forma breve"}],  # Inputs de exemplo
    multimodal=True,
    save_history=True,
    editable=True,
    theme="default",
    chatbot=custom_chatbot,
    flagging_mode="manual",
    textbox=multimodal_textbox
)
    # Mantém o histórico de conversas
chat.saved_conversations.secret = "abcdefasd6200683922" 
chat.saved_conversations.storage_key = "chatbot_universitario" 
chat.launch()