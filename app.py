import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import time
import google.generativeai as genai
from PIL import Image
import os

# ==========================================
# 0. CONFIGURATION & STYLING
# ==========================================
st.set_page_config(page_title="ClimateGuardian AI", page_icon="🌿", layout="wide")

# Configure the API key
genai.configure(api_key="AIzaSyD5Y9RLK5-109WAky20N3P2DTJG7rNHbwo")

# === Background Music ==

if st.button("Play Music"):
    with open("background-music-443623.mp3", "rb") as audio:
        st.audio(audio.read(), format="audio/mp3", loop=True)


# --- CUSTOM CSS FOR ECO THEME + GREEN ANIMATED BACKGROUND ---
st.markdown("""
<style>
/* Animated Green Gradient Background */
.stApp {
    background: linear-gradient(-45deg, #a8e6cf, #dcedc1, #81c784, #4caf50);
    background-size: 400% 400%;
    animation: gradientBG 20s ease infinite;
}

/* Keyframes for animated gradient */
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Optional: Overlay Animated Image */
.stApp::before {
    content: "";
    background: url('nature_animation.gif') no-repeat center center;
    background-size: cover;
    position: fixed;
    top:0; left:0;
    width:100%; height:100%;
    opacity:0.15;
    z-index:-1;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #e8f5e9;
    border-right: 2px solid #c8e6c9;
}

/* Headers */
h1, h2, h3 {
    color: #2e7d32;
    font-family: 'Helvetica Neue', sans-serif;
}

/* Buttons */
div.stButton > button {
    background-color: #4CAF50;
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 24px;
    font-weight: bold;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: 0.3s;
}
div.stButton > button:hover {
    background-color: #45a049;
    transform: scale(1.05);
}

/* Input Fields */
.stTextInput > div > div > input {
    border-radius: 10px;
    border: 1px solid #4CAF50;
}

/* Metrics */
div[data-testid="stMetricValue"] {
    color: #1b5e20;
}

/* Custom Card */
.eco-card {
    padding: 20px;
    background-color: white;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    margin-bottom: 20px;
    border-left: 5px solid #4CAF50;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SESSION STATE SETUP
# ==========================================
if 'student_data' not in st.session_state:
    st.session_state['student_data'] = pd.DataFrame(columns=['Student_ID', 'Action', 'Points', 'Date'])

if 'messages' not in st.session_state:
    st.session_state['messages'] = [{"role": "assistant", "content": "🌿 Hi! I'm EcoBot. I can generate quizzes, give tips, or help you save the planet!"}]

if 'quiz_data' not in st.session_state:
    st.session_state['quiz_data'] = None

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def get_gemini_model():
    return genai.GenerativeModel('gemini-2.5-flash')

def generate_ai_quiz_question():
    try:
        model = get_gemini_model()
        prompt = """
        Generate 1 multiple choice question about environmental sustainability, recycling, or climate change.
        Strictly follow this format using the pipe symbol (|) as a separator:
        Question Text | Option A | Option B | Option C | Option D | Correct Option (A/B/C/D) | Short Explanation
        """
        response = model.generate_content(prompt)
        text = response.text.strip()
        parts = text.split('|')
        if len(parts) >= 6:
            return {
                "q": parts[0].strip(),
                "options": [parts[1].strip(), parts[2].strip(), parts[3].strip(), parts[4].strip()],
                "ans": parts[5].strip().upper(),
                "exp": parts[6].strip() if len(parts) > 6 else "Great job saving the planet!"
            }
        else:
            return None
    except Exception as e:
        return None

def log_action(action, points):
    new_data = pd.DataFrame({
        'Student_ID': ['Student_User'], 
        'Action': [action],
        'Points': [points],
        'Date': [datetime.date.today()]
    })
    st.session_state['student_data'] = pd.concat([st.session_state['student_data'], new_data], ignore_index=True)

# ==========================================
# 3. MODULES
# ==========================================
def chat_interface():
    st.markdown('<div class="eco-card"><h3>🤖 EcoBot Mentor</h3><p>Ask me anything about nature!</p></div>', unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("How can I recycle glass?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("EcoBot is thinking... 🌱"):
            try:
                model = get_gemini_model()
                ai_prompt = f"You are EcoBot, a fun sustainability expert for students. Keep it short and encouraging. Answer: {prompt}"
                response = model.generate_content(ai_prompt)
                reply = response.text
            except:
                reply = "I'm having trouble connecting to the nature network. Try again!"
        
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)

def game_interface():
    st.markdown('<div class="eco-card"><h3>🎮 AI Eco-Challenge</h3><p>Infinite questions generated by AI!</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state['quiz_data'] is None:
            if st.button("🌱 Generate New Question"):
                with st.spinner("Growing a new question..."):
                    q_data = generate_ai_quiz_question()
                    if q_data:
                        st.session_state['quiz_data'] = q_data
                        st.rerun()
                    else:
                        st.error("AI couldn't generate a question. Try again.")
        
        if st.session_state['quiz_data']:
            q = st.session_state['quiz_data']
            st.subheader(f"Q: {q['q']}")
            opts = q['options']
            choice = st.radio("Select an answer:", opts, key="quiz_choice")
            choice_index = opts.index(choice)
            choice_letter = ["A", "B", "C", "D"][choice_index]
            
            if st.button("Submit Answer"):
                if choice_letter == q['ans']:
                    st.balloons()
                    st.success(f"Correct! 🎉 {q['exp']}")
                    log_action("AI Quiz Win", 15)
                    st.session_state['quiz_data'] = None
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"Oops! The correct answer was Option {q['ans']}.")
                    st.warning(q['exp'])
                    st.session_state['quiz_data'] = None
                    time.sleep(3)
                    st.rerun()

    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/4148/4148323.png", width=150)
        st.write("**Current Points:**")
        total = st.session_state['student_data']['Points'].sum()
        st.metric("Eco-Score", total)

def mission_tracker():
    st.markdown('<div class="eco-card"><h3>📝 Daily Green Missions</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        action = st.selectbox("Select Mission Completed:", 
                              ["Recycled Plastic", "Planted a Tree", "Walked/Biked to School", "Saved Electricity", "Used Reusable Bag", "Composted Food"])
    
    with col2:
        points_map = {"Recycled Plastic": 5, "Planted a Tree": 50, "Walked/Biked to School": 20, "Saved Electricity": 10, "Used Reusable Bag": 5, "Composted Food": 15}
        st.metric(label="Points Value", value=points_map[action])
    
    if st.button("✅ Log Mission"):
        log_action(action, points_map[action])
        st.success(f"Mission '{action}' logged! Points added.")

def admin_dashboard():
    st.markdown('<div class="eco-card"><h3>🏫 School Sustainability Dashboard</h3></div>', unsafe_allow_html=True)
    
    df = st.session_state['student_data']
    
    if df.empty:
        st.info("No data yet. Go play the game or log a mission!")
        return

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Eco-Points", df['Points'].sum())
    m2.metric("Total Actions", len(df))
    m3.metric("Trees Planted", len(df[df['Action'] == "Planted a Tree"]))
    
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(df, names='Action', values='Points', title="Impact Distribution", color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        fig_bar = px.bar(df, x='Action', y='Points', color='Points', title="Top Activities", color_continuous_scale='Greens')
        st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# 4. MAIN LAYOUT
# ==========================================
def main():
    with st.sidebar:
        st.title("🌍 ClimateGuardian")
        try:
            image = Image.open("image_c07dfb.png")
            st.image(image, caption="Save Earth, Save Future", use_container_width=True)
        except FileNotFoundError:
            st.warning("⚠️ Please upload 'image_c07dfb.png' to the folder.")
            
        menu = st.radio("Navigate", ["Student Hub", "Admin Dashboard"])
        st.info("Developed by Environment cleaner")

    try:
        col_banner1, col_banner2 = st.columns([1, 4])
        with col_banner1:
             st.image("image_c07dfb.png", width=120)
        with col_banner2:
            st.title("Welcome to ClimateGuardian!")
            st.write("Your AI-powered companion for a greener planet.")
    except:
        st.title("Welcome to ClimateGuardian!")

    if menu == "Student Hub":
        tab1, tab2, tab3 = st.tabs(["🤖 AI Chat", "🎮 AI Quiz", "✅ Missions"])
        with tab1: chat_interface()
        with tab2: game_interface()
        with tab3: mission_tracker()
    elif menu == "Admin Dashboard":
        admin_dashboard()

if __name__ == "__main__":
    main()



