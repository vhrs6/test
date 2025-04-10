import streamlit as st

def how_to_use_page():
    """
    Help page that explains how to use the application.
    """
    st.title("📚 How to Use This Application")
    
    # Overview
    st.markdown("""
    This application has two main features:
    1. **Result Fetcher & Chatbot**: Fetch and analyze exam results
    2. **Student Data Processor & Chatbot**: Process and analyze student data
    """)
    
    # Page 1 Guide
    st.header("1️⃣ Result Fetcher & Chatbot")
    st.caption("WORKS ONLY WHEN THE RESULT SERVER IS ACTIVE IN THE COLLEGE NETWORK")

    st.markdown("""
    #### Getting Started
    1. Enter the year (e.g., 22 for 2022)
    2. Select departments from the dropdown
    3. Set USN ranges for regular and diploma students
    4. Click "Fetch Results" to retrieve data
    
    #### Using the Results
    - View results in the displayed table
    - Download data in CSV, Excel, or PDF format
    - Use the chatbot to analyze results
    
    #### Chatbot Features
    1. Click "Load Data into Chatbot" to prepare the data
    2. Ask questions about the results, such as:
       - "Who scored the highest SGPA?"
       - "How many students scored above 8.5?"
       - "Compare performance between departments"
    """)
    
    # Page 2 Guide
    st.header("2️⃣ Student Data Processor & Chatbot")
    st.markdown("""
    #### Data Processing
    1. Edit subject columns if needed (space-separated)
    2. Adjust the number of subjects
    3. Paste student data in text format
    4. Adjust space threshold if needed
    
    #### Using Processed Data
    - Review the processed data table
    - Download in CSV or Excel format
    - Use the chatbot for analysis
    
    #### Tips for Data Format
    - Each line should contain: USN, Name, Subject scores, SGPA, CGPA
    - Ensure proper spacing between data chunks
    - Check warnings if any data is not properly processed
    """)
    
    # Chatbot Guide
    st.header("🤖 Using the Chatbot")
    st.markdown("""
    #### Selecting LLM Provider
    1. Use the sidebar to select your preferred provider:
       - Groq
       - OpenAI
       - Gemini
    2. Enter the corresponding API key
    
    #### Getting API Keys
    - **Groq**: Sign up at https://console.groq.com
    - **OpenAI**: Get key from https://platform.openai.com
    - **Gemini**: Generate key at https://makersuite.google.com
    
    #### Best Practices
    1. Always load data before asking questions
    2. Be specific in your questions
    3. For comparisons, mention specific criteria
    4. Cross-check data when the chatbot expresses uncertainty
    
    #### Example Questions
    - "List all students who scored above 90 in Mathematics"
    - "Compare performance between subjects"
    - "Who are the top performers in each subject?"
    - "Show students with same scores in any subject"
    """)
    
    # Troubleshooting
    st.header("⚠️ Troubleshooting")
    st.markdown("""
    #### Common Issues
    1. **Data Not Loading**
       - Check internet connection
       - Verify API key is correct
       - Ensure data format is proper
    
    2. **Incorrect Data Processing**
       - Adjust space threshold
       - Check subject column names
       - Verify input data format
    
    3. **Chatbot Issues**
       - Reload data if responses are incorrect
       - Try a different LLM provider
       - Clear chat history and start fresh
    """)
    
    # Additional Resources
    st.header("📌 Additional Resources")
    st.markdown("""
    - Use the expander sections for detailed warnings
    - Check documentation for API usage limits
    - Contact support for persistent issues
    """)
