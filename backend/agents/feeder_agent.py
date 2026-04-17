from backend.database.faiss_manager import FAISSManager
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os
import json

class FeederIntelligenceAgent:
    def __init__(self):
        self.faiss_manager = FAISSManager()
        model_name = os.getenv("LLM_MODEL", "llama3-8b-8192")
        self.llm = ChatGroq(model_name=model_name, temperature=0.2)
        
    def process_sme_input(self, raw_input: str, topic: str):
        """
        Takes raw SME input and structures it into Q&A with rubrics.
        """
        prompt = PromptTemplate(
            input_variables=["input_text", "topic"],
            template="""You are a Feeder Intelligence Agent. 
Convert the following unstructured SME knowledge about '{topic}' into a structured interview question and evaluation rubric.
Return ONLY a valid JSON object with the keys: "question", "ideal_answer", "rubric", "difficulty".

SME Input:
{input_text}"""
        )
        
        chain = prompt | self.llm
        response = chain.invoke({"input_text": raw_input, "topic": topic})
        
        structured_content = response.content
        
        # Save to Vector DB
        text_to_embed = f"Topic: {topic}\n{structured_content}"
        metadata = {"topic": topic, "source": "sme_input"}
        
        self.faiss_manager.add_texts([text_to_embed], [metadata])
        
        return structured_content
