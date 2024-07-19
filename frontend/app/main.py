import streamlit as st
import asyncio
import websockets
import json
import base64
from streamlit_float import float_init

float_init()


async def retrieve_bot_response(text, image):
    async with websockets.connect(
            "ws://192.168.8.114:8000/api/v1/chat/tools") as websocket:
        message_data = {"message": text, "image": image}
        json_data = json.dumps(message_data)

        await websocket.send(json_data)
        counter = 0
        with st.empty():
            stream_data = ""
            try:
                while True:
                    counter += 1
                    response = await asyncio.wait_for(websocket.recv(),
                                                      timeout=20)
                    response = json.loads(response)

                    if "error" in response:
                        stream_data = response["error"]
                        break

                    if response["sender"] == "bot":
                        stream_data = (
                            response["message"]["body"][0]["items"][0]["text"]
                            if counter != 2 else "")
                        st.markdown(stream_data)

                    if response["type"] == "end":
                        break
                st.markdown(stream_data)
            except asyncio.TimeoutError:
                st.warning("Connection timed out. Closing the connection.")

        return stream_data


st.title("Simple chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
prompt = st.chat_input("What is up?")

# Accept image upload
uploaded_file = st.file_uploader("Upload an image",
                                 type=["png", "jpg", "jpeg"])

# Prepare the image data if an image is uploaded
image_data = None
if uploaded_file is not None:
    image_data = base64.b64encode(uploaded_file.read()).decode("utf-8")

# Process the input and image if provided
if prompt or image_data:
    # Add user message to chat history
    user_message = {"role": "user", "content": prompt}
    if image_data:
        user_message["image"] = image_data
    st.session_state.messages.append(user_message)

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
        if image_data:
            st.image(uploaded_file)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = asyncio.new_event_loop().run_until_complete(
            retrieve_bot_response(prompt, image_data))

    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })
