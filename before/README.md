# ⚖️ Legal Document AI Assistant

A high-end, production-ready **RAG (Retrieval-Augmented Generation)** chatbot designed for mission-critical legal intelligence. This system scrapes verified legal documents from [legaldesk.com](https://legaldesk.com), processes them into a semantic vector database, and provides an intelligent, context-aware Q&A interface with a premium **Glassmorphism** design.

---

## ✨ Key Features
- 🔍 **Intelligent Web Scraping**: Sophisticated scraper that extracts structured content and metadata from legal document repositories.
- 🧠 **Dynamic RAG Pipeline**: Orchestrated workflow using **LangChain**, **OpenAI Embeddings**, and **Pinecone** for high-precision retrieval.
- 🌡️ **Temperature Control**: Sidebar slider to toggle between **Factual (Low Temp)** and **Creative (High Temp)** AI responses.
- 📎 **Verified Sources**: Every answer includes direct links to the original legal documents for verification.
- 🛡️ **Meta-Query Handling**: Built-in logic to handle questions about the AI itself without querying the document database.

---

## 🛠️ How it Works (The Pipeline)

### 1. Document Extraction (Scraping)
The system uses `src/utils/scraper.py` (BeautifulSoup4 + html2text) to traverse document categories. It extracts:
- Document Title
- Cleaned Markdown Content
- Category & Source URL

### 2. Processing & Chunking
`src/models/document_processor.py` takes the raw text and breaks it into semantic chunks (using `RecursiveCharacterTextSplitter`). This ensures that context is preserved while remaining within the LLM's token limits.

### 3. Vectorization & Storage
Chunks are converted into 1536-dimensional embeddings using `text-embedding-3-small`. These are stored in a **Pinecone Serverless Index** with comprehensive metadata (title, category, url) to enable filtered retrieval.

### 4. Semantic Retrieval
When you ask a question, the system:
1. Generates an embedding for your query.
2. Performs a similarity search in Pinecone to find the most relevant document chunks.
3. Filters results based on relevance scores.

### 5. AI Reasoning (RAG)
The retrieved chunks are passed as "Context" to **GPT-3.5-turbo** (or GPT-4) along with your question. The AI is strictly instructed to only answer using the provided context, ensuring factual accuracy.

---

## 🚀 Installation & Setup

### 1. Requirements
- Python 3.8+
- OpenAI API Key
- Pinecone API Key & Environment

### 2. Setup Procedure
```bash
# Clone and enter directory
git clone https://github.com/nadeem9986/legal-ai-rag-assistant.git
cd legal-ai-rag-assistant

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file from the provided example:
```env
OPENAI_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=your_region_here
PINECONE_INDEX_NAME=legal-documents
```

---

## 📖 Application Modes

### 📥 First Run: Scrape & Index
Click **"Load Documents"** in the sidebar. This will trigger the full pipeline to scrape documents, generate embeddings, and create your Pinecone index.

### 💬 Query Mode
Once "Ready", simply type your question in the chat bar.
- Use the **Temperature Slider** to adjust response style.
- Click **"View Sources"** below any AI response to see the reference documents.
- Use **"Clear Chat"** to reset the conversation.

---

## 🏗️ Technical Architecture

```
rag_usecase_1/
├── app.py                  # Premium UI & Streamlit logic
├── src/
│   ├── main_pipeline.py    # Master Orchestrator
│   ├── utils/
│   │   └── scraper.py      # BeautifulSoup extraction
│   └── models/
│       ├── doc_processor.py # Text chunking logic
│       └── rag_engine.py    # Pinecone/OpenAI integration
├── requirements.txt         # Core dependencies
└── .env                    # System secrets
```

---

## 🎨 design Principles
This app follows **Modern UI Standards**:
- **Typography**: Outfit (Headings) and Inter (Body) fonts.
- **Feedback**: Smooth slide-in animations for chat bubbles.
- **Accessibility**: High-contrast dark theme for readability.

---
