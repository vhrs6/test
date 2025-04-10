__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import atexit
import streamlit as st
import os
import pandas as pd
from utils.fetch_results import fetch_results
from utils.file_handling import save_to_csv, delete_temp_file, create_pdf_from_dataframe
from utils.vector_db import convert_csv_to_vector_db, delete_vector_db
from utils.chatbot import setup_vectorstore, chat_chain
from io import BytesIO
from backup import page2


def page1():
    """
    Page 1 of the Streamlit app.
    This page allows users to fetch exam results, display them, and interact with a chatbot.
    """
    # Initialize session state
    if 'all_results' not in st.session_state:
        st.session_state.all_results = None
    if 'sorted_column' not in st.session_state:
        st.session_state.sorted_column = 'USN'
    if 'sort_ascending' not in st.session_state:
        st.session_state.sort_ascending = True
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "conversationsal_chain" not in st.session_state:
        st.session_state.conversationsal_chain = None
    if "temp_csv_path" not in st.session_state:
        st.session_state.temp_csv_path = None
    if "llm_api_key" not in st.session_state:
        st.session_state.llm_api_key = None
    if "selected_llm" not in st.session_state:
        st.session_state.selected_llm = "Groq"
    if "selected_embeddings" not in st.session_state:
        st.session_state.selected_embeddings = "Huggingface"

    # Cleanup function
    # Sidebar for LLM and embeddings selection
    with st.sidebar:
        st.title("🤖 Chatbot Settings")
        selected_llm = st.selectbox(
            "Select LLM Provider",
            ["Groq", "OpenAI", "Gemini"],
            key="llm_selector"
        )
        api_key = st.text_input(
            f"Enter {selected_llm} API Key",
            type="password",
            key="api_key_input"
        )
        selected_embeddings = st.selectbox(
            "Select Embeddings Provider",
            ["Huggingface", "Gemini","OpenAI"],
            key="embeddings_selector"
        )
        embedding_api_key = st.text_input(
            f"Enter {selected_llm} API Key",
            type="password",
            key="embedding_key_input"
        )
        if api_key:
            st.session_state.llm_api_key = api_key
            st.session_state.selected_llm = selected_llm
            st.session_state.selected_embeddings = selected_embeddings
            st.session_state.embedding_api_key = embedding_api_key

    def cleanup():
        """
        Cleans up temporary files and directories.
        """
        if st.session_state.temp_csv_path and os.path.exists(st.session_state.temp_csv_path):
            delete_temp_file(st.session_state.temp_csv_path)
        if st.session_state.vectorstore:
            st.session_state.vectorstore.delete_collection()
            delete_vector_db()
        print("✅ Cleanup completed.")

    # Register cleanup function for normal program exit
    atexit.register(cleanup)

    # Streamlit App
    # st.set_page_config(page_title="DSCE Exam Result Fetcher & Chatbot", layout="wide")
    st.title("DSCE Exam Result Fetcher & Chatbot")
    st.caption("WORKS ONLY WHEN THE RESULT SERVER IS ACTIVE IN THE COLLEGE NETWORK")


    # User Inputs
    year = st.number_input("Enter Year (e.g., 22 for 2022)", min_value=10, max_value=99, value=22, step=1)
    branches = ["CS", "CY", "ME", "ET", "EI", "EC", "IS", "IM", "AU", "EE","BT"]
    selected_branches = st.multiselect("Select Departments", branches, default=["CS"])
    usn_range = st.slider("Select USN Range", 1, 500, (1, 10))
    diploma_usn_range = st.slider("Select Diploma USN Range", 400, 500, (400, 410))
    selected_branches = [b.lower() for b in selected_branches]

    col1, buff, col2 = st.columns([1, 0.1, 1])
    with col1:
        # Fetch Results
        if st.button("Fetch Results"):
            st.write("Fetching results, please wait...")
            progress_bar = st.progress(0)
            progress_text = st.empty()  # Placeholder for progress percentage
            all_results = fetch_results(year, selected_branches, usn_range, diploma_usn_range, progress_bar, progress_text)
            if all_results:
                st.session_state.all_results = all_results
                # Save fetched data to a temporary CSV file
                st.session_state.temp_csv_path = save_to_csv(all_results)
                st.success("Results fetched and saved to temporary CSV successfully!")
            else:
                st.error("No valid results found!")

        # Display Results
        if st.session_state.all_results is not None:
            df = pd.DataFrame(st.session_state.all_results, columns=["USN", "Name", "SGPA"])
            st.subheader("Fetched Results")
            st.dataframe(df, hide_index=True)

            # Download Data
            st.subheader("Download Data")
            download_format = st.selectbox("Select download format", ["CSV", "Excel", "PDF"])
            if download_format == "CSV":
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", data=csv_data, file_name="exam_results.csv", mime="text/csv")
            elif download_format == "Excel":
                excel_data = BytesIO()
                with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name="Results")
                excel_data.seek(0)
                st.download_button("Download Excel", data=excel_data, file_name="exam_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            elif download_format == "PDF":
                pdf_buffer = create_pdf_from_dataframe(df)
                st.download_button("Download PDF", data=pdf_buffer, file_name="exam_results.pdf", mime="application/pdf")

            # Load Data into Chatbot
            if st.button("Load Data into Chatbot"):
                if st.session_state.all_results is not None:
                    progress_bar_load = st.progress(0)
                    progress_text_load = st.empty()  # Placeholder for progress percentage
                    if not st.session_state.llm_api_key:
                        st.error(f"Please enter {st.session_state.selected_llm} API Key in the sidebar first")
                        return
                    
                    st.session_state.vectorstore = convert_csv_to_vector_db(
                        st.session_state.temp_csv_path,
                        embeddings_provider=st.session_state.selected_embeddings,
                        api_key=st.session_state.embedding_api_key,
                        progress_bar=progress_bar_load,
                        progress_text=progress_text_load
                    )
                    st.session_state.conversationsal_chain = chat_chain(
                        st.session_state.vectorstore,
                        provider=st.session_state.selected_llm,
                        api_key=st.session_state.llm_api_key
                    )
                    st.success("Data loaded into chatbot successfully!")
                else:
                    st.error("No data fetched yet. Please fetch data first.")
    with col2:
        # Chatbot Interface
        st.subheader("📚 Documents Chatbot")
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_input = st.chat_input("Ask AI...")
        if user_input and st.session_state.conversationsal_chain:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                response = st.session_state.conversationsal_chain({"question": user_input})
                assistant_response = response["answer"]
                st.markdown(assistant_response)
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

from how_to_use import how_to_use_page

pg = st.navigation([
    st.Page(how_to_use_page, title="How to Use", icon="📚"),
    st.Page(page1, title="Result Fetcher", icon="🔍"),
    st.Page(page2, title="Student Data Processor", icon="⚙️"),
])
pg.run()
