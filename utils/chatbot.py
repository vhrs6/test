import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq 
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

def get_llm(provider, api_key):
    """
    Get the appropriate LLM based on provider and API key.
    
    Args:
        provider (str): The LLM provider name ("Groq", "OpenAI", or "Gemini")
        api_key (str): The API key for the selected provider
        
    Returns:
        LLM: The initialized language model
        
    Raises:
        ValueError: If provider is not supported or if API key is missing
    """
    if not api_key:
        raise ValueError(f"API key is required for {provider}")
        
    if provider == "Groq":
        os.environ["GROQ_API_KEY"] = api_key
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0
        )
    elif provider == "OpenAI":
        os.environ["OPENAI_API_KEY"] = api_key
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0
        )
    elif provider == "Gemini":
        os.environ["GOOGLE_API_KEY"] = api_key
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=0
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

def setup_vectorstore():
    """
    Initializes the Chroma vector store with HuggingFace embeddings.
    """
    persist_directory = "vector_db_dir"
    embeddings = HuggingFaceEmbeddings()
    vectorstore = Chroma(persist_directory=persist_directory,
                         embedding_function=embeddings)
    return vectorstore

def get_prompt_template():
    """
    Creates a structured prompt template for consistent responses.
    """
    system_template = """You are a helpful academic data analysis assistant. Follow these rules strictly:

1. ALWAYS respond in English
2. When discussing scores or marks:
   - If multiple students have the same score, list ALL of them
   - Include their names and USNs for clarity
3. If you are unsure about any information:
   - Clearly state your uncertainty
   - Ask the user to cross-check the data
   - NEVER make assumptions or hallucinate information
4. When analyzing data:
   - Only use the information present in the provided context
   - Cite specific numbers and names from the data
   - Be precise in your comparisons

Context: {context}
Current conversation: {chat_history}
Human: {question}
Assistant: Let me help you with that..."""

    return PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=system_template,
    )

def chat_chain(vectorstore, provider="Groq", api_key=None):
    """
    Creates a conversational retrieval chain for the chatbot.
    """
    llm = get_llm(provider, api_key)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2000})
    memory = ConversationBufferMemory(
        llm=llm,
        output_key="answer",
        memory_key="chat_history",
        return_messages=True
    )
    
    qa_prompt = get_prompt_template()
    
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        memory=memory,
        verbose=True,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": qa_prompt}
    )
    return chain
