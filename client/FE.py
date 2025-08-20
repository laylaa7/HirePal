import streamlit as st
import base64
from io import BytesIO
import json

# Configure page
st.set_page_config(
    page_title="HirePal - Deloitte Recruiting Assistant",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Deloitte branding and styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');
    
    .main {
        font-family: 'Source Sans Pro', sans-serif;
        background-color: #ffffff;
    }
    
    .deloitte-green {
        color: #86BC25;
    }
    
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .bot-message {
        background-color: #f8f9fa;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 16px;
        margin: 8px 0;
        margin-right: 60px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .recruiter-message {
        background-color: #86BC25;
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 16px;
        margin: 8px 0;
        margin-left: 60px;
        text-align: right;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .candidate-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        transition: transform 0.2s ease;
    }
    
    .candidate-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .candidate-header {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
    }
    
    .candidate-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #86BC25, #a8d147);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 20px;
        margin-right: 16px;
    }
    
    .candidate-info h3 {
        margin: 0;
        color: #2c3e50;
        font-weight: 600;
        font-size: 18px;
    }
    
    .candidate-info p {
        margin: 4px 0;
        color: #6c757d;
        font-size: 14px;
    }
    
    .skills-container {
        margin: 12px 0;
    }
    
    .skill-tag {
        display: inline-block;
        background-color: #e8f5e8;
        color: #86BC25;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        margin: 2px 4px 2px 0;
        font-weight: 500;
    }
    
    .action-buttons {
        display: flex;
        gap: 12px;
        margin-top: 16px;
    }
    
    .btn-shortlist {
        background-color: #86BC25;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .btn-shortlist:hover {
        background-color: #75a521;
    }
    
    .btn-skip {
        background-color: #dc3545;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .btn-skip:hover {
        background-color: #c82333;
    }
    
    .btn-view-cv {
        background-color: #6c757d;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .btn-view-cv:hover {
        background-color: #5a6268;
    }
    
    .header-title {
        text-align: center;
        color: #86BC25;
        font-weight: 700;
        font-size: 32px;
        margin-bottom: 8px;
    }
    
    .header-subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 16px;
        margin-bottom: 32px;
    }
    
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e9ecef;
        padding: 12px 20px;
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #86BC25;
        box-shadow: 0 0 0 2px rgba(134, 188, 37, 0.2);
    }
    
    .stButton > button {
        background-color: #86BC25;
        color: white;
        border-radius: 25px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        font-family: 'Source Sans Pro', sans-serif;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #75a521;
    }
</style>
""", unsafe_allow_html=True)

# Sample candidate data
SAMPLE_CANDIDATES = [
    {
        "name": "Sarah Chen",
        "role": "Senior Data Scientist",
        "skills": ["Python", "Machine Learning", "SQL", "TensorFlow", "AWS"],
        "location": "San Francisco, CA",
        "experience": "5+ years",
        "cv_content": "Experienced Data Scientist with expertise in ML algorithms and big data processing..."
    },
    {
        "name": "Michael Rodriguez",
        "role": "Full Stack Developer",
        "skills": ["React", "Node.js", "TypeScript", "MongoDB", "Docker"],
        "location": "Austin, TX",
        "experience": "4+ years",
        "cv_content": "Full Stack Developer with strong background in modern web technologies..."
    },
    {
        "name": "Emily Johnson",
        "role": "Product Manager",
        "skills": ["Agile", "Roadmapping", "Analytics", "Stakeholder Management", "Jira"],
        "location": "New York, NY",
        "experience": "6+ years",
        "cv_content": "Strategic Product Manager with proven track record of launching successful products..."
    },
    {
        "name": "David Kim",
        "role": "DevOps Engineer",
        "skills": ["Kubernetes", "CI/CD", "Terraform", "AWS", "Monitoring"],
        "location": "Seattle, WA",
        "experience": "7+ years",
        "cv_content": "DevOps Engineer specializing in cloud infrastructure and automation..."
    }
]

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "content": "Hello 👋 this is HirePal, Deloitte's recruiting assistant. What role are you hiring for today?"}
    ]

if 'current_candidates' not in st.session_state:
    st.session_state.current_candidates = []

if 'current_candidate_index' not in st.session_state:
    st.session_state.current_candidate_index = 0

if 'shortlisted' not in st.session_state:
    st.session_state.shortlisted = []

def get_initials(name):
    return ''.join([word[0].upper() for word in name.split()[:2]])

def display_candidate_card(candidate, index):
    """Display a candidate card with interactive buttons"""
    
    card_html = f"""
    <div class="candidate-card">
        <div class="candidate-header">
            <div class="candidate-avatar">
                {get_initials(candidate['name'])}
            </div>
            <div class="candidate-info">
                <h3>{candidate['name']}</h3>
                <p><strong>{candidate['role']}</strong></p>
                <p>📍 {candidate['location']} • {candidate['experience']}</p>
            </div>
        </div>
        <div class="skills-container">
            {''.join([f'<span class="skill-tag">{skill}</span>' for skill in candidate['skills']])}
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("👀 View CV", key=f"view_cv_{index}"):
            with st.expander("📄 CV Preview", expanded=True):
                st.markdown(f"**{candidate['name']} - {candidate['role']}**")
                st.markdown("---")
                st.text_area("CV Content", candidate['cv_content'], height=200, disabled=True)
    
    with col2:
        if st.button("✅ Shortlist", key=f"shortlist_{index}", type="primary"):
            if candidate not in st.session_state.shortlisted:
                st.session_state.shortlisted.append(candidate)
                st.success(f"✅ {candidate['name']} added to shortlist!")
            next_candidate()
    
    with col3:
        if st.button("❌ Skip", key=f"skip_{index}"):
            st.info(f"⏭️ Skipped {candidate['name']}")
            next_candidate()

def next_candidate():
    """Move to next candidate or show completion message"""
    if st.session_state.current_candidate_index < len(st.session_state.current_candidates) - 1:
        st.session_state.current_candidate_index += 1
        st.rerun()
    else:
        # All candidates reviewed
        st.session_state.messages.append({
            "role": "bot", 
            "content": f"🎉 You've reviewed all candidates! You have {len(st.session_state.shortlisted)} candidates in your shortlist."
        })
        st.session_state.current_candidates = []
        st.session_state.current_candidate_index = 0
        st.rerun()

def simulate_candidate_search(query):
    """Simulate AI search for candidates based on query"""
    # Simple keyword matching for demo
    relevant_candidates = []
    query_lower = query.lower()
    
    for candidate in SAMPLE_CANDIDATES:
        # Check if query matches role or skills
        if (query_lower in candidate['role'].lower() or 
            any(query_lower in skill.lower() for skill in candidate['skills']) or
            any(skill.lower() in query_lower for skill in candidate['skills'])):
            relevant_candidates.append(candidate)
    
    # If no specific matches, return some candidates anyway
    if not relevant_candidates:
        relevant_candidates = SAMPLE_CANDIDATES[:2]
    
    return relevant_candidates

# Header
st.markdown('<h1 class="header-title">HirePal</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Deloitte\'s AI-Powered Recruiting Assistant</p>', unsafe_allow_html=True)

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "bot":
        st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="recruiter-message">{message["content"]}</div>', unsafe_allow_html=True)

# Display current candidate if available
if st.session_state.current_candidates and st.session_state.current_candidate_index < len(st.session_state.current_candidates):
    current_candidate = st.session_state.current_candidates[st.session_state.current_candidate_index]
    st.markdown("---")
    st.markdown(f"**Candidate {st.session_state.current_candidate_index + 1} of {len(st.session_state.current_candidates)}**")
    display_candidate_card(current_candidate, st.session_state.current_candidate_index)

st.markdown('</div>', unsafe_allow_html=True)

# Input area
st.markdown("---")
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input("Type your message...", placeholder="e.g., 'Looking for a senior data scientist with Python experience'", label_visibility="collapsed")

with col2:
    send_button = st.button("Send", type="primary")

# Handle user input
if send_button and user_input:
    # Add user message
    st.session_state.messages.append({"role": "recruiter", "content": user_input})
    
    # Simulate bot response and candidate search
    candidates = simulate_candidate_search(user_input)
    
    if candidates:
        bot_response = f"Great! I found {len(candidates)} candidates matching your criteria. Let me show them to you one by one:"
        st.session_state.messages.append({"role": "bot", "content": bot_response})
        st.session_state.current_candidates = candidates
        st.session_state.current_candidate_index = 0
    else:
        bot_response = "I couldn't find any candidates matching that criteria. Could you try a different search term or be more specific about the role requirements?"
        st.session_state.messages.append({"role": "bot", "content": bot_response})
    
    st.rerun()

# Sidebar with shortlisted candidates
if st.session_state.shortlisted:
    with st.sidebar:
        st.markdown("### 📋 Shortlisted Candidates")
        for i, candidate in enumerate(st.session_state.shortlisted):
            with st.expander(f"{candidate['name']} - {candidate['role']}"):
                st.write(f"**Location:** {candidate['location']}")
                st.write(f"**Experience:** {candidate['experience']}")
                st.write("**Skills:**")
                for skill in candidate['skills']:
                    st.write(f"• {skill}")
