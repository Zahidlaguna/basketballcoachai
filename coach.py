import streamlit as st
from typing import Generator
import os
from groq import Groq

st.set_page_config(page_title="Basketball Coach AI", page_icon=":basketball:", layout="wide")

st.title('Basketball Coach :basketball:')

st.subheader("This is a basketball coach AI, where you can ask questions about basketball plays and get answers, our main goal is to help you understand basketball plays and improve your game!!!",
             divider='grey', anchor=False)


api_key = os.getenv("GROQ_API_KEY")
client = Groq.client(api_key=api_key)

model = "llama3-8b-8192"

if "messages" not in st.session_state:
    st.session_state.messages = []
    
for message in st.session_state.messages:
    avatar = "🏀" if message["role"] == "coach" else "⛹🏾‍♂️"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

def response(completion) -> Generator[str, None, None]:
    for chunk in completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
            
if prompt := st.chat_input("Enter your prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar='⛹🏾‍♂️'):
        st.markdown(prompt)

    # Fetch response from Groq API
    try:
        chat_completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": m["role"],
                    "content": m["content"]
                }
                for m in st.session_state.messages
            ],
            stream=True
        )

        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="🏀"):
            chat_responses_generator = response(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
    except Exception as e:
        st.error(e, icon="🚨")

    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
    else:
        # Handle the case where full_response is not a string
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response})

st.sidebar.title("Previous conversations")
# Save previous conversations in the sidebar
if st.sidebar.button("Save Conversation"):
    with open("/Users/zahidlaguna/Desktop/basketballcoachGPT/conversations.txt", "a") as file:
        for message in st.session_state.messages:
            file.write(f"{message['role']}: {message['content']}\n")
        st.sidebar.success("Conversation saved successfully!")

# Load previous conversations from the sidebar
if st.sidebar.button("Load Conversation"):
    with open("/Users/zahidlaguna/Desktop/basketballcoachGPT/conversations.txt", "r") as file:
        lines = file.readlines()
        st.session_state.messages = []
        for line in lines:
            if ":" in line:
                role, content = line.strip().split(":", 1)
                st.session_state.messages.append({"role": role, "content": content})
        st.sidebar.success("Conversation loaded successfully!")
        
background_image = '''
<style>
[data-testid="stApp"]{
    background-color:#eb690d ;
    background-size: cover;
}
[data-testid="stHeader"]{
    background-color: rgba(0, 0, 0, 0);
}
</style>
'''
st.markdown(background_image, unsafe_allow_html=True)