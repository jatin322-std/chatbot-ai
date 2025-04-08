import streamlit as st
import google.generativeai as genai
import os

# Fetch the Gemini API key securely from Streamlit secrets
GEMINI_API_KEY = st.secrets["api_keys"]["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# Set up the model
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1000,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# System prompt with greeting handling
SYSTEM_PROMPT = """You are a knowledgeable and friendly sports equipment advisor. Your role is to:

1. First respond appropriately to greetings (hi, hello, etc.) with a friendly welcome.
2. Help users find sports gear based on:
   - The sport they're interested in
   - Their skill level (beginner, intermediate, advanced)
   - Their budget range
   - Any specific preferences (brand, material, etc.)

For greetings, respond warmly but briefly, then ask how you can help with sports equipment.

For equipment questions:
- Ask clarifying questions if needed.
- Provide 2-3 options with:
  - Product names (if known).
  - Key features.
  - Price ranges.
  - Where to buy (general suggestions).

Keep responses friendly, concise but informative, and always prioritize safety.
"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi there! I'm your sports equipment assistant. How can I help you today?"
        }
    ]

# Display chat messages
st.title("🏆 Sports Equipment Advisor")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about sports equipment..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare conversation history for Gemini
    conversation_history = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}]
    conversation_history.append({"role": "model", "parts": [{"text": "Hi there! I'm your sports equipment assistant. How can I help you today?"}]})
    
    for msg in st.session_state.messages[1:]:  # Skip the initial greeting
        if msg["role"] == "user":
            conversation_history.append({"role": "user", "parts": [{"text": msg["content"]}]})
        else:
            conversation_history.append({"role": "model", "parts": [{"text": msg["content"]}]})

    # Generate response
    try:
        response = model.generate_content(conversation_history)
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Sorry, I'm having trouble responding. Please try again."
        })
