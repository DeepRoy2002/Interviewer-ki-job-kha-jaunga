import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

class FAISSManager:
    def __init__(self):
        self.db_path = os.getenv("FAISS_STORE_PATH", "faiss_store")
        model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        
        # Load existing index if available, else initialize None
        if os.path.exists(self.db_path):
            self.vector_store = FAISS.load_local(self.db_path, self.embeddings, allow_dangerous_deserialization=True)
        else:
            self.vector_store = None
            
    def add_texts(self, texts, metadatas=None):
        if self.vector_store is None:
            self.vector_store = FAISS.from_texts(texts, self.embeddings, metadatas=metadatas)
        else:
            self.vector_store.add_texts(texts, metadatas=metadatas)
        self.vector_store.save_local(self.db_path)
        
    def similarity_search(self, query, k=3):
        if self.vector_store is None:
            return []
        return self.vector_store.similarity_search(query, k=k)
