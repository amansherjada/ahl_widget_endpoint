from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

from langchain_pinecone import PineconeVectorStore
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain

from pinecone import Pinecone

# -------------------------------------
# Load Environment Variables
# -------------------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# -------------------------------------
# Initialize Flask App
# -------------------------------------
app = Flask(__name__)
CORS(app)

# -------------------------------------
# Initialize Services
# -------------------------------------

# Pinecone Initialization
pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
index = pc.Index(PINECONE_INDEX_NAME)

# HuggingFace Embeddings
embedding_model = HuggingFaceEmbeddings()

# Vector Store (LangChain style)
vector_store = PineconeVectorStore(index=index, embedding=embedding_model)

# Retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# LLM Initialization
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.7,
    max_tokens=300,
)

# -------------------------------------
# Main Response Generator
# -------------------------------------

def generate_response(query, language):
    try:
        # Step 1: Search documents
        documents = retriever.get_relevant_documents(query)

        # Step 2: Merge contexts
        contexts = [doc.page_content for doc in documents]
        context_text = "\n\n".join(contexts) if contexts else "No relevant information found."

        # Step 3: Conversation History (optional future extension)
        conversation_history = ""

        # Step 4: Professional Prompt
        system_prompt_template = """
        American Hairline Website Customer Support AI Assistant

        ## Core Objective
        Provide clear, friendly, and professional customer support for non-surgical hair replacement while guiding customers to connect with the team for a call.

        ## Chat Guidelines
        - Keep it simple, short, and natural.
        - Make the conversation feel human, not robotic.
        - Never share exact prices or medical advice.
        - Always encourage customer to call/WhatsApp +91 9222666111.
        - Avoid long boring paragraphs.

        ## Handling Common Topics
        - If asked about pricing: "Pricing depends on your needs. Please WhatsApp/call +91 9222666111."
        - If asked about locations: Provide friendly location summary + suggest WhatsApp.
        - If asked about products: Briefly say "We offer natural-looking non-surgical hair replacement" and suggest to WhatsApp.

        ## Must-Do
        - End every reply softly suggesting to call/WhatsApp the team.
        - Use retrieved context only when relevant.

        Retrieved context:
        {context}

        Conversation history:
        {conversation_history}

        User's current question: {question}

        Final Answer:
        """

        # Step 5: Build Prompt
        prompt = PromptTemplate(
            template=system_prompt_template,
            input_variables=["context", "conversation_history", "question"]
        )

        # Step 6: Load QA Chain
        qa_chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)

        # Step 7: Run LLM
        result = qa_chain({
            "input_documents": documents,
            "context": context_text,
            "conversation_history": conversation_history,
            "question": query,
        })

        return result["output_text"]

    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, I couldn't process your request right now."

# -------------------------------------
# Chat API Endpoint
# -------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    query = data.get('query')  # (Optional)
    language = data.get('language', 'english')  # Default

    if not query:
        return jsonify({"response": "Please send a valid message."})

    response_text = generate_response(query, language)

    return jsonify({"response": response_text})

# -------------------------------------
# Run Flask App
# -------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
