import streamlit as st
import pandas as pd
import numpy as np

Konfigurasi halaman
st.set_page_config(page_title="Dashboard Statistik Deskriptif", layout="wide")
st.title("📊 Dashboard Statistik Deskriptif")

Baca Data
try:
    df = pd.read_csv("latihan1.csv")
except FileNotFoundError:
    st.error("File 'latihan1.csv' tidak ditemukan. Pastikan file sudah di-upload ke repositori GitHub.")
    st.stop()

Tentukan Kolom Numerik
(Mengabaikan kolom 'Student_ID' dan 'Gender' seperti di kode Flask Anda)
NUM = [c for c in df.columns if c not in ("Student_ID", "Gender")]

Fungsi Statistik (Logika dari kode Flask Anda)
def hitung_statistik(s):
    q1, q3 = s.quantile([.25, .75])
    iqr = q3 - q1
    return {
        "Mean": s.mean(),
        "Median": s.median(),
        "Modus": s.mode().iloc[0] if not s.mode().empty else np.nan,
        "Min": s.min(),
        "Max": s.max(),
        "Range": s.max() - s.min(),
        "Std Dev": s.std(),
        "Varians": s.var(),
        "Skewness": s.skew(),
        "CV (%)": (s.std() / s.mean()) * 100 if s.mean() != 0 else np.nan,
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "Outlier": ((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum()
    }

Hitung untuk Semua Kolom Numerik
hasil = {}
for col in NUM:
    hasil[col] = hitung_statistik(df[col])

Tampilkan dalam DataFrame
df_hasil = pd.DataFrame(hasil).T
df_hasil = df_hasil.round(2)  # Bulatkan 2 desimal

st.subheader("📈 Ringkasan Statistik")
st.dataframe(df_hasil, use_container_width=True)

(Opsional) Tampilkan Data Mentah
with st.expander("🔍 Lihat Data Mentah"):
    st.dataframe(df, use_container_width=True)
