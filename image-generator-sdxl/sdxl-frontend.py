"""Streamlit frontend for the real-time image generator service."""

import base64
import io

import requests
import streamlit as st
from PIL import Image
from st_keyup import st_keyup

# Initialize session state
if "last_prompt" not in st.session_state:
    st.session_state["last_prompt"] = ""

# Constants
SEED = 2
DEFAULT_API_ADDRESS = ""
DEFAULT_API_KEY = ""


def _check_address():
    if not st.session_state.get("api_address") and not DEFAULT_API_ADDRESS:
        return "Error: Please provide an API address"
    return None


def make_image(_prompt, address):
    """POST to the Covalent service backend to generate an image."""

    if err := _check_address():
        st.error(err)
        return None

    address = address.strip()
    api_key = st.session_state.get("api_key") or DEFAULT_API_KEY
    headers = {"x-api-key": api_key} if api_key else {}
    json_ = {"prompt": _prompt, "num_inference_steps": 2}
    try:
        response = requests.post(
            address + "/text-to-image",
            json=json_,
            headers=headers,
            timeout=120,
        )
        response.raise_for_status()
    except Exception:
        st.error(f"Error: Failed to get image from '{address}'")
        return None

    image_arr = io.BytesIO(base64.b64decode(response.json()))
    return Image.open(image_arr)


st.set_page_config(page_title="Real-Time Image Generation")

left, middle, last = st.columns([1, 10, 1])

# Sidebar for settings
with st.sidebar:
    st.title("Settings")
    st.text_input("API Address", DEFAULT_API_ADDRESS, key="api_address")
    st.text_input("API Key", DEFAULT_API_KEY, key="api_key", type="password")
    logo = Image.open("./assets/logo.png")
    st.caption("AI powered by")
    st.image(logo, output_format="PNG")

with middle:

    # Main content area
    st.title("Real-Time Image Generator")

    # Prompt input and image display
    user_prompt = st_keyup(
        "Enter a prompt:",
        key="0",
        debounce=300,
    )
    if user_prompt and user_prompt != st.session_state["last_prompt"]:
        st.session_state["last_prompt"] = user_prompt
        prompt = f"<random seed {SEED}> {user_prompt}"
        img = make_image(prompt, st.session_state.api_address)
        _, col, _ = st.columns([1, 40, 1])
        with col:
            if img:
                st.image(
                    img,
                    caption=user_prompt,
                    use_column_width=False,
                    output_format="JPEG",
                    width=500,
                )
