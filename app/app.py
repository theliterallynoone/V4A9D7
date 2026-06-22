import streamlit as st
import json
from datetime import datetime
import os

# Set page config
st.set_page_config(page_title="Texting App", page_icon="💬", layout="centered")

# Load users
def load_users():
    with open("users.json", "r") as f:
        return json.load(f)["users"]

# Load messages
def load_messages():
    if os.path.exists("messages.json"):
        with open("messages.json", "r") as f:
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

# Login page
if not st.session_state.logged_in:
    st.title("💬 Texting App")
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
            if password == users[user_id]["password"]:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                del st.session_state.selected_user
                st.rerun()
            else:
                st.error("❌ Incorrect password!")

else:
    # Main app - logged in
    st.title(f"💬 Welcome, {st.session_state.user_id}!")
    
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
        
        st.subheader(f"💬 {channel}")
        st.markdown("---")
        
        # Display messages for this channel
        channel_messages = [m for m in messages if (m["from"] == "V" and m["to"] == recipient)]
        
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
                    st.success("✅ Message sent!")
                    st.rerun()
                else:
                    st.warning("Please enter a message!")
    
    elif user_id == "A":
        st.subheader("📥 Messages from V")
        st.markdown("---")
        
        # A can only receive messages from V
        channel_messages = [m for m in messages if (m["from"] == "V" and m["to"] == "A")]
        
        if channel_messages:
            for msg in channel_messages:
                with st.chat_message(msg["from"]):
                    st.write(msg["text"])
                    st.caption(msg["timestamp"])
        else:
            st.info("No messages from V yet.")
        
        st.info("ℹ️ You can only receive messages from V. You cannot send messages.")
    
    elif user_id == "D":
        st.subheader("📥 Messages from V")
        st.markdown("---")
        
        # D can only receive messages from V
        channel_messages = [m for m in messages if (m["from"] == "V" and m["to"] == "D")]
        
        if channel_messages:
            for msg in channel_messages:
                with st.chat_message(msg["from"]):
                    st.write(msg["text"])
                    st.caption(msg["timestamp"])
        else:
            st.info("No messages from V yet.")
        
        st.info("ℹ️ You can only receive messages from V. You cannot send messages.")
