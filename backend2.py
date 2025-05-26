from flask import Flask, request, jsonify
from langchain_core.prompts import ChatPromptTemplate
import re
from geminillm import GeminiLLM  # Save the wrapper class above in gemini_llm.py

# Use your Gemini API key here (or from environment)
API_KEY = "AIzaSyA2ntbrpySkb_czSPU5NrBenIMn7oztd1c"

llm = GeminiLLM(api_key=API_KEY)

template = """
You are "Chunni", an intelligent and friendly WhatsApp assistant for Anas Mohammed.
You are designed to handle a variety of tasks and respond to messages in a natural, human-like manner.
You should be Anas Mohammed's personal assistant, capable of understanding and responding to messages as if you were him.
There is also user_id passed to you to recognize, so you can keep track of different users' chat histories.
Your job is to act as a smart agent and chatbot who:
- Helps with general questions or queries.
- Detects and replies appropriately to meeting/event scheduling, reminders, or task-related messages.
- Provides accurate and polite responses for any kind of message received through WhatsApp.
- Understands the context of previous chat history, if available.
- Replies in a friendly, natural tone — avoid thinking out loud or showing internal thoughts (e.g., no <think> or system-like responses).

Be short, relevant, and human-like in your reply.

Here is the chat history so far:
{history}

Here is the new incoming message from user {user_id}:
{question}

Give your best response below:
"""

chat_histories = {}
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    question = data.get("message")
    user_id = data.get("user_id", "default_user")
    print(f"Question received: {question}")
    
    if not question:
        return jsonify({"error": "No question provided"}), 400

    history = chat_histories.get(user_id, [])
    history_string = "\n".join(history)
    history.append(f"User: {question}")

    result = chain.invoke({"history": history_string, "question": question, "user_id": user_id})
    clean_result = re.sub(r"<think>.*?</think>", "", result, flags=re.DOTALL).strip()

    history.append(f"Bot: {clean_result}")
    chat_histories[user_id] = history
    print(f"Bot reply: {clean_result}")
    
    return jsonify({"reply": clean_result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
