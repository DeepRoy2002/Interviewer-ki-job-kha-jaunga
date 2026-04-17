from backend.database.faiss_manager import FAISSManager
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os

class CandidateMentoringAgent:
    def __init__(self):
        self.faiss_manager = FAISSManager()
        model_name = os.getenv("LLM_MODEL", "llama3-8b-8192")
        self.llm = ChatGroq(model_name=model_name, temperature=0.7)
        
    def conduct_interview_turn(self, topic: str, candidate_answer: str = None):
        """
        If candidate_answer is None, ask the first question.
        Else, evaluate answer and ask next question.
        """
        
        # Retrieve context from FAISS
        context_docs = self.faiss_manager.similarity_search(topic, k=2)
        context = "\n".join([doc.page_content for doc in context_docs]) if context_docs else "No specific context available, rely on general knowledge."
        
        if not candidate_answer:
            # Ask first question
            prompt = PromptTemplate(
                input_variables=["context", "topic"],
                template="""You are an expert Interviewer. Based on this topic context: '{context}', 
Ask exactly one challenging interview question about '{topic}'. Do not include the answer."""
            )
            chain = prompt | self.llm
            response = chain.invoke({"context": context, "topic": topic})
            return response.content, None # Q, Feedback
            
        else:
            # Evaluate answer and ask next
            prompt = PromptTemplate(
                input_variables=["context", "topic", "candidate_answer"],
                template="""You are an expert Interviewer evaluating a candidate's answer.
Context / Rubric: '{context}'
Topic: '{topic}'
Candidate's Answer: '{candidate_answer}'

1. Provide brief constructive mentoring feedback based on the rubric/context.
2. Provide a readiness rating out of 10.
"""
            )
            chain = prompt | self.llm
            feedback_res = chain.invoke({"context": context, "topic": topic, "candidate_answer": candidate_answer})
            
            return None, feedback_res.content

    
    from backend.database.faiss_manager import FAISSManager
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os

class CandidateMentoringAgent:
    def __init__(self):
        self.faiss_manager = FAISSManager()
        model_name = os.getenv("LLM_MODEL", "llama3-8b-8192")
        self.llm = ChatGroq(model_name=model_name, temperature=0.7)
        
    def get_question(self, topic: str, previous_questions: list):
        """Generates a single question under 300 characters."""
        context_docs = self.faiss_manager.similarity_search(topic, k=2)
        context = "\n".join([doc.page_content for doc in context_docs]) if context_docs else "General knowledge"
        
        history_str = "\n".join(previous_questions)
        prompt = PromptTemplate(
            input_variables=["context", "topic", "history"],
            template="""You are an expert Interviewer. 
            Context: {context}
            Topic: {topic}
            History: {history}

            Task: Ask ONE challenging follow-up question. 
            Constraint: The question must be concise and NOT exceed 300 characters. 
            Do not provide answers or feedback yet."""
        )
        chain = prompt | self.llm
        response = chain.invoke({"context": context, "topic": topic, "history": history_str})
        
        # Trim just in case the LLM ignores the constraint
        return response.content[:300]

    def get_study_material(self, topic: str):
        """Optimized: Retrieves 3 docs and truncates them to save tokens."""
        # Reduced k from 5 to 3
        context_docs = self.faiss_manager.similarity_search(topic, k=3)
        
        # Truncate each document to 800 characters
        context_text = "\n".join([f"- {d.page_content[:800]}" for d in context_docs])
        
        prompt = PromptTemplate(
            input_variables=["context", "topic"],
            template="""Context: {context}
                        Topic: {topic}
                        Task: Extract 5 short interview Q&As from the context. 
                        Format: Q: [Question] A: [Answer]. Keep answers under 20 words."""
        )
        chain = prompt | self.llm
        return chain.invoke({"context": context_text, "topic": topic}).content

    def summarize_session(self, topic: str, interview_history: list):
        """Optimized: Truncates candidate answers to avoid token overflow."""
        history_text = ""
        for i, turn in enumerate(interview_history):
            # Truncate candidate answer to 400 chars to save tokens in the final summary
            short_answer = turn['answer'][:400] 
            history_text += f"Q{i+1}: {turn['question']}\nA{i+1}: {short_answer}\n\n"

        prompt = PromptTemplate(
            input_variables=["topic", "history"],
            template="""Review this '{topic}' interview:
{history}
Provide brief feedback and a final 'Score: X/10'."""
        )
        chain = prompt | self.llm
        return chain.invoke({"topic": topic, "history": history_text}).content

    def summarize_session(self, topic: str, interview_history: list):
        """Analyzes all 10 turns and provides a final score."""
        history_text = ""
        for i, turn in enumerate(interview_history):
            history_text += f"Q{i+1}: {turn['question']}\nA{i+1}: {turn['answer']}\n\n"

        prompt = PromptTemplate(
            input_variables=["topic", "history"],
            template="""You are a Senior Technical Recruiter evaluating a full interview for '{topic}'.
            
            Interview Transcript:
            {history}
            
            Provide:
            1. Mentoring Feedback (Strengths and areas to improve).
            2. Final Readiness Score out of 10.
            
            IMPORTANT: End your response with 'Score: X/10' (e.g., Score: 8.5/10)."""
        )
        chain = prompt | self.llm
        return chain.invoke({"topic": topic, "history": history_text}).content
