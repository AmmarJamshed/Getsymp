#!/usr/bin/env python
# coding: utf-8

# In[5]:


import streamlit as st
import requests
from PIL import Image
import base64
from io import BytesIO

# --- Page Config ---
st.set_page_config(page_title="AI Health Symptom Analyzer", page_icon="🧑‍⚕️", layout="centered")

# --- Title ---
st.title("🧑‍⚕️ AI Health Symptom Analyzer")
st.write("Upload an image, and DeepSeek's vision-language model will suggest possible visible symptoms. *(Not a diagnosis!)*")

# --- API Key --- (Hardcoded key, no need for secrets.toml)
API_KEY = "sk-5f72e1b0d1d74e85a16278dd86139dea"
API_URL = "https://api.deepseek.com/v1/vl/completions"

# --- Image uploader ---
uploaded_file = st.file_uploader("📤 Upload your image", type=["jpg", "jpeg", "png"])

def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.convert("RGB").save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

def analyze_image_with_deepseek(image_b64: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-vl",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Based on visible features in this image, list any possible visible health symptoms or concerns. Be cautious and do not provide a diagnosis, only visible clues."
                    }
                ]
            }
        ],
        "temperature": 0.7
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    try:
        result = response.json()
        # Uncomment below line to print raw response in dev mode
        # st.json(result)

        if 'choices' in result:
            return result['choices'][0]['message']['content']
        elif 'error' in result:
            raise Exception(result['error'].get('message', 'Unknown error from API'))
        else:
            raise Exception(f"Unexpected API response: {result}")
    except Exception as e:
        raise Exception(f"DeepSeek API error: {e}")

# --- Main logic ---
if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        image_b64 = image_to_base64(image)
        with st.spinner("Analyzing image for visible symptoms..."):
            result = analyze_image_with_deepseek(image_b64)

        st.success("✅ Analysis complete!")
        st.markdown(f"**📝 Possible Visible Symptoms (Not a diagnosis):**\n\n{result}")

    except Exception as e:
        st.error(f"Error: {e}")

