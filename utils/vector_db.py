import tempfile
import shutil
import os
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Global variable to store the temporary directory
temp_vector_db_dir = None

def convert_csv_to_vector_db(csv_file_path, embeddings_provider="huggingface", api_key=None, progress_bar=None, progress_text=None):
    """
    Converts a CSV file into a vector database using Chroma.
    Args:
        csv_file_path (str): Path to the CSV file.
        progress_bar (streamlit.progress): Streamlit progress bar object.
        progress_text (streamlit.empty): Streamlit placeholder for progress percentage.
    Returns:
        Chroma: Vector database object.
    """
    global temp_vector_db_dir

    # Create a temporary directory for the vector database
    temp_vector_db_dir = tempfile.mkdtemp()

    # Load CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file_path)

    # Combine all columns into a single "content" column
    df["content"] = df.apply(lambda row: ", ".join([f"{col}: {row[col]}" for col in df.columns]), axis=1)

    # Use DataFrameLoader to process the data
    loader = DataFrameLoader(df, page_content_column="content")
    documents = loader.load()

    # Update progress bar (10% completion)
    if progress_bar and progress_text:
        progress_bar.progress(0.1)
        progress_text.text("Progress: 10%")

    # Split documents into smaller chunks for better embedding
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0, separators=["\n"])
    text_chunks = text_splitter.split_documents(documents)

    # Update progress bar (30% completion)
    if progress_bar and progress_text:
        progress_bar.progress(0.3)
        progress_text.text("Progress: 30%")

    # Load the embedding model based on provider
    if embeddings_provider == "Huggingface":
        embeddings = HuggingFaceEmbeddings()
    elif embeddings_provider == "Gemini":
        if not api_key:
            raise ValueError("API key required for Gemini embeddings")
        os.environ["GOOGLE_API_KEY"] = api_key
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    elif embeddings_provider == "OpenAI":
        if not api_key:
            raise ValueError("API key required for OpenAI embeddings")
        os.environ["OPENAI_API_KEY"] = api_key
        embeddings = OpenAIEmbeddings(model="OpenAIEmbeddings")
    else:
        raise ValueError(f"Unsupported embeddings provider: {embeddings_provider}")

    # Update progress bar (50% completion)
    if progress_bar and progress_text:
        progress_bar.progress(0.5)
        progress_text.text("Progress: 50%")

    # Store vectorized data in ChromaDB
    vectordb = Chroma.from_documents(
        documents=text_chunks,
        embedding=embeddings,
        persist_directory=temp_vector_db_dir
    )

    # Update progress bar (100% completion)
    if progress_bar and progress_text:
        progress_bar.progress(1.0)
        progress_text.text("Progress: 100%")

    print("✅ CSV Data Vectorized Successfully")
    print(f"Total students processed: {len(documents)}")
    return vectordb

def delete_vector_db():
    """
    Deletes the vector database directory.
    """
    global temp_vector_db_dir
    if temp_vector_db_dir and os.path.exists(temp_vector_db_dir):
        # Delete the directory
        shutil.rmtree(temp_vector_db_dir)
        print(f"✅ Vector database directory {temp_vector_db_dir} deleted successfully!")
    else:
        print(f"❌ Vector database directory does not exist.")
