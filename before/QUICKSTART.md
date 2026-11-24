# 🚀 QUICK START GUIDE

## The app is running! But you need to add your API keys first.

### Step 1: Get Your API Keys

#### OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-...`)

#### Pinecone API Key
1. Go to: https://www.pinecone.io/
2. Sign up for free account
3. Go to "API Keys" in dashboard
4. Copy your API key
5. Note your environment (e.g., `us-east-1`)

### Step 2: Update the .env File

Open `c:\Users\nad\Desktop\ai-training-sources-main\rag_usecase_1\.env`

Replace these lines with your actual keys:

```
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
PINECONE_API_KEY=YOUR_PINECONE_KEY_HERE
PINECONE_ENVIRONMENT=us-east-1
```

### Step 3: Reload the App

1. Go to http://localhost:8501
2. Press `R` or click "Always rerun" when prompted
3. Click "Load Documents" in the sidebar
4. Wait for documents to scrape (~2-3 minutes)
5. Start asking questions!

---

**Example Questions to Try:**
- "What is a rental agreement?"
- "How do I create a power of attorney?"
- "What documents do I need for name change?"

**Need Help?**
- Pinecone free tier: https://www.pinecone.io/pricing/
- OpenAI pricing: https://openai.com/pricing
