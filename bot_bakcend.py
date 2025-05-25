from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from flask import Flask, request, jsonify
import re

llm = OllamaLLM(model="llama3.2")

template = """
You are "Chunni", an intelligent and friendly WhatsApp assistant for Anas Mohammed.

Your job is to act as a smart agent and chatbot who:
- Helps with general questions or queries.
- Detects and replies appropriately to meeting/event scheduling, reminders, or task-related messages.
- Provides accurate and polite responses for any kind of message received through WhatsApp.
- Understands the context of previous chat history, if available.
- Replies in a friendly, natural tone — avoid thinking out loud or showing internal thoughts (e.g., no <think> or system-like responses).

Be short, relevant, and human-like in your reply.

Here is the chat history so far:
{history}

Here is the new incoming message:
{question}

Give your best response below:
"""


chat_histories={}

prompt = ChatPromptTemplate.from_template(template)

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process():
    print("chat history: ", chat_histories)
    data = request.get_json()
    question = data.get("message")  # Changed from "question" to "message" to match your bot's POST data
    user_id=data.get("user_id", "default_user")  # Get user_id from the request, default to "default_user"
    print(f"Question received: {question}")
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    history=chat_histories.get(user_id, [])
    history_string= "\n".join(history)
    history.append(f"User: {question}")

    chain = prompt | llm
    result = chain.invoke({"history":history_string ,"question": question})
    clean_result = re.sub(r"<think>.*?</think>", "", result, flags=re.DOTALL).strip()
    history.append(f"Bot: {clean_result}")
    chat_histories[user_id] = history
    print(f"Bot reply: {clean_result}")
    return jsonify({"reply": clean_result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
