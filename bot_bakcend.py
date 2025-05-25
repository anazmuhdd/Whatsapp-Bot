from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from flask import Flask, request, jsonify

llm = OllamaLLM(model="llama3.2")

template = """
You are a WhatsApp bot that can answer questions about various topics in a continous chat.
You are a helpful assistant that provides concise and accurate answers to user questions.
there are historie sprovided you to about previuos chats.if chats are not provided, you can answer the question based on your knowledge.
if chats are procided, you can use them to answer the question more accurately.
here is the chat history:
{history}
Here is the question to answer: {question}
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
    history.append(f"Bot: {result}")
    chat_histories[user_id] = history
    print(f"Bot reply: {result}")
    return jsonify({"reply": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
