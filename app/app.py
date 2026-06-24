import streamlit as st
import json
from datetime import datetime
import os

BASE_DIR = os.path.dirname(__file__)

# Set page config
st.set_page_config(page_title="hub", layout="centered")

THEMES = {
    "Pastel Pink": {
        "bg": "#ffe6f0",
        "card": "#ffd9e8",
        "text": "#3a2a36",
        "input": "#fff0f7",
        "border": "#f2c1d6"
    },
    "Teal Light Green": {
        "bg": "#e8f7f2",
        "card": "#d5f0e5",
        "text": "#0f4d4a",
        "input": "#e7f7f1",
        "border": "#aeddd2"
    },
    "Dark Mood": {
        "bg": "#121212",
        "card": "#1e1e1e",
        "text": "#e5e5e5",
        "input": "#2a2a2a",
        "border": "#3f3f3f"
    }
}

def apply_theme(theme_name):
    theme = THEMES.get(theme_name, THEMES["Teal Light Green"])
    st.markdown(
        f"""<style>
        [data-testid="stAppViewContainer"] {{ background: {theme['bg']}; color: {theme['text']}; }}
        .main {{ background-color: transparent; }}
        .css-1v3fvcr {{ background-color: transparent; }}
        .reportview-container .main footer, .reportview-container .main header {{ background: transparent; }}
        .stButton>button {{ background-color: {theme['card']}; color: {theme['text']}; border: 1px solid {theme['border']}; border-radius: 8px; }}
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {{ background-color: {theme['input']}; color: {theme['text']}; border: 1px solid {theme['border']}; border-radius: 8px; }}
        .stRadio>div>div>label {{ color: {theme['text']}; }}
        .stMarkdown, .stText, .stCaption {{ color: {theme['text']}; }}
        .st-b7 {{ background-color: {theme['card']} !important; }}
        .css-1d391kg {{ background-color: {theme['card']} !important; }}
        .css-1outpf7 {{ background-color: {theme['card']} !important; }}
        </style>""",
        unsafe_allow_html=True,
    )

# Load users
def load_users():
    users_path = os.path.join(BASE_DIR, "users.json")
    with open(users_path, "r") as f:
        return json.load(f)["users"]

# Load messages
def load_messages():
    messages_path = os.path.join(BASE_DIR, "messages.json")
    if os.path.exists(messages_path):
        with open(messages_path, "r") as f:
            return json.load(f)["messages"]
    return []

# Save messages
def save_messages(messages):
    with open("messages.json", "w") as f:
        json.dump({"messages": messages}, f, indent=2)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
if "theme" not in st.session_state:
    st.session_state.theme = "Teal Light Green"

# Login page
if not st.session_state.logged_in:
    st.sidebar.title("Theme")
    st.sidebar.selectbox("Choose a theme", list(THEMES.keys()), key="theme")
    apply_theme(st.session_state.theme)
    st.title("hub")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Login as V", use_container_width=True, key="btn_v"):
            st.session_state.selected_user = "V"
    
    with col2:
        if st.button("Login as A", use_container_width=True, key="btn_a"):
            st.session_state.selected_user = "A"
    
    with col3:
        if st.button("Login as D", use_container_width=True, key="btn_d"):
            st.session_state.selected_user = "D"
    
    if "selected_user" in st.session_state:
        st.markdown("---")
        users = load_users()
        user_id = st.session_state.selected_user
        
        st.subheader(f"Login as {user_id}")
        password = st.text_input("Password", type="password", key="pwd_input")
        
        if st.button("Sign In", use_container_width=True):
            if user_id in users and password == users[user_id].get("password", ""):
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.session_state.pop("selected_user", None)
                st.rerun()
            else:
                st.error("Incorrect password!")

else:
    st.sidebar.title("Theme")
    st.sidebar.selectbox("Choose a theme", list(THEMES.keys()), key="theme")
    apply_theme(st.session_state.theme)
    # Main app - logged in
    st.title(f"wsg gng, {st.session_state.user_id}!")
    
    if st.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.rerun()
    
    st.markdown("---")
    
    messages = load_messages()
    user_id = st.session_state.user_id
    
    # Different UI based on who's logged in
    if user_id == "V":
        # V can text A and D
        channel = st.radio("Select Channel:", ["Chat with A", "Chat with D"], horizontal=True)
        
        recipient = "A" if channel == "Chat with A" else "D"
        
        st.subheader(channel)
        st.markdown("---")
        
        # Display messages for this channel (both directions)
        channel_messages = [m for m in messages if (m["from"] == "V" and m["to"] == recipient) or (m["from"] == recipient and m["to"] == "V")]
        channel_messages.sort(key=lambda x: x["timestamp"])
        
        if channel_messages:
            for msg in channel_messages:
                with st.chat_message(msg["from"]):
                    st.write(msg["text"])
                    st.caption(msg["timestamp"])
        else:
            st.info(f"No messages yet. Start the conversation!")
        
        st.markdown("---")
        
        # Send message
        col1, col2 = st.columns([4, 1])
        with col1:
            message_text = st.text_input(f"Message to {recipient}:", key=f"msg_{recipient}")
        with col2:
            if st.button("Send", key=f"send_{recipient}"):
                if message_text.strip():
                    new_message = {
                        "from": "V",
                        "to": recipient,
                        "text": message_text,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    messages.append(new_message)
                    save_messages(messages)
                    st.success("Message sent")
                    st.rerun()
                else:
                    st.warning("Please enter a message!")
    
    elif user_id == "A":
        st.subheader("Chat with V")
        st.markdown("---")
        
        # A can send and receive messages from V
        channel_messages = [m for m in messages if (m["from"] == "V" and m["to"] == "A") or (m["from"] == "A" and m["to"] == "V")]
        channel_messages.sort(key=lambda x: x["timestamp"])
        
        if channel_messages:
            for msg in channel_messages:
                with st.chat_message(msg["from"]):
                    st.write(msg["text"])
                    st.caption(msg["timestamp"])
        else:
            st.info("No messages yet.")
        
        st.markdown("---")
        
        # Send message to V
        col1, col2 = st.columns([4, 1])
        with col1:
            message_text = st.text_input("Message to V:", key="msg_a_to_v")
        with col2:
            if st.button("Send", key="send_a_to_v"):
                if message_text.strip():
                    new_message = {
                        "from": "A",
                        "to": "V",
                        "text": message_text,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    messages.append(new_message)
                    save_messages(messages)
                    st.success("Message sent")
                    st.rerun()
                else:
                    st.warning("Please enter a message!")
    
    elif user_id == "D":
        st.subheader("Chat with V")
        st.markdown("---")
        
        # D can send and receive messages from V
        channel_messages = [m for m in messages if (m["from"] == "V" and m["to"] == "D") or (m["from"] == "D" and m["to"] == "V")]
        channel_messages.sort(key=lambda x: x["timestamp"])
        
        if channel_messages:
            for msg in channel_messages:
                with st.chat_message(msg["from"]):
                    st.write(msg["text"])
                    st.caption(msg["timestamp"])
        else:
            st.info("No messages yet.")
        
        st.markdown("---")
        
        # Send message to V
        col1, col2 = st.columns([4, 1])
        with col1:
            message_text = st.text_input("Message to V:", key="msg_d_to_v")
        with col2:
            if st.button("Send", key="send_d_to_v"):
                if message_text.strip():
                    new_message = {
                        "from": "D",
                        "to": "V",
                        "text": message_text,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    messages.append(new_message)
                    save_messages(messages)
                    st.success("Message sent")
                    st.rerun()
                else:
                    st.warning("Please enter a message!")
