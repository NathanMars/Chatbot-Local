# Chatbot-Local
Um Chatbot pessoal rodando localmente num servidor Ollama usando uma interface customizada do Gradio, desenolvido para um projeto acadêmico.  

---

## Instruções  
- Instale o Ollama [da fonte oficial](https://ollama.com/download)  
- No terminal, na pasta raiz do projeto:\
  `pip install -r requirements.txt`
- Reinicie a IDE caso necessário
- No terminal, na raiz do projeto, importe o modelo que deseja usar, o comando ideal seria:\
  `ollama pull llama3.2-vision`  
- Rodar aplicação através de App.py

Se quiser testar outros modelos, basta:
1. Alterar o conteúdo de model no lrecho de App.py

      `stream = ollama.chat(`\
              `model='llama3.2-vision',`\
              `messages=model_messages,`\
              `stream=True,`\
          `)`

2. Rodar um dos comandos da lista do [repositório oficial do Ollama](https://github.com/ollama/ollama)\
**Observação:** Se for usar outro modelo, use `pull` ao invés do `run` que o readme do Ollama sugere, pra evitar rodar o modelo duas vezes ao baixar ele.

---

**Grupo:** Nathan Marques Silva, Bruna Cristina Mafra, Denilson dos Santos Proença Pereira, Igor Fernando Souza e Silva, Guilherme Lara Vieira Carvalho

