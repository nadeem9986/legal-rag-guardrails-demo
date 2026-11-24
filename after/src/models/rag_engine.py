"""
RAG Engine with Pinecone vector database
Handles embeddings, storage, and retrieval
"""

from typing import List, Dict
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
import time
from src import guardrails as G


class PineconeRAGEngine:
    """
    RAG engine using Pinecone vector database with langchain-pinecone
    """
    
    def __init__(
        self,
        openai_api_key: str,
        pinecone_api_key: str,
        pinecone_environment: str,
        index_name: str = "legal-documents",
        model_name: str = "gpt-3.5-turbo"
    ):
        """
        Initialize RAG engine with Pinecone
        """
        self.openai_api_key = openai_api_key
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_environment = pinecone_environment
        self.index_name = index_name
        self.model_name = model_name
        
        # Set API keys in environment
        os.environ["OPENAI_API_KEY"] = openai_api_key
        os.environ["PINECONE_API_KEY"] = pinecone_api_key
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=openai_api_key
        )
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=pinecone_api_key)
        
        self.vector_store = None
    
    def create_index(self, dimension: int = 1536, metric: str = "cosine"):
        """Create Pinecone index if it doesn't exist"""
        try:
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                print(f"Creating Pinecone index: {self.index_name}")
                
                self.pc.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric=metric,
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                
                # Wait for index to be ready
                while not self.pc.describe_index(self.index_name).status['ready']:
                    time.sleep(1)
                
                print(f"Index {self.index_name} created successfully")
            else:
                print(f"Index {self.index_name} already exists")
                
        except Exception as e:
            print(f"Error creating index: {e}")
            raise
    
    def store_documents(self, chunks: List[Dict]):
        """Store document chunks in Pinecone using langchain-pinecone"""
        try:
            print(f"Storing {len(chunks)} chunks in Pinecone...")
            
            # Prepare texts and metadatas
            texts = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            
            # Create vector store using langchain-pinecone
            self.vector_store = PineconeVectorStore.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas,
                index_name=self.index_name
            )
            
            print(f"Successfully stored {len(chunks)} chunks in Pinecone")
            
        except Exception as e:
            print(f"Error storing documents: {e}")
            raise
    
    def load_existing_index(self):
        """Load existing Pinecone index"""
        try:
            print(f"Loading existing index: {self.index_name}")
            
            self.vector_store = PineconeVectorStore(
                index_name=self.index_name,
                embedding=self.embeddings
            )
            
            print("Index loaded successfully")
            return True
            
        except Exception as e:
            print(f"Error loading index: {e}")
            return False
    
    def query(self, question: str, k: int = 3, temperature: float = 0.3) -> Dict:
        """
        Query the RAG system
        
        Args:
            question: User question
            k: Number of documents to retrieve
            temperature: LLM temperature (0.0-1.0, lower = more factual)
            
        Returns:
            Dictionary with answer and sources
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Load or create index first.")
        
        trace = []   # what each check decided, shown in the UI and the comparison
        try:
            # Search for relevant documents
            results = self.vector_store.similarity_search_with_score(question, k=k)
            trace.append({"step": "retrieve", "detail": f"{len(results)} chunks, scores " + ", ".join(f"{float(sc):.3f}" for _, sc in results)})

            if G.A2_RELEVANCE_BAR:
                kind = getattr(self, "score_kind", "similarity")
                seen, kept = set(), []
                for doc, sc in results:
                    if doc.page_content in seen:
                        trace.append({"step": "dedupe", "detail": "dropped a duplicate chunk"})
                        continue
                    seen.add(doc.page_content)
                    if not G.score_ok(float(sc), kind):
                        trace.append({"step": "relevance bar", "detail": f"dropped chunk with score {float(sc):.3f} ({kind}, {'lower' if kind == 'distance' else 'higher'} is closer)"})
                        continue
                    kept.append((doc, sc))
                results = kept
                if not results:
                    trace.append({"step": "refuse", "detail": "nothing passed the bar: fixed reply, model not called, no source links"})
                    return {"answer": G.NO_ANSWER, "sources": [], "trace": trace}
            elif not results:
                return {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": [], "trace": trace
                }

            # Extract context from results
            context = "\n\n".join([doc.page_content for doc, _ in results])

            if G.B5_WEAK_SIGNAL_LOGS:
                for sig in G.weak_signals(context, question):
                    print("WEAK SIGNAL (logged, not blocked):", sig)
                    trace.append({"step": "weak signal (log only)", "detail": sig})

            model_with_temp = self.llm.bind(temperature=temperature)
            if G.B1_PROMPT_SEPARATION:
                from langchain_core.messages import SystemMessage, HumanMessage
                messages = [
                    SystemMessage(content=G.SYSTEM_RULES),
                    HumanMessage(content=(
                        "<reference_text>\n" + context + "\n</reference_text>\n\n"
                        "<question>\n" + question + "\n</question>"
                    )),
                ]
                trace.append({"step": "prompt", "detail": "rules in a system message; reference text and question in labelled blocks"})
                response = model_with_temp.invoke(messages)
            else:
                # Create prompt with human-like persona (original behaviour: one string)
                prompt = f"""You are a helpful and professional Legal AI Assistant. 
Your goal is to provide clear, conversational, and "human-like" answers based on the legal document segments provided below.

INSTRUCTIONS:
1. Be direct but empathetic. 
2. If the user is asking for help with a specific document (like an Affidavit), explain the general steps or purpose as found in the text.
3. Do not just say "use the template on the website." Instead, describe what the document is for and what information it typically requires.
4. If you cannot find the answer in the provided documents, politely state that you don't have that specific information.
5. Avoid being overly repetitive or robotic.

CONTEXT FROM LEGAL DOCUMENTS:
{context}

USER QUESTION: {question}

HELPFUL RESPONSE:"""
                trace.append({"step": "prompt", "detail": "single string (original)"})
                response = model_with_temp.invoke(prompt)
            answer = response.content

            if G.B5_WEAK_SIGNAL_LOGS:
                for sig in G.weak_signals(context, question, answer):
                    if sig.startswith("answer has URL"):
                        print("WEAK SIGNAL (logged, not blocked):", sig)
                        trace.append({"step": "weak signal (log only)", "detail": sig})

            # Format sources
            sources = []
            for doc, score in results:
                source_info = {
                    "title": doc.metadata.get("title", "Unknown"),
                    "url": doc.metadata.get("url", ""),
                    "category": doc.metadata.get("category", "Unknown"),
                    "snippet": doc.page_content[:200] + "...",
                    "score": float(score)
                }
                sources.append(source_info)

            return {"answer": answer, "sources": sources, "trace": trace}

        except Exception as e:
            print(f"Error querying: {e}")
            if G.B4_SAFE_ERRORS:
                return {"answer": G.GENERIC_ERROR, "sources": [], "trace": trace}
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": [], "trace": trace
            }

    def get_index_stats(self) -> Dict:
        """Get statistics about the Pinecone index"""
        try:
            index = self.pc.Index(self.index_name)
            stats = index.describe_index_stats()
            return stats
        except Exception as e:
            print(f"Error getting index stats: {e}")
            return {}
