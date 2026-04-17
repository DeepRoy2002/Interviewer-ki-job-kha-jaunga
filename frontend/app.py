import sys
import os
import re
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
# Path setup
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.agents.feeder_agent import FeederIntelligenceAgent
from backend.agents.candidate_agent import CandidateMentoringAgent
from backend.agents.executive_agent import ExecutiveTrackingAgent

load_dotenv()

st.set_page_config(page_title="AI Mentoring Platform", layout="wide")

# --- 1. STYLING (The Card Design CSS) ---
st.markdown("""
    <style>
    .role-card {
        border-radius: 10px;
        padding: 25px;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        height: 280px;
        margin-bottom: 10px;
        transition: transform 0.3s ease;
    }
    .role-card:hover {
        transform: translateY(-5px);
        border-color: #4CAF50;
    }
    .role-icon { font-size: 50px; margin-bottom: 15px; }
    .role-title { font-weight: bold; font-size: 22px; color: #1E1E1E; margin-bottom: 10px; }
    .role-desc { color: #666; font-size: 15px; line-height: 1.4; }
    </style>
""", unsafe_allow_html=True)

# --- 2. ROLE SELECTION (The Gatekeeper / Frontpage) ---
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if st.session_state.user_role is None:
    st.title("AI-Powered Interview Mentoring Platform")
    st.markdown("<h4 style='color: gray;'>Choose your role to continue</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="role-card"><div class="role-icon">🗣️</div><div class="role-title">Candidate</div><div class="role-desc">Practice a full 10-question mock interview and get a readiness score.</div></div>', unsafe_allow_html=True)
        if st.button("Enter Candidate Portal", use_container_width=True):
            st.session_state.user_role = "Candidate"
            st.rerun()

    with col2:
        st.markdown('<div class="role-card"><div class="role-icon">🧠</div><div class="role-title">Feeder</div><div class="role-desc">SMEs can upload raw knowledge to build interview rubrics and questions.</div></div>', unsafe_allow_html=True)
        if st.button("Enter Feeder Portal", use_container_width=True):
            st.session_state.user_role = "Feeder"
            st.rerun()

    with col3:
        st.markdown('<div class="role-card"><div class="role-icon">📊</div><div class="role-title">Executive</div><div class="role-desc">View performance trends, score graphs, and candidate readiness analytics.</div></div>', unsafe_allow_html=True)
        if st.button("Enter Executive Portal", use_container_width=True):
            st.session_state.user_role = "Executive"
            st.rerun()
    st.stop()


# --- 2. SIDEBAR FOR NAVIGATION & LOGOUT ---
with st.sidebar:
    st.title(f"Logged in as: {st.session_state.user_role}")
    if st.button("Change Role / Logout"):
        # Reset all session states
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.divider()
    st.info("Role-based access active. Switch roles above if needed.")


# --- 3. PAGE CONTENT ROUTING ---

# --- ROLE: CANDIDATE ---
if st.session_state.user_role == "Candidate":
    st.title("🗣️ Candidate Portal")
    
    # Initialize Candidate-specific states
    if "cand_mode" not in st.session_state:
        st.session_state.cand_mode = None  # None, 'Study', or 'Quiz'
    
    # 1. INITIAL CHOICE: Study vs Quiz
    if st.session_state.cand_mode is None:
        st.subheader("How would you like to prepare today?")
        col_study, col_quiz = st.columns(2)
        
        with col_study:
            st.info("### 📚 Study Mode\nReview top 5 questions and answers based on expert knowledge.")
            if st.button("Start Studying", use_container_width=True):
                st.session_state.cand_mode = "Study"
                st.rerun()
                
        with col_quiz:
            st.success("### ✍️ Take Quiz\nA formal 10-question evaluation with final scoring.")
            if st.button("Start Quiz", use_container_width=True):
                st.session_state.cand_mode = "Quiz"
                st.rerun()

    # 2. STUDY MODE LOGIC
    elif st.session_state.cand_mode == "Study":
        st.subheader("📚 Study Session")
        topic = st.text_input("What topic would you like to study?", key="study_topic")
        
        if topic:
            if st.button("Generate Study Material") or "study_content" in st.session_state:
                if "study_content" not in st.session_state or st.session_state.get("last_topic") != topic:
                    agent = CandidateMentoringAgent()
                    with st.spinner("Fetching expert Q&A..."):
                        st.session_state.study_content = agent.get_study_material(topic)
                        st.session_state.last_topic = topic
                
                st.markdown(st.session_state.study_content)
                st.divider()
                
                col_cont, col_switch = st.columns(2)
                with col_cont:
                    if st.button("Study More (Refresh)", use_container_width=True):
                        del st.session_state.study_content
                        st.rerun()
                with col_switch:
                    if st.button("Ready? Take the Quiz ➔", use_container_width=True):
                        st.session_state.cand_mode = "Quiz"
                        st.session_state.main_topic = topic # Carry topic over
                        st.rerun()

    # 3. QUIZ MODE LOGIC (Your existing logic)
    elif st.session_state.cand_mode == "Quiz":
        st.subheader("✍️ Formal Interview Quiz")
        TOTAL_QUESTIONS = 10
        PASS_THRESHOLD = 7.0

        if "interview_active" not in st.session_state:
            st.session_state.interview_active = False
            st.session_state.q_count = 0
            st.session_state.history = []
            st.session_state.current_q = ""

        # Pre-fill topic if coming from Study Mode
        default_topic = st.session_state.get("main_topic", "")
        topic_input = st.text_input("Confirm Quiz Topic:", value=default_topic)

        if not st.session_state.interview_active:
            if st.button("Begin Evaluation"):
                if topic_input:
                    st.session_state.interview_active = True
                    st.session_state.main_topic = topic_input
                    st.session_state.q_count = 1
                    agent = CandidateMentoringAgent()
                    st.session_state.current_q = agent.get_question(topic_input, [])
                    st.rerun()
        else:
            # (Insert your existing 10-question logic here...)
            st.progress(st.session_state.q_count / TOTAL_QUESTIONS)
            st.info(f"Question {st.session_state.q_count}: {st.session_state.current_q}")
            answer = st.chat_input("Your answer...")
            
            if answer:
                st.session_state.history.append({"question": st.session_state.current_q, "answer": answer})
                if st.session_state.q_count < TOTAL_QUESTIONS:
                    st.session_state.q_count += 1
                    agent = CandidateMentoringAgent()
                    st.session_state.current_q = agent.get_question(st.session_state.main_topic, [h['question'] for h in st.session_state.history])
                    st.rerun()
                else:
                    # Final Summary logic remains same as previous code provided...
                    st.session_state.interview_active = False
                    agent = CandidateMentoringAgent()
                    summary = agent.summarize_session(st.session_state.main_topic, st.session_state.history)
                    st.markdown(summary)
                    # ... add your score extraction and logging ...
                    if st.button("Back to Candidate Menu"):
                        st.session_state.cand_mode = None
                        st.rerun()

# --- ROLE: FEEDER ---
elif st.session_state.user_role == "Feeder":
    st.title("🧠 Feeder Intelligence Agent")
    st.write("Ingest SME knowledge into the Vector Database.")
    
    feeder_topic = st.text_input("Topic Name (e.g. AWS Architecture):")
    raw_content = st.text_area("Paste unstructured interview knowledge here:", height=300)
    
    if st.button("Ingest Knowledge"):
        if feeder_topic and raw_content:
            with st.spinner("Processing..."):
                feeder_agent = FeederIntelligenceAgent()
                try:
                    structured = feeder_agent.process_sme_input(raw_content, feeder_topic)
                    st.success("Successfully ingested!")
                    st.json(structured)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("All fields are required.")

# --- ROLE: EXECUTIVE ---
elif st.session_state.user_role == "Executive":
    st.title("📊 Executive Dashboard")
    exec_agent = ExecutiveTrackingAgent()
    metrics = exec_agent.get_dashboard_metrics()
    
    # 1. Top Level Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Interviews", str(metrics["total_interviews_conducted"]))
    col2.metric("Knowledge Areas", str(len(set([e["topic"] for e in metrics["evaluations"]]))))
    col3.metric("Avg Readiness", f"{metrics['average_readiness_score']} / 10")
    
    st.divider()

    if metrics["evaluations"]:
        # 2. Score Improvement Visualization
        st.subheader("📈 Score Trends by Topic")
        
        # Convert evaluations to a DataFrame
        df = pd.DataFrame(metrics["evaluations"])
        
        # We create an 'Attempt Number' for each topic to show progress over time
        df['Attempt'] = df.groupby('topic').cumcount() + 1
        
        # Pivot data for the line chart: Rows = Attempt, Columns = Topics, Values = Scores
        chart_data = df.pivot(index='Attempt', columns='topic', values='score')
        
        # Handle cases with missing values (if one topic has 5 attempts and another has 2)
        chart_data = chart_data.ffill().fillna(0) 

        st.line_chart(chart_data)
        
        st.caption("This graph shows how candidate scores evolve across successive attempts for each specific topic.")

        # 3. Raw Data Logs
        with st.expander("View Detailed Evaluation Logs"):
            st.dataframe(df[["topic", "score", "Attempt"]], use_container_width=True)
    else:
        st.info("No interview data available yet. Trends will appear once candidates complete interviews.")