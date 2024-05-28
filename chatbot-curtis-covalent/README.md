# Streamlit Chatbot

<div align="center">
<img src="./streamlit-chatbot-demo.gif", width="60%">
</div>

## Instructions
1. Make a conda environment with:
```
accelerate==0.29.1
covalent-cloud==0.54.0
cloudpickle=2.2.1
ipywidgets==8.1.2
streamlit==1.33.0
torch==2.2.2
transformers==4.39.3
```

2. Run the deploy notebook.

3. Copy paste the deployment address (e.g. `"https://fn.int.covalent.xyz/0662098d4603432d123456789"`) into the streamlit app script.

4. Run or deploy the streamlit app.

## Info

The notebook and script together are designed to run a Llama-2 chatbot. By default, the app runs in live streaming mode.

There are two global settings in the app script:
```python
MESSAGE_MEMORY_SIZE = 100
MAX_RESPONSE_TOKENS = 500
```
The memory size determines the number of prior messages (one prompt-response pair equals 2 messages) that the chat bot "remembers". The chatbot's memory lives on the Streamlit app side. Refreshing the app window will clear the bot's memory.

The number of response tokens determines the maximum length of the response. The chatbot should reasonably terminate responses when appropriate, so a large number is recommended to avoid premature truncation.

The model is prompted with the following. This format is recommended for Llama-2.
```python
LLAMA_PROMPT_TEMPLATE = """<s>[INST] <<SYS>>
You are a friendly Canadian chat bot named 'Curtis Covalent'.

Please consider the message history below, and provide brief and polite response.
<</SYS>>
{message_memory} [/INST] """  # NOTE: trailing space is important!
```

The `message_memory` above is a formatted reproduction of the chat displayed to the user (with a maximum context length of `MAX_MEMORY_SIZE` messagess).

## Fun stuff

The app will play a screen animation if the words "snow" or "balloons" are detected in the bot's response.

## Debugging

- Check the `env` passed to the executor. Make sure it is valid. If the environment is old, try re-creating it in the UI or creating a replacement.