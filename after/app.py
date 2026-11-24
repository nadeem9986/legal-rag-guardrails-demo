import streamlit as st
from dotenv import load_dotenv
import os
import sys
import time

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main_pipeline import RAGPipeline
from src import guardrails as G

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Legal AI Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PREMIUM ORANGE DYNAMIC UI BLEND ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&family=Outfit:wght@400;600&display=swap');
    
    :root {
        --primary: #FF8C00; /* Legal Orange */
        --primary-gradient: linear-gradient(135deg, #FF8C00 0%, #E65100 100%);
        --surface: rgba(255, 255, 255, 0.04);
        --border: rgba(255, 255, 255, 0.08);
        --bg: #0A0A0C;
    }

    /* Seamless Background Blend with Orange Accents */
    .stApp {
        background: var(--bg) !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(255, 140, 0, 0.05) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(230, 81, 0, 0.05) 0px, transparent 50%) !important;
    }

    * { font-family: 'SF Pro Display', 'Inter', sans-serif; -webkit-font-smoothing: antialiased; }

    #MainMenu, footer, header { visibility: hidden; }

    /* Unified Header */
    .header-blend {
        padding: 3rem 1rem;
        text-align: center;
        background: linear-gradient(to bottom, rgba(255,255,255,0.02), transparent);
        border-radius: 0 0 40px 40px;
        margin-bottom: 2rem;
    }

    .header-blend h1 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        font-size: 2.8rem !important;
        letter-spacing: -1px !important;
        background: linear-gradient(180deg, #FFFFFF 0%, #FFB74D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(30px) !important;
        border-right: 1px solid var(--border) !important;
    }

    /* --- DYNAMIC ORANGE CHAT BUBBLES --- */
    .user-message {
        background: var(--primary-gradient) !important;
        color: white !important;
        padding: 0.8rem 1.2rem !important;
        border-radius: 20px 20px 4px 20px !important;
        margin-left: auto !important;
        width: fit-content !important; 
        max-width: 70% !important;
        box-shadow: 0 8px 20px rgba(255, 140, 0, 0.15);
        word-wrap: break-word;
    }

    .ai-message {
        background: var(--surface) !important;
        backdrop-filter: blur(10px);
        color: #E2E2E2 !important;
        padding: 1rem 1.4rem !important;
        border-radius: 20px 20px 20px 4px !important;
        margin-right: auto !important;
        width: fit-content !important; 
        max-width: 80% !important;
        border: 1px solid var(--border) !important;
        line-height: 1.6;
        word-wrap: break-word;
    }

    /* --- DYNAMIC EXPANDER BOX --- */
    [data-testid="stExpander"] {
        background: transparent !important;
        border: none !important;
        width: fit-content !important;
        max-width: 100%;
        margin-top: 5px !important;
    }

    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--primary) !important; /* Orange text for Sources */
        padding: 0.4rem 0.8rem !important;
        font-size: 0.85rem !important;
        width: fit-content !important;
    }
    
    /* guardrails demo: make the expander labels readable on the dark theme */
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary p {
        color: #f0f0f0 !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stExpander"] details > div, [data-testid="stExpander"] details > div * { color: #e6e6e6 !important; }
    [data-testid="stExpander"] summary { border: 1px solid rgba(255,255,255,0.35) !important; border-radius: 10px !important; }

    .source-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.8rem;
        margin-top: 0.5rem;
    }

    /* Form & UI Elements Accents */
    .stMetric { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 20px !important; }
    
    .stButton>button { 
        background: var(--surface) !important; 
        border: 1px solid var(--border) !important; 
        color: white !important; 
        border-radius: 12px !important; 
        transition: all 0.2s ease !important; 
    }
    
    .stButton>button:hover { 
        background: var(--primary-gradient) !important; 
        border-color: var(--primary) !important; 
        box-shadow: 0 0 20px rgba(255, 140, 0, 0.3); 
    }

    .stTextInput input { 
        background: rgba(255, 255, 255, 0.05) !important; 
        border: 1px solid var(--border) !important; 
        border-radius: 14px !important; 
        color: white !important; 
    }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- CORE LOGIC (ALL FEATURES PRESERVED) ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = None
if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False
if 'num_documents' not in st.session_state:
    st.session_state.num_documents = 0
if 'num_chunks' not in st.session_state:
    st.session_state.num_chunks = 0

def initialize_pipeline():
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
    
    if not all([openai_key, pinecone_key, pinecone_env]):
        st.error("⚠️ API Keys Missing in .env")
        return None
    
    try:
        return RAGPipeline(openai_api_key=openai_key, pinecone_api_key=pinecone_key, pinecone_environment=pinecone_env)
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

def main():
    st.markdown("""
        <div class="header-blend">
            <h1>⚖️ Legal Intel</h1>
            <p style="color: #8E8E93; font-size: 1rem;">Intelligent Document Analysis in a Unified Space</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 📚 Management")
        if st.button("🔄 Sync Documents", use_container_width=True):
            with st.spinner("Processing..."):
                st.session_state.pipeline = initialize_pipeline()
                if st.session_state.pipeline:
                    if st.session_state.pipeline.load_existing_vector_store():
                        stats = st.session_state.pipeline.get_stats()
                        total_vectors = stats.get('index_stats', {}).get('total_vector_count', 0)
                        st.session_state.num_documents = max(1, total_vectors // 15)
                        st.session_state.num_chunks = total_vectors
                        st.session_state.documents_loaded = True
                        st.rerun()

        if st.session_state.documents_loaded:
            c1, c2 = st.columns(2)
            c1.metric("Files", st.session_state.num_documents)
            c2.metric("Chunks", st.session_state.num_chunks)
        
        st.markdown("---")
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
            
        st.markdown("### ⚙️ Settings")
        st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, 0.3)

    if st.session_state.documents_loaded:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                _u = G.esc(message["content"]) if G.B2_SAFE_RENDER else message["content"]
                st.markdown(f'<div class="user-message">{_u}</div>', unsafe_allow_html=True)
            else:
                _a = G.esc(message["content"]) if G.B2_SAFE_RENDER else message["content"]
                st.markdown(f'<div class="ai-message">{_a}</div>', unsafe_allow_html=True)
                if message.get('trace'):
                    with st.expander("🛡️ Checks that ran"):
                        for t in message['trace']:
                            st.markdown(f"**{t['step']}**: {G.esc(t['detail'])}", unsafe_allow_html=True)
                
                if message.get('sources'):
                    with st.expander("📎 View Sources"):
                        unique_sources = []
                        seen_urls = set()
                        for s in message['sources']:
                            if s['url'] not in seen_urls:
                                unique_sources.append(s)
                                seen_urls.add(s['url'])
                        
                        for source in unique_sources:
                            if G.B2_SAFE_RENDER:
                                _t, _c, _href = G.esc(source['title']), G.esc(source['category']), G.safe_url(source['url'])
                            else:
                                _t, _c, _href = source['title'], source['category'], source['url']
                            _link = (f'<a href="{G.esc(_href) if G.B2_SAFE_RENDER else _href}" target="_blank" style="color:#FF8C00; text-decoration:none;">Open Document →</a>'
                                     if _href else '<small>Link hidden (not an https legaldesk.com page)</small>')
                            st.markdown(f"""
                                <div class="source-card">
                                    <strong>{_t}</strong><br>
                                    <small>{_c}</small><br>
                                    {_link}
                                </div>
                            """, unsafe_allow_html=True)

        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([6, 1])
            user_input = col1.text_input("Query", placeholder="Ask anything about the documents...", label_visibility="collapsed")
            if col2.form_submit_button("🚀") and user_input:
                if G.B3_INPUT_LIMITS and len(user_input) > G.MAX_QUESTION_CHARS:
                    st.warning(f"Please keep your question under {G.MAX_QUESTION_CHARS} characters.")
                    st.stop()
                st.session_state.chat_history.append({'role': 'user', 'content': user_input})
                
                system_keywords = ['who are you', 'what are you', 'who might u be', 'your name', 'about you']
                if any(k in user_input.lower() for k in system_keywords):
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': "I am your Legal AI Assistant. I can help you analyze legal documents, explain affidavits, and guide you through legal procedures based on the documents I've synced. How can I help you today?",
                        'sources': []
                    })
                    st.rerun()
                else:
                    with st.spinner("Thinking..."):
                        response = st.session_state.pipeline.query(user_input, temperature=st.session_state.temperature)
                        st.session_state.chat_history.append({
                            'role': 'assistant', 
                            'content': response['answer'], 
                            'sources': response['sources'],
                            'trace': response.get('trace', [])
                        })
                    st.rerun()
    else:
        st.info("👋 Welcome. Please click **Sync Documents** to begin.")

if __name__ == "__main__":
    main()
