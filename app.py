import streamlit as st
import fitz  # PyMuPDF
from huggingface_hub import InferenceClient
import openai
import time
import os
from dotenv import load_dotenv

# --- تنظیمات اولیه ---
st.set_page_config(page_title="مترجم PDF هوشمند", layout="wide")
st.title("📖 مترجم PDF با DeepSeek و OpenAI")

# راست‌چین کردن متن فارسی
st.markdown("""
<style>
p, div, h1, h2, h3, h4, h5, h6 {
    direction: rtl;
    text-align: right;
    font-family: 'Segoe UI', Tahoma, sans-serif;
}
</style>
""", unsafe_allow_html=True)

# --- نوار کناری برای تنظیمات ---
with st.sidebar:
    st.header("تنظیمات")
    model_choice = st.radio(
        "انتخاب مدل ترجمه:",
        ["DeepSeek (رایگان)", "OpenAI (نیاز به API)"]
    )

# --- آپلود فایل PDF ---
uploaded_file = st.file_uploader("فایل PDF خود را آپلود کنید", type="pdf")

if uploaded_file:
    # استخراج متن از PDF
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    
    st.success(f"✅ {len(doc)} صفحه با موفقیت خوانده شد!")

    # --- توابع ترجمه ---
    def translate_with_deepseek(text):
        load_dotenv()
        client = InferenceClient(
            model="arvan/DeepSeek-VL-7B-v1.5-fa",
            token=os.getenv("HUGGINGFACE_TOKEN")
        )
        prompt = f"""
        شما یک مترجم حرفه‌ای هستید. متن زیر را به فارسی روان ترجمه کنید:
        {text}
        """
        response = client.text_generation(prompt, max_new_tokens=1500)
        return response

    def translate_with_openai(text):
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "متن را به فارسی روان ترجمه کن."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content

    # --- دکمه ترجمه ---
    if st.button("ترجمه کن"):
        with st.spinner("در حال ترجمه..."):
            try:
                if model_choice == "DeepSeek (رایگان)":
                    translated = translate_with_deepseek(text)
                    time.sleep(2)  # جلوگیری از Rate Limit
                else:
                    translated = translate_with_openai(text)
                
                st.subheader("ترجمه:")
                st.write(translated)
                st.download_button("دانلود ترجمه", translated, file_name="ترجمه.txt")
            except Exception as e:
                st.error(f"خطا: {str(e)}")
