# 📚 How to Use This Application

This application has two main features:

1. **Result Fetcher & Chatbot** — Fetch and analyze exam results  
2. **Student Data Processor & Chatbot** — Process and analyze student data

---

## 1️⃣ Result Fetcher & Chatbot

> **Note:** Works **only** when the result server is active within the **college network**.

### 🛠️ Getting Started

1. Enter the year (e.g., `22` for 2022)
2. Select departments from the dropdown
3. Set USN ranges for **regular** and **diploma** students
4. Click **"Fetch Results"** to retrieve data

### 📊 Using the Results

- View results in the displayed table
- Download data in **CSV**, **Excel**, or **PDF** format
- Use the integrated chatbot to ask analytical questions

### 🤖 Chatbot Features

1. Click **"Load Data into Chatbot"** to initialize analysis
2. Example questions:
   - Who scored the highest SGPA?
   - How many students scored above 8.5?
   - Compare performance between departments

---

## 2️⃣ Student Data Processor & Chatbot

### 🔄 Data Processing Steps

1. Edit subject column names (space-separated)
2. Adjust the number of subjects
3. Paste student data (raw text format)
4. Set **space threshold** if data parsing seems off

### 📤 Using Processed Data

- Review parsed data in the table
- Download in **CSV** or **Excel**
- Ask questions using the chatbot

### 📌 Tips for Data Formatting

- Each line should contain: `USN`, `Name`, `Subject scores`, `SGPA`, `CGPA`
- Maintain consistent spacing between data chunks
- Address warnings for improperly formatted lines

---

## 🤖 Using the Chatbot

### 🌐 Selecting LLM Provider

1. In the sidebar, select your provider:
   - Groq
   - OpenAI
   - Gemini
2. Enter your **API key**

### 🔑 Getting API Keys

- **Groq**: [https://console.groq.com](https://console.groq.com)  
- **OpenAI**: [https://platform.openai.com](https://platform.openai.com)  
- **Gemini**: [https://makersuite.google.com](https://makersuite.google.com)

### ✅ Best Practices

- Always **load the data** before querying
- Ask **specific** and well-structured questions
- Include comparison criteria explicitly
- Reconfirm data if the chatbot seems unsure

### 💬 Example Prompts

- List all students who scored above 90 in Mathematics
- Compare performance between subjects
- Who are the top performers in each subject?
- Show students with same scores in any subject

---

## ⚠️ Troubleshooting

### Common Issues & Fixes

#### 🔹 Data Not Loading

- Check internet connection
- Verify API key
- Reformat your input data

#### 🔹 Incorrect Data Processing

- Adjust space threshold
- Ensure correct subject headers
- Validate the student data format

#### 🔹 Chatbot Issues

- Reload data before querying again
- Switch to a different LLM provider
- Clear chat history and retry

---

## 📌 Additional Resources

- Expandable sections in the app show **warnings**
- Refer to official documentation for **API rate limits**
- Contact **support** if issues persist

---
