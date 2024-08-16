#chainlit

import streamlit as st
import asyncio
import websockets
import json
import base64
from streamlit_float import float_init

float_init()


# async def retrieve_bot_response(text, image):
#     async with websockets.connect(
#             "ws://192.168.208.1:8000/api/v1/chat/tools") as websocket:
#         message_data = {"message": text, "image": image}
#         json_data = json.dumps(message_data)
#         last_response = ""
#         stream_data = ""
#         print("stream_data start", stream_data)
#         await websocket.send(json_data)
#         counter = 0
#         stream_str = ""
#         last_response = ""
#         # with st.empty():
#         with st.empty() as placeholder:

#             try:
#                 # 收到第一個訊息後，回延遲；之後才回復
#                 while True:
#                     counter += 1
#                     response = await asyncio.wait_for(websocket.recv(),
#                                                       timeout=36000)
#                     response = json.loads(response)
#                     print(f'response:{response}')

#                     # if "error" in response:
#                     #     stream_data = response["error"]
#                     #     break
#                     # if response["response"] == "":
#                     #     break
#                     placeholder.text(response)
#                     last_response = response
#                     # stream_data = st.write(stream_str)
#             except asyncio.TimeoutError:
#                 # st.warning("Connection timed out. Closing the connection.")
#                 print("Connection timed out. Closing the connection.")
#         # print("stream_data", stream_data, type(stream_data))

#         # return last_response if stream_data in ["", None, "None"
#         #                                         ] else stream_data
#         return last_response
async def retrieve_bot_response(text, image):
    #
    #ws://192.168.208.1:8000/api/v1/chat/tools
    async with websockets.connect("ws://127.0.0.1:8000/api/v1/chat/tools", ping_timeout=60, ping_interval=10) as websocket:
        message_data = {"message": text, "image": image}
        json_data = json.dumps(message_data)
        await websocket.send(json_data)

        accumulated_response = ""

        # with st.empty():
        try:
            while True:
                response = await asyncio.wait_for(websocket.recv(), timeout=300)
                # response = await websocket.recv()
                response = json.loads(response)
                print(f'response:{response}')

                if "END" in response:
                    accumulated_response =response.get('END')
                    st.write(f'<p style="background-color:#FFF380;">{accumulated_response}</p>', unsafe_allow_html=True)
                else:
                    # accumulated_response = json.dumps(response)
                    accumulated_response = response
                    st.markdown(f'<p style="background-color:#FAFAD2;">{accumulated_response}</p>', unsafe_allow_html=True)

                

        except asyncio.TimeoutError:
            st.warning("Connection timed out. Closing the connection.")
    
        return accumulated_response


st.title("飲食資料確認")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
# prompt = st.chat_input("What is up?")
# prompt = "食物圖片如下:"

# Accept image upload
uploaded_file = st.file_uploader("Upload an image",
                                 type=["png", "jpg", "jpeg"])

# Prepare the image data if an image is uploaded
image_data = None
if uploaded_file is not None:
    image_data = base64.b64encode(uploaded_file.read()).decode("utf-8")

# Process the input and image if provided
# if prompt or image_data:
st.empty()
if image_data:
    # Add user message to chat history
    prompt = "食物圖片如下"
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
        print("full_response", full_response, type(full_response))
        # message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })
