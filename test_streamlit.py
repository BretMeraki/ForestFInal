import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.title("Forest App Test UI")

# Display session state
st.write("## Session State")
st.json(st.session_state)

# Display sidebar with login form
with st.sidebar:
    st.title("Login Test")
    username = st.text_input("Username", value="bretmeraki@icloud.com")
    if st.button("Login"):
        st.success(f"Mock login for {username}")
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = True
        if "user_info" not in st.session_state:
            st.session_state.user_info = {"email": username}
        st.rerun()

# Display main content
if st.session_state.get("authenticated"):
    st.write("## Main Content (Authenticated)")
    st.write(f"Logged in as: {st.session_state.get('user_info', {}).get('email', 'Unknown')}")
    
    # Test onboarding
    onboarding_options = ["needs_goal", "needs_context", "completed"]
    selected_status = st.selectbox("Test Onboarding Status", onboarding_options)
    
    if selected_status == "needs_goal":
        st.write("### Goal Setting")
        goal = st.text_area("What's your main goal?")
        if st.button("Submit Goal"):
            st.success("Goal submitted (mock)")
            st.session_state["onboarding_status"] = "needs_context"
            st.rerun()
    
    elif selected_status == "needs_context":
        st.write("### Context Setting")
        context = st.text_area("Tell us more about your situation...")
        if st.button("Submit Context"):
            st.success("Context submitted (mock)")
            st.session_state["onboarding_status"] = "completed"
            st.rerun()
    
    elif selected_status == "completed":
        st.write("### Chat Interface")
        user_input = st.chat_input("What would you like to do?")
        if user_input:
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write(f"You said: {user_input}")
else:
    st.write("## Please log in")
    st.info("Use the sidebar to log in")

# Debug environment variables
st.write("## Environment Variables")
backend_url = os.getenv("BACKEND_URL", "No BACKEND_URL found")
st.write(f"BACKEND_URL: {backend_url}")
