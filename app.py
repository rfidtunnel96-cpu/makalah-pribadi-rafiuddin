import streamlit as st
from groq import Groq
from docxtpl import DocxTemplate
from datetime import datetime
import io

# --- KONFIGURASI API ---
# Menggunakan API Key yang kamu berikan
client = Groq(api_key="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")

# Konfigurasi Halaman Browser
st.set_page_config(page_title="Rafi Makalah AI", page_icon="📝", layout="centered")

# --- SISTEM KEAMANAN ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Akses Terkunci")
    pw = st.text_input("Masukkan Password Akses:", type="password")
    if pw == "rafi2006":
        st.session_state["authenticated"] = True
        st.rerun()
    else:
        if pw: st.error("Password Salah!")
        st.info("Silakan masukkan password untuk menggunakan generator.")
        st.stop()

# --- TAMPILAN UTAMA ---
st.title("📝 UIN Alauddin Makalah Gen")
st.write(f"Halo, **{st.session_state.get('user', 'Rafi')}**! Siap buat makalah hari ini?")

with st.form("generator_form"):
    st.subheader("📌 Identitas & Judul")
    judul = st.text_area("Judul Makalah (Lengkap)", placeholder="Contoh: Analisis Keamanan Jaringan pada Server Kampus")
    
    col1, col2 = st.columns(2)
    with col1:
        matkul = st.text_input("Mata Kuliah")
        nama_user = st.text_input("Nama Penyusun", value="Muh Rafiuddin S")
    with col2:
        dosen = st.text_input("Dosen Pengampu")
        nim_user = st.text_input("NIM", value="24023")
        
    submit = st.form_submit_button("🚀 Generate Makalah Sekarang")

def generate_ai_text(prompt):
    """Fungsi untuk mengambil konten dari Llama 3 via Groq"""
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Anda adalah asisten akademik UIN Alauddin. Tulis formal, tanpa markdown (**), gunakan sitasi (Nama, Tahun). Jangan beri nomor urut di awal kalimat."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Gagal mendapatkan data AI: {e}"

if submit:
    if not judul or not matkul:
        st.warning("Judul dan Mata Kuliah wajib diisi!")
    else:
        with st.spinner("⏳ AI sedang menyusun makalah... Mohon tunggu."):
            try:
                # 1. GENERATE KONTEN (Bab 1, 2, 3 & Pustaka)
                latar = generate_ai_text(f"Buat latar belakang akademik untuk makalah {judul}")
                rumusan = generate_ai_text(f"Buat 3 rumusan masalah untuk {judul} tanpa angka di depan")
                tujuan = generate_ai_text(f"Buat 3 tujuan penelitian untuk {judul} tanpa angka di depan")
                
                # Pembahasan Bab 2
                isi1 = generate_ai_text(f"Jelaskan landasan teori dan tinjauan pustaka lengkap untuk {judul}")
                isi2 = generate_ai_text(f"Berikan analisis dan pembahasan utama terkait implementasi {judul}")
                
                # Penutup & Pustaka
                kesimpulan = generate_ai_text(f"Buat kesimpulan singkat untuk makalah {judul}")
                pustaka = generate_ai_text(f"Buat Daftar Pustaka APA Style urut A-Z untuk {judul}. Berikan jarak antar sumber.")

                # 2. PROSES KE TEMPLATE WORD
                # Pastikan file template_uin.docx sudah diupload di GitHub
                doc = DocxTemplate("template_uin.docx")
                
                context = {
                    'judul': judul.upper(),
                    'matkul': matkul,
                    'dosen': dosen,
                    'nama': nama_user,
                    'penyusun': nama_user,
                    'nim': nim_user,
                    'tahun': datetime.now().year,
                    'latar_belakang': latar,
                    'rumusan_masalah': rumusan,
                    'tujuan_penelitian': tujuan,
                    'sub_bab_1': "Landasan Teori",
                    'isi_sub_1': isi1,
                    'sub_bab_2': "Analisis Pembahasan",
                    'isi_sub_2': isi2,
                    'kesimpulan': kesimpulan,
                    'daftar_pustaka': pustaka
                }
                
                # Render dengan jinja_env agar tidak error jika ada tag yang hilang
                doc.render(context)

                # 3. OUTPUT KE STREAMLIT
                bio = io.BytesIO()
                doc.save(bio)
                bio.seek(0)
                
                st.success("✅ Makalah Berhasil Disusun!")
                st.download_button(
                    label="📥 Klik untuk Download Makalah (.docx)",
                    data=bio,
                    file_name=f"Makalah_{nama_user}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"Terjadi kesalahan teknis: {e}")
                st.info("Pastikan file 'template_uin.docx' sudah di-upload ke GitHub.")
