import streamlit as st
from groq import Groq
from docxtpl import DocxTemplate
from datetime import datetime
import io

# --- KONFIGURASI API KEY BARU ---
client = Groq(api_key="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")

st.set_page_config(page_title="Rafi Makalah AI", page_icon="🎓")

# --- KEAMANAN (Password) ---
# Agar orang lain tidak menghabiskan kuota API kamu
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    pw = st.text_input("Masukkan Password Akses:", type="password")
    if pw == "rafi2006": # Kamu bisa ganti password ini
        st.session_state["authenticated"] = True
        st.rerun()
    else:
        st.info("Halaman ini dikunci. Masukkan password untuk melanjutkan.")
        st.stop()

# --- TAMPILAN WEB ---
st.title("🎓 UIN Alauddin Makalah Gen")
st.write("Dibuat oleh: **Muh Rafiuddin S** (Sistem Informasi)")

with st.form("main_form"):
    judul = st.text_input("Judul Makalah")
    matkul = st.text_input("Mata Kuliah")
    dosen = st.text_input("Nama Dosen")
    
    col1, col2 = st.columns(2)
    with col1:
        nama_user = st.text_input("Nama Penyusun", value="Muh Rafiuddin S")
    with col2:
        nim_user = st.text_input("NIM", value="24023")
        
    submit = st.form_submit_button("Generate & Download")

def generate_text(prompt):
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Asisten akademik formal UIN. Tanpa markdown, gunakan sitasi."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

if submit and judul:
    with st.spinner("Sedang memproses... Tunggu sebentar ya, Rafi."):
        try:
            # 1. Generate Konten
            latar = generate_text(f"Buat latar belakang akademik untuk {judul}")
            rumusan = generate_text(f"Sebutkan 3 rumusan masalah untuk {judul} (tanpa nomor)")
            tujuan = generate_text(f"Sebutkan 3 tujuan penelitian untuk {judul} (tanpa nomor)")
            isi1 = generate_text(f"Jelaskan teori dasar {judul}")
            pustaka = generate_text(f"Daftar pustaka APA Style A-Z untuk {judul}")

            # 2. Load Template
            doc = DocxTemplate("template_uin.docx")
            context = {
                'judul': judul.upper(), 'matkul': matkul, 'dosen': dosen,
                'nama': nama_user, 'penyusun': nama_user, 'nim': nim_user,
                'tahun': 2026, 'latar_belakang': latar, 'rumusan_masalah': rumusan,
                'tujuan_penelitian': tujuan, 'isi_sub_1': isi1, 'daftar_pustaka': pustaka
            }
            doc.render(context)

            # 3. Kirim ke Memory
            output = io.BytesIO()
            doc.save(output)
            output.seek(0)
            
            st.success("✅ Makalah siap didownload!")
            st.download_button(
                label="📥 Download File Word",
                data=output,
                file_name=f"Makalah_{judul[:20]}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")