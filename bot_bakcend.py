from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from flask import Flask, request, jsonify

llm = OllamaLLM(model="llama3.2")

template = """
You are a WhatsApp bot that can answer questions about any queries.

Here is the question to answer: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    question = data.get("message")  # Changed from "question" to "message" to match your bot's POST data
    print(f"Question received: {question}")
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    chain = prompt | llm
    result = chain.invoke({"question": question})
    return jsonify({"reply": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
