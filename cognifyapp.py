import streamlit as st
import time
import datetime

# --- CONFIGURATION & THEME ---
st.set_page_config(
    page_title="Cognify | Task Execution Support",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for soft, calming, mobile-first aesthetic without emojis
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
    
    .stButton > button:hover {
        border-color: #A0A0A0;
        background-color: #FDFDFD;
    }

    .stButton > button:active {
        background-color: #F0F2F6;
        transform: translateY(1px);
    }

    /* Primary action styling */
    div[data-testid="stVerticalBlock"] > div:nth-child(1) > button {
        background-color: #EEF2FF;
        border: 1px solid #C7D2FE;
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

    .support-text {
        font-size: 1rem;
        color: #636E72;
        margin-top: 1rem;
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
        transition: width 0.5s ease;
    }

    .disclaimer {
        font-size: 0.8rem;
        color: #95A5A6;
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
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
    st.session_state.mental_load = 20  # Percentage

# --- LOGIC AGENTS ---

class TaskDecompositionAgent:
    """Simulated AI that breaks tasks into micro-steps."""
    @staticmethod
    def get_steps(task_query, pacing="standard"):
        # Simulated heuristic decomposition
        common_tasks = {
            "laundry": ["Gather clothes", "Sort by color", "Put in machine", "Add soap", "Start machine"],
            "email": ["Open inbox", "Select one email", "Read content", "Draft brief reply", "Press send"],
            "hydration": ["Find a glass", "Go to the tap", "Fill glass with water", "Drink the whole glass"]
        }
        
        # Generic decomposition logic
        base_steps = common_tasks.get(task_query.lower(), [
            "Prepare your space",
            "Focus on the first physical movement",
            "Complete the middle part",
            "Check your progress",
            "Finalize and tidy up"
        ])
        
        if pacing == "gentle":
            # Double the steps by breaking them down further
            new_steps = []
            for step in base_steps:
                new_steps.append(f"Prepare for: {step}")
                new_steps.append(step)
            return new_steps
        return base_steps

class StateInferenceAgent:
    """Detects user hesitation or overwhelm without diagnosis."""
    @staticmethod
    def check_for_hesitation():
        current_time = time.time()
        elapsed = current_time - st.session_state.last_interaction_time
        # If user takes > 45 seconds on one step, suggest simplified pacing
        if elapsed > 45 and st.session_state.pacing_level == "standard":
            return True
        return False

# --- UI COMPONENTS ---

def render_load_indicator():
    """Visual, non-numeric cognitive load indicator."""
    load = st.session_state.mental_load
    st.write("Current Mental Space")
    st.markdown(f"""
        <div class="load-indicator">
            <div class="load-fill" style="width: {load}%"></div>
        </div>
    """, unsafe_allow_html=True)

def reset_app():
    st.session_state.stage = "setup"
    st.session_state.step_index = 0
    st.session_state.hesitation_count = 0
    st.session_state.mental_load = 20
    st.session_state.pacing_level = "standard"

def ground_user():
    """Emergency grounding feature."""
    st.info("Let us take a moment. Notice your breath. Notice your feet on the floor. There is no rush.")
    if st.button("I feel a bit steadier now"):
        st.session_state.hesitation_count = 0
        st.rerun()

# --- MAIN APPLICATION FLOW ---

def main():
    # Header
    st.title("Cognify")
    
    # 1. SETUP STAGE
    if st.session_state.stage == "setup":
        st.write("What would you like to focus on right now?")
        
        task_input = st.text_input("Enter a task in plain language", 
                                  placeholder="e.g., Sorting the laundry")
        
        category = st.selectbox("Task Category", 
                               ["Daily Life", "Work", "Study", "Self-Care"])
        
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
            if st.button("Start Gentle (Smaller Steps)"):
                if task_input:
                    st.session_state.current_task = task_input
                    st.session_state.pacing_level = "gentle"
                    st.session_state.steps = TaskDecompositionAgent.get_steps(task_input, pacing="gentle")
                    st.session_state.stage = "execution"
                    st.session_state.last_interaction_time = time.time()
                    st.rerun()

    # 2. EXECUTION STAGE
    elif st.session_state.stage == "execution":
        # Check for hesitation
        if StateInferenceAgent.check_for_hesitation():
            st.session_state.hesitation_count += 1
            st.session_state.mental_load = min(100, st.session_state.mental_load + 15)
        
        render_load_indicator()
        
        # Progress Tracking
        total_steps = len(st.session_state.steps)
        current_idx = st.session_state.step_index
        
        st.write(f"Task: {st.session_state.current_task}")
        st.progress((current_idx) / total_steps)

        # Step Card
        current_step_text = st.session_state.steps[current_idx]
        st.markdown(f"""
            <div class="step-card">
                <div class="instruction-text">{current_step_text}</div>
                <div class="support-text">Focus only on this movement. Nothing else matters yet.</div>
            </div>
        """, unsafe_allow_html=True)

        # Interaction Buttons
        if st.button("I have done this"):
            st.session_state.last_interaction_time = time.time()
            if current_idx + 1 < total_steps:
                st.session_state.step_index += 1
                st.session_state.mental_load = max(10, st.session_state.mental_load - 5)
                st.rerun()
            else:
                st.session_state.stage = "reflection"
                st.rerun()

        col_left, col_right = st.columns(2)
        with col_left:
            if st.button("Not sure how"):
                st.info("That is okay. Let us try an even smaller version of this step.")
                # Adaptive behavior: simplify current step
                st.session_state.steps.insert(current_idx + 1, f"Just look at what is needed for: {current_step_text}")
                st.session_state.mental_load = min(100, st.session_state.mental_load + 10)
        
        with col_right:
            if st.button("Too much right now"):
                st.session_state.stage = "grounding"
                st.rerun()

        # Coach Persona / Encouragement
        if st.session_state.hesitation_count > 0:
            st.write("We are going at your pace. There is no timer here.")

    # 3. GROUNDING STAGE (Additional Feature: Emergency Pause)
    elif st.session_state.stage == "grounding":
        st.subheader("Taking a moment")
        ground_user()
        if st.button("Return to task"):
            st.session_state.stage = "execution"
            st.session_state.last_interaction_time = time.time()
            st.rerun()

    # 4. REFLECTION STAGE
    elif st.session_state.stage == "reflection":
        st.balloons() # Visual celebration without emojis
        st.subheader("Task Complete")
        st.write("You showed great persistence. Take a moment to acknowledge the effort you put in.")
        
        st.markdown("""
            <div class="step-card">
                Complete: {0}<br>
                Pacing: {1}
            </div>
        """.format(st.session_state.current_task, st.session_state.pacing_level), unsafe_allow_html=True)
        
        if st.button("Start a new task"):
            reset_app()
            st.rerun()

    # --- SIDEBAR / MEMORY SAFE SESSION (Additional Feature) ---
    with st.sidebar:
        st.write("Session Support")
        if st.button("Reset Everything"):
            reset_app()
            st.rerun()
        
        st.divider()
        st.write("Guidance Mode")
        st.write("Currently using " + st.session_state.pacing_level + " pacing.")
        
        # Ethical Disclaimer
        st.markdown("""
            <div class="disclaimer">
                Cognify is a cognitive support tool and does not provide medical advice, 
                diagnosis, or treatment. It is designed to assist with task execution 
                flow through heuristic logic.
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
