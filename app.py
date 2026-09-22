import streamlit as st
import google.generativeai as genai
from gtts import gTTS

# Tampilan Halaman Web
st.set_page_config(page_title="Memorial Video Call AI", layout="wide")
st.title("🎥 Memorial Video Call AI (Prototipe)")

# Sidebar untuk Input
with st.sidebar:
    st.header("⚙️ Pengaturan")
    gemini_api_key = st.text_input("Gemini API Key", type="password")
    uploaded_photo = st.file_uploader("Unggah Foto Mendiang", type=["jpg", "png", "jpeg"])
    
    st.markdown("---")
    system_instruction = st.text_area(
        "Cerita / Kepribadian Mendiang", 
        value="Kamu adalah orang tersayang yang sudah meninggal. Jawablah pesan pengguna dengan hangat, penuh kasih, dan singkat seolah sedang bicara di panggilan video."
    )

# Area Video Call
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Kamera Pengguna")
    st.info("Kamera Aktif (Anda)")

with col2:
    st.subheader("🕊️ Mendiang")
    if uploaded_photo:
        st.image(uploaded_photo, use_container_width=True)
    else:
        st.warning("Silakan unggah foto di sidebar terlebih dahulu.")

st.markdown("---")

# Area Chat
user_message = st.text_input("Ketik pesan Anda untuk memulai percakapan:")

if st.button("Kirim Pesan") and user_message:
    if not gemini_api_key:
        st.error("Masukkan Gemini API Key terlebih dahulu di sidebar!")
    else:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-3.6-flash')
            
            prompt = f"{system_instruction}\n\nPengguna berkata: {user_message}\nBalasan singkat:"
            response = model.generate_content(prompt)
            
            st.success(f"**Mendiang:** {response.text}")
            
            tts = gTTS(text=response.text, lang='id')
            tts.save("response.mp3")
            
            audio_file = open("response.mp3", "rb")
            st.audio(audio_file.read(), format="audio/mp3")
            
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
