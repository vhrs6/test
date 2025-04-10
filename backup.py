import re
import pandas as pd
import streamlit as st
import io
from utils.chatbot import setup_vectorstore, chat_chain
from utils.vector_db import convert_csv_to_vector_db, delete_vector_db

def page2():
    """
    Page 2 of the Streamlit app.
    This page processes student data and provides chatbot interaction.
    """
    # Initialize session state for chatbot
    if "chat_history_p2" not in st.session_state:
        st.session_state.chat_history_p2 = []
    if "vectorstore_p2" not in st.session_state:
        st.session_state.vectorstore_p2 = None
    if "conversationsal_chain_p2" not in st.session_state:
        st.session_state.conversationsal_chain_p2 = None
    if "llm_api_key" not in st.session_state:
        st.session_state.llm_api_key = None
    if "selected_llm" not in st.session_state:
        st.session_state.selected_llm = "Groq"

    # Sidebar for LLM selection and API key
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
            key="embeddings_selector")
        
        if api_key:
            st.session_state.llm_api_key = api_key
            st.session_state.selected_llm = selected_llm
            st.session_state.selected_embeddings = selected_embeddings

    # Main UI
    st.title("Student Data Processor")

    # Editable subject columns
    subject_columns_input = st.text_area(
        placeholder="22MAT41A 22IS42 22IS43 22IS44 22ISL45 22IS464 22ISL474 22ISL473 22UH48 22IS49 22MATDIP41",
        label="Subject Columns (space-separated)",
    )
    if subject_columns_input:
        subject_columns = [col.strip() for col in subject_columns_input.split()]
    else:
        subject_columns = []

    num_subjects = st.number_input("Enter the number of subjects", min_value=0, max_value=50, value=len(subject_columns), step=1)
    warning_messages = []
    if len(subject_columns) != num_subjects:
        warning_messages.append("The number of subjects does not match the defined subject columns. Adjust accordingly.")

    # Text area for student data
    raw_data_input = st.text_area("Paste Student Data (.txt format)")
    space_threshold = st.number_input("Space threshold for splitting chunks", min_value=1, max_value=10, value=5, step=1)
    st.caption("Tweak this value if the chunks are not being split correctly.")

    def clean_tokens(tokens):
        """Splits 5-digit numbers into two tokens."""
        cleaned = []
        for token in tokens:
            if re.match(r'^\d{5}$', token):
                cleaned.append(token[:-3])
                cleaned.append(token[-3:])
            else:
                cleaned.append(token)
        return cleaned

    def group_tokens(tokens):
        """
        Groups tokens by reading until a valid grade is encountered.
        Valid grades include: A+, B+, B, A, O, NE, F, C, PP, P.
        """
        tokens = clean_tokens(tokens)
        valid_grades = {"A+", "B+", "B", "A", "O", "NE", "F", "C", "PP", "P","NP","N","X","I"}
        groups = []
        i = 0
        while i < len(tokens):
            group = []
            while i < len(tokens) and tokens[i] not in valid_grades:
                group.append(tokens[i])
                i += 1
            if i < len(tokens) and tokens[i] in valid_grades:
                group.append(tokens[i])
                i += 1
            groups.append(group)
        return groups

    def get_total_from_group(group):
        """
        Returns the second-last element as the subject total.
        If group is empty or has only one element, returns "NE".
        """
        if not group or len(group) < 2:
            return "NE"
        return group[-2].strip()

    def process_line(line):
        parts = re.split(fr'(\s{{{space_threshold},}})', line.strip())

        if len(parts) < 3:
            warning_messages.append(f"⚠️ Skipping line due to insufficient parts: {line}")
            return None
        
        # Extract USN, Name, and initial subject tokens from parts[0]
        chunk0 = parts[0]
        tokens0 = chunk0.split()
        usn = tokens0[0]
        name_tokens = []
        i = 1
        while i < len(tokens0) and not tokens0[i][0].isdigit():
            name_tokens.append(tokens0[i])
            i += 1
        name = " ".join(name_tokens)
        subject_tokens = tokens0[i:]
        initial_groups = group_tokens(subject_tokens)
        
        # Process remaining parts
        additional_groups = []
        for j in range(1, len(parts) - 1, 2):
            delim = parts[j]
            chunk = parts[j+1]
            if len(delim) >= 5:
                missing_groups = len(delim) // 5
                additional_groups.extend(["NE"] * missing_groups)
            chunk_tokens = chunk.split()
            extra_groups = group_tokens(chunk_tokens)
            additional_groups.extend(extra_groups)
        
        final_subject_groups = initial_groups + additional_groups
        
        # Extract totals
        totals = []
        for g in final_subject_groups:
            if g == "NE":
                totals.append("NE")
            else:
                totals.append(get_total_from_group(g))
        
        while len(totals) < num_subjects:
            totals.append("NE")
        totals = totals[:num_subjects]
        
        # Extract SGPA and CGPA
        remaining_data = parts[-1].split()
        if len(remaining_data) < 2:
            sgpa, cgpa = "NE", "NE"
        else:
            sgpa, cgpa = remaining_data[-2], remaining_data[-1]
        
        return [usn, name] + totals + [sgpa, cgpa]

    # Main Processing
    if raw_data_input:
        raw_data = raw_data_input.splitlines()
        rows = []
        for line in raw_data:
            row = process_line(line)
            if row:
                rows.append(row)
        
        final_columns = ["USN", "Name"] + subject_columns[:num_subjects] + ["SGPA", "CGPA"]
        df = pd.DataFrame(rows, columns=final_columns)
        
        if warning_messages:
            with st.expander("Warnings and Notices"):
                for message in warning_messages:
                    st.write(message)
        
        st.write("### Processed Data:")
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode('utf-8')
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)
        
        st.download_button("Download as CSV", data=csv, file_name="student_data.csv", mime="text/csv")
        st.download_button("Download as Excel", data=excel_buffer, file_name="student_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # Add chatbot interface
        st.divider()
        st.subheader("📚 Documents Chatbot")
        
        if st.button("Load Data into Chatbot"):
            if not st.session_state.llm_api_key:
                st.error(f"Please enter {st.session_state.selected_llm} API key in the sidebar first")
                return
            
            progress_bar_load = st.progress(0)
            progress_text_load = st.empty()
            temp_csv_path = "temp_data_p2.csv"
            df.to_csv(temp_csv_path, index=False)
            st.session_state.vectorstore_p2 = convert_csv_to_vector_db(
    temp_csv_path,
    embeddings_provider=st.session_state.selected_embeddings,
    api_key=st.session_state.llm_api_key,
    progress_bar=progress_bar_load,
    progress_text=progress_text_load
)

            st.session_state.conversationsal_chain_p2 = chat_chain(
                st.session_state.vectorstore_p2,
                provider=st.session_state.selected_llm,
                api_key=st.session_state.llm_api_key
            )
            st.success("Data loaded into chatbot successfully!")

        # Display chat interface
        for message in st.session_state.chat_history_p2:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_input = st.chat_input("Ask AI about the processed data...")
        if user_input and st.session_state.conversationsal_chain_p2:
            st.session_state.chat_history_p2.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                response = st.session_state.conversationsal_chain_p2({"question": user_input})
                assistant_response = response["answer"]
                st.markdown(assistant_response)
                st.session_state.chat_history_p2.append({"role": "assistant", "content": assistant_response})
