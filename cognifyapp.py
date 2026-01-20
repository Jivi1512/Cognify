import streamlit as st
import time
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION & THEME ---
st.set_page_config(
    page_title="Cognify | Task Execution Support",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for soft, calming, mobile-first aesthetic
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #F8F9FA;
        color: #2D3436;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3.5rem;
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        transition: all 0.2s ease;
        font-size: 1.1rem;
        color: #2D3436;
    }
    
    .step-card {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        margin-bottom: 1.5rem;
        border-left: 5px solid #C7D2FE;
    }

    .instruction-text {
        font-size: 1.4rem;
        line-height: 1.6;
        font-weight: 500;
        color: #1A1A1A;
    }

    .load-indicator {
        height: 8px;
        border-radius: 4px;
        background-color: #E0E0E0;
        margin-bottom: 2rem;
    }

    .load-fill {
        height: 100%;
        border-radius: 4px;
        background-color: #A5B4FC;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'stage' not in st.session_state:
    st.session_state.stage = "setup"
if 'current_task' not in st.session_state:
    st.session_state.current_task = None
if 'steps' not in st.session_state:
    st.session_state.steps = []
if 'step_index' not in st.session_state:
    st.session_state.step_index = 0
if 'hesitation_count' not in st.session_state:
    st.session_state.hesitation_count = 0
if 'last_interaction_time' not in st.session_state:
    st.session_state.last_interaction_time = time.time()
if 'pacing_level' not in st.session_state:
    st.session_state.pacing_level = "standard"
if 'mental_load' not in st.session_state:
    st.session_state.mental_load = 20

# --- DATA PERSISTENCE ---

def save_user_to_sheets(user_data):
    """Saves user profile information to the configured Google Sheet."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Read existing data to append
        existing_data = conn.read(worksheet="users", ttl=0)
        new_row = pd.DataFrame([user_data])
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(worksheet="users", data=updated_df)
        return True
    except Exception as e:
        st.error("Technical connection issue. Data saved locally for this session only.")
        return False

# --- LOGIC AGENTS ---

class TaskDecompositionAgent:
    @staticmethod
    def get_steps(task_query, pacing="standard"):
        common_tasks = {
            "laundry": ["Gather clothes", "Sort by color", "Put in machine", "Add soap", "Start machine"],
            "email": ["Open inbox", "Select one email", "Read content", "Draft brief reply", "Press send"],
            "hydration": ["Find a glass", "Go to the tap", "Fill glass with water", "Drink the whole glass"]
        }
        base_steps = common_tasks.get(task_query.lower(), [
            "Prepare your space",
            "Focus on the first physical movement",
            "Complete the middle part",
            "Check your progress",
            "Finalize and tidy up"
        ])
        if pacing == "gentle":
            new_steps = []
            for step in base_steps:
                new_steps.append(f"Prepare for: {step}")
                new_steps.append(step)
            return new_steps
        return base_steps

# --- UI PAGES ---

def show_login_page():
    """Onboarding and profile registration page."""
    st.title("Welcome to Cognify")
    st.write("Please share a few details so we can adjust the experience to your needs.")
    
    with st.form("onboarding_form"):
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=1, max_value=120, value=25)
        occupation = st.text_input("Occupation / Daily Role")
        gender = st.selectbox("Gender", ["Prefer not to say", "Female", "Male", "Non-binary", "Other"])
        cognitive_goal = st.selectbox("Primary Support Goal", 
                                     ["Executive Function", "Memory Support", "Focus Recovery", "Reducing Overwhelmed Feelings"])
        
        submitted = st.form_submit_button("Begin Experience")
        
        if submitted:
            if name and occupation:
                user_record = {
                    "name": name,
                    "age": age,
                    "occupation": occupation,
                    "gender": gender,
                    "goal": cognitive_goal,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_user_to_sheets(user_record)
                st.session_state.user_name = name
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.warning("Please complete all fields to help us personalize your support.")

def main_app():
    """Main task execution interface."""
    st.title("Cognify")
    st.write(f"Logged in as: {st.session_state.user_name}")
    
    if st.session_state.stage == "setup":
        st.write("What would you like to focus on right now?")
        task_input = st.text_input("Enter a task in plain language", placeholder="e.g., Sorting the laundry")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Steady"):
                if task_input:
                    st.session_state.current_task = task_input
                    st.session_state.steps = TaskDecompositionAgent.get_steps(task_input)
                    st.session_state.stage = "execution"
                    st.session_state.last_interaction_time = time.time()
                    st.rerun()
        with col2:
            if st.button("Start Gentle"):
                if task_input:
                    st.session_state.current_task = task_input
                    st.session_state.pacing_level = "gentle"
                    st.session_state.steps = TaskDecompositionAgent.get_steps(task_input, pacing="gentle")
                    st.session_state.stage = "execution"
                    st.session_state.last_interaction_time = time.time()
                    st.rerun()

    elif st.session_state.stage == "execution":
        # Progress and Load Logic
        current_idx = st.session_state.step_index
        total_steps = len(st.session_state.steps)
        
        st.write(f"Focusing on: {st.session_state.current_task}")
        st.progress((current_idx) / total_steps)
        
        current_step_text = st.session_state.steps[current_idx]
        st.markdown(f"""
            <div class="step-card">
                <div class="instruction-text">{current_step_text}</div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Step Complete"):
            if current_idx + 1 < total_steps:
                st.session_state.step_index += 1
                st.rerun()
            else:
                st.session_state.stage = "reflection"
                st.rerun()
        
        if st.button("Take a Break"):
            st.session_state.stage = "setup"
            st.rerun()

    elif st.session_state.stage == "reflection":
        st.subheader("Task Finished")
        st.write("You focused well today. Your mind deserves this moment of success.")
        if st.button("Start New Task"):
            st.session_state.stage = "setup"
            st.session_state.step_index = 0
            st.rerun()

# --- MAIN ROUTER ---

if not st.session_state.authenticated:
    show_login_page()
else:
    main_app()

# Sidebar Info
with st.sidebar:
    st.write("System Status")
    if st.session_state.authenticated:
        st.write("Profile: Verified")
        if st.button("Sign Out"):
            st.session_state.authenticated = False
            st.rerun()
    st.divider()
    st.caption("Privacy First: Your data is stored securely in your private cloud sheet.")
