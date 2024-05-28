"""Streamlit frontend for the real-time chatbot service."""

import re

import requests
import streamlit as st
from PIL import Image

LLAMA_PROMPT_TEMPLATE = """<s>[INST] <<SYS>>
You are a friendly Canadian chatbot named 'Curtis Covalent'. Introduce yourself as such.

Please consider the message history below, then provide a brief and polite response.
<</SYS>>
{message_memory} [/INST] """  # NOTE: trailing space is important!

INFO_STRING = """Curtis is a simple chatbot that uses an inference API served by Covalent.

The LLM is prompted as follows:
%s

The `message_memory` is used to insert a fixed  number of previous messages
from the chat history.
""" % "\n\t".join([" "] + LLAMA_PROMPT_TEMPLATE.split("\n"))

# Defaults
MEMORY_LENGTH = 50
MAX_RESPONSE_TOKENS = 275
DEFAULT_API_ADDRESS = ""
DEFAULT_API_KEY = ""

st.set_page_config(
    page_title="Canadian Chatbot: Curtis",
    layout="wide",
)


def _shift_memory():
    # shift the memory buffer to size
    memory = st.session_state.memory
    memory_length = st.session_state.memory_length
    if memory_length > 0:
        st.session_state.memory = memory[-memory_length:]
    else:
        st.session_state.memory = []


def _new_message(role, _prompt):
    # formatting for memory list
    return f"{role.capitalize()}: {_prompt}"


def _add_to_memory(_prompt, role):
    # append to memory and remove oldest if necessary
    memory = st.session_state.memory
    memory.append(_new_message(role, _prompt))


def _format_prompt_with_history(_prompt):
    # insert user message into llama prompt template
    _prompt = _new_message("user", _prompt)
    _prompt = "\n\n".join([_prompt, "Bot: "])
    message_memory = "\n\n".join(st.session_state.memory + [_prompt])
    complete_prompt = LLAMA_PROMPT_TEMPLATE.format(
        message_memory=message_memory
    )
    return complete_prompt


def _clean_gen_text(gen_text):
    # bot completes the prompt, so we remove the prompt from the response
    gen_text = gen_text.rsplit("[/INST]", maxsplit=1)[-1]
    gen_text = gen_text.split("Bot:")[-1]
    gen_text = gen_text.lstrip()

    # Clean up italics. Non-streaming only.
    gen_text = re.sub(r'\*[^*]+\*', '', gen_text)
    gen_text = re.sub(r'\s{2,}', ' ', gen_text)
    return gen_text.strip()


def _check_address():
    if not st.session_state.api_address:
        return "Please provide an API address"
    return None


def get_bot_response(user_input):
    """POST to the Covalent backend and wait for the entire response."""

    complete_prompt = _format_prompt_with_history(user_input)

    api_key = st.session_state.get("api_key") or DEFAULT_API_KEY
    headers = {"x-api-key": api_key} if api_key else {}

    params = {
        "prompt": complete_prompt,
        "max_new_tokens": st.session_state.max_response_tokens,
    }
    ################################
    # POST REQUEST TO FUNCTION SERVE
    ################################
    url = st.session_state.api_address.strip() + "/generate"
    try:
        r = requests.post(url, json=params, headers=headers, timeout=30)
        r.raise_for_status()
    except Exception:
        st.error("Failed to get response. Invalid address?")
    else:
        return _clean_gen_text(r.json())


def stream_bot_response(user_input):
    """POST to the Covalent backend and stream the response."""

    complete_prompt = _format_prompt_with_history(user_input)

    api_key = st.session_state.get("api_key") or DEFAULT_API_KEY
    headers = {"x-api-key": api_key} if api_key else {}

    params = {
        "prompt": complete_prompt,
        "max_new_tokens": st.session_state.max_response_tokens,
    }
    url = st.session_state.api_address.strip() + "/stream"
    try:
        r = requests.post(url, json=params, headers=headers,
                          stream=True, timeout=120)
        r.raise_for_status()
    except Exception:
        st.error("Failed to stream response. Invalid address?")
    else:
        for t in r.iter_content(chunk_size=None):
            s = t.decode()
            s = s.replace('�', '')  # streaming breaks emojis 😭
            if s:
                yield s


def bot_respond(prompt):
    """"Handle bot responses to a prompt."""

    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    if STREAM:
        with st.chat_message("assistant"):
            response = st.write_stream(stream_bot_response(prompt))
    else:
        with st.spinner("Generating..."):
            response = get_bot_response(prompt)

        if response:
            with st.chat_message("assistant"):
                st.markdown(response)

    # Add assistant response to chat log
    if response:
        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )

        # "Easter eggs"
        if " balloons " in response:
            st.balloons()
        if " snow " in response:
            st.snow()

        _add_to_memory(prompt, "user")
        _add_to_memory(response, "bot")
        _shift_memory()


STREAM = st.toggle("Streaming Mode", True)

# BASED ON
# https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps#build-a-simple-chatbot-gui-with-streaming

with st.sidebar:
    st.title("Settings")
    st.text_input("API Address", DEFAULT_API_ADDRESS, key="api_address")
    st.text_input("API Key", DEFAULT_API_KEY, key="api_key", type="password")
    st.slider("Memory Length", 0, 99, MEMORY_LENGTH,
              key="memory_length", on_change=_shift_memory)
    st.slider("Max Response Tokens", 50, 500,
              MAX_RESPONSE_TOKENS, key="max_response_tokens")
    logo = Image.open("./assets/logo.png")
    st.caption("AI powered by")
    st.image(logo, output_format="PNG")

st.title("Curtis 🤖", help=INFO_STRING)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.memory = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Message the bot..."):
    # Add user message to chat log
    if err := _check_address():
        st.error(err)
    else:
        bot_respond(prompt)
