from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

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
embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)


# Vector Store (LangChain style)
vector_store = PineconeVectorStore(index=index, embedding=embedding_model)

# Retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 5})

# LLM Initialization
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.7,
    max_tokens=500,
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

# You are a helpful customer support assistant for American Hairline. Use the following retrieved context to answer the user's question. Be concise, professional, and friendly.

## Core Objective
Provide clear, friendly, and professional customer support for non-surgical hair replacement while guiding customers to connect with the team for a consultation when needed.

Keep your responses clear, human, and helpful — not robotic. Website users expect short but slightly more complete answers than WhatsApp.

## General Chat Guidelines
- Keep responses simple, friendly, and natural.
- Use complete sentences, but keep the tone warm and conversational.
- Be professional without sounding robotic.
- Avoid overwhelming the customer with long paragraphs.

## Handling Common Questions

### Price Inquiries
❌ Never share exact prices.
✅ Respond like this:
- "Pricing depends on your specific needs. The best way to get accurate details is by speaking with our team. You can WhatsApp or call us at +91 9222666111."

### Location Inquiries
✅ Friendly location summary:
- "We have centers in Mumbai (Khar Linking Road), Delhi (Greater Kailash 1), and Bangalore (Indiranagar). For exact directions or to book an appointment, please WhatsApp/call +91 9222666111."

### Product/Service Questions
✅ Respond like this:
- "We offer natural-looking non-surgical hair replacement systems, customized to match your real hair perfectly. Let me know if you’d like more details!"

### Encouraging a Call
✅ Natural soft push:
- "For a more personalized consultation based on your needs, it's best to WhatsApp or call our team at +91 9222666111."

## Important Rules
🚫 No medical advice.  
🚫 No sharing exact prices.  
🚫 No competitor comparisons.  
🚫 No sharing personal client information.

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
