import streamlit as st
import http.client
import cv2
import numpy as np
from PIL import Image
from txtai.pipeline import Summary
from PyPDF2 import PdfReader

# Helper function to call the handwriting OCR API
def call_handwriting_api(image_bytes):
    conn = http.client.HTTPSConnection("pen-to-print-handwriting-ocr.p.rapidapi.com")
    
    boundary = "----011000010111000001101001"
    
    # Prepare the payload properly with the image content
    payload = (
        f"--{boundary}\r\n"
        "Content-Disposition: form-data; name=\"srcImg\"; filename=\"image.jpg\"\r\n"
        "Content-Type: image/jpeg\r\n\r\n"
    ).encode("utf-8") + image_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")
    
    headers = {
        'x-rapidapi-key': "2a9c405c14mshc66d154f6b62900p1551d6jsn8c3e9ee14c79",
        'x-rapidapi-host': "pen-to-print-handwriting-ocr.p.rapidapi.com",
        'Content-Type': f"multipart/form-data; boundary={boundary}"
    }

    conn.request("POST", "/recognize/", payload, headers)
    res = conn.getresponse()
    data = res.read()
    
    return data.decode("utf-8")

# Function to format and display the detected text
def display_detected_text(text):
    st.markdown(
        f"""
        <div style="border:2px solid #4CAF50; padding: 10px; border-radius: 5px;">
            <h3 style="color:#4CAF50;">Detected Text:</h3>
            <p style="font-family:Courier; font-size:16px;">{text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Streamlit pages
def home_page():
    st.title("Doctor's Handwriting Detection and Summarization")
    st.image("img/doc.jpeg")
    st.markdown('''## Introduction and Overview:

Welcome to the Handwriting OCR App, a modern solution designed to digitize handwritten text effortlessly using cutting-edge Optical Character Recognition (OCR) technology. Built with Streamlit and powered by an external API, this app offers an intuitive interface for extracting text from both uploaded images and live webcam feeds. Whether you're scanning notes, letters, or any handwritten content, this app ensures accurate and quick conversion of handwritten text into digital form.

The app utilizes a three-page navigation system: the Home Page introduces the app, the Upload Page allows users to submit an image for text extraction, and the Webcam Page offers real-time detection using a webcam. The backend is powered by the Pen-to-Print Handwriting OCR API, which processes images and returns detected text in a user-friendly format. The API call is crafted with multipart form data to ensure seamless handling of image uploads, while the app’s frontend is stylized to deliver clear, readable results.

Overall, this project combines simplicity and functionality, providing a robust platform for converting handwritten content into machine-readable text with ease.''')

def upload_page():
    st.title("Upload Handwriting Image")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image", use_column_width=True)

        # Convert image to bytes
        img_bytes = uploaded_file.getvalue()
        result = call_handwriting_api(img_bytes)
        
        import json
        result_data = json.loads(result)
        
        detected_text = result_data.get("value", "No text detected.")
        display_detected_text(detected_text)

def summarize_page():
    st.title("Summarize Text & Document")
    
    choice = st.selectbox("Select your choice", ["Summarize Text", "Summarize Document"])
    
    @st.cache_resource
    def text_summary(text):
        summary = Summary()
        return summary(text)
    
    def extract_text_from_pdf(file_path):
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            page = reader.pages[0]
            text = page.extract_text()
        return text

    if choice == "Summarize Text":
        st.subheader("Summarize Text")
        input_text = st.text_area("Enter your text here")
        if st.button("Summarize Text"):
            col1, col2 = st.columns([1,1])
            with col1:
                st.markdown("**Your Input Text**")
                st.info(input_text)
            with col2:
                st.markdown("**Summary Result**")
                result = text_summary(input_text)
                st.success(result)

    elif choice == "Summarize Document":
        st.subheader("Summarize Document")
        input_file = st.file_uploader("Upload your document here", type=['pdf'])
        if input_file and st.button("Summarize Document"):
            with open("doc_file.pdf", "wb") as f:
                f.write(input_file.getbuffer())
            
            col1, col2 = st.columns([1,1])
            with col1:
                extracted_text = extract_text_from_pdf("doc_file.pdf")
                st.markdown("**Extracted Text is Below:**")
                st.info(extracted_text)
            with col2:
                doc_summary = text_summary(extracted_text)
                st.markdown("**Summary Result**")
                st.success(doc_summary)

# Streamlit page navigation
st.sidebar.title("Navigation")
options = st.sidebar.radio("Select a page:", ["Home", "Upload Image", "Summarize Text & Document"])

if options == "Home":
    home_page()
elif options == "Upload Image":
    upload_page()
elif options == "Summarize Text & Document":
    summarize_page()
