import numpy as np, pandas as pd
from flask import Flask, jsonify, render_template

app = Flask(__name__)
df = pd.read_csv("latihan1.csv")
NUM = [c for c in df.columns if c not in ("Student_ID", "Gender")]


def desc(s):
    q1, q3 = s.quantile([.25, .75]); iqr = q3 - q1
    v = dict(mean=s.mean(), median=s.median(), mode=s.mode().iloc[0], std=s.std(), var=s.var(),
             min=s.min(), max=s.max(), range=s.max() - s.min(), q1=q1, q3=q3, iqr=iqr,
             skew=s.skew(), cv=s.std() / s.mean() * 100,
             outlier=((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum())
    return {k: round(float(x), 2) for k, x in v.items()}


def slope(x, y):
    return float(np.polyfit(df[x], df[y], 1)[0])


def insights():
    g = df.groupby("Gender")[NUM].mean(); r = df[NUM].corr()["Exam_Score"]
    lo = df[df.Exam_Score < 60]; age = df.groupby("Age").mean(numeric_only=True)
    tier = df.groupby(pd.cut(df.Study_Hours, [4, 8, 12, 17])).Exam_Score.mean()
    n_att, n_slp, n_scr = (df.Attendance < 80).sum(), (df.Sleep_Hours < 6).sum(), (df.Screen_Hours > 7).sum()
    return [
        dict(t="1. Jadikan jam belajar target utama", d=f"Tiap +1 jam belajar berasosiasi dengan ±{slope('Study_Hours','Exam_Score'):.1f} poin nilai (r = {r.Study_Hours:.2f}). Mahasiswa belajar ≤8 jam rata-rata {tier.iloc[0]:.0f}, sedangkan >12 jam {tier.iloc[2]:.0f}.",
             k="Wajibkan kelompok belajar / jadwal belajar terstruktur, dengan target minimal 10–12 jam per minggu untuk yang di bawah rata-rata."),
        dict(t="2. Pantau kehadiran sebagai sistem peringatan dini", d=f"Kehadiran berkorelasi sangat kuat dengan nilai (r = {r.Attendance:.2f}); tiap +1% ≈ +{slope('Attendance','Exam_Score'):.1f} poin. Ada {n_att} mahasiswa dengan kehadiran <80%.",
             k="Tetapkan ambang kehadiran 80%; di bawahnya otomatis dihubungi dosen wali."),
        dict(t="3. Program khusus mahasiswa laki-laki", d=f"Nilai F {g.Exam_Score.F:.1f} vs M {g.Exam_Score.M:.1f}. M belajar {g.Study_Hours.M:.1f} jam (F {g.Study_Hours.F:.1f}), tidur {g.Sleep_Hours.M:.1f} jam (F {g.Sleep_Hours.F:.1f}), layar {g.Screen_Hours.M:.1f} jam (F {g.Screen_Hours.F:.1f}).",
             k="Rancang pendampingan manajemen waktu dan kebiasaan belajar yang menyasar kelompok M."),
        dict(t="4. Batasi waktu layar", d=f"{n_scr} mahasiswa memakai layar >7 jam/hari. Tiap +1 jam layar ≈ {slope('Screen_Hours','Exam_Score'):.1f} poin nilai (r = {r.Screen_Hours:.2f}).",
             k="Kampanye digital wellbeing dan tantangan pengurangan layar non-akademik."),
        dict(t="5. Perbaiki kebiasaan tidur", d=f"{n_slp} mahasiswa tidur <6 jam. Tidur berkorelasi positif dengan nilai (r = {r.Sleep_Hours:.2f}); rata-rata tidur kelompok bernilai <60 hanya {lo.Sleep_Hours.mean():.1f} jam.",
             k="Edukasi sleep hygiene, hindari jadwal kuliah/ujian yang terlalu pagi bila memungkinkan."),
        dict(t="6. Dampingi mahasiswa tingkat akhir", d=f"Nilai turun dari {age.Exam_Score[18]:.1f} (usia 18) ke {age.Exam_Score[22]:.1f} (usia 22); pengeluaran naik {age.Monthly_Spending[18]:.0f} → {age.Monthly_Spending[22]:.0f}, kepuasan turun {age.Satisfaction[18]:.1f} → {age.Satisfaction[22]:.1f}.",
             k="Sediakan mentoring, beasiswa kerja kampus, atau konseling keuangan untuk usia 21–22."),
        dict(t="7. Identifikasi mahasiswa berisiko", d=f"{len(lo)} mahasiswa bernilai <60: rata-rata belajar {lo.Study_Hours.mean():.1f} jam, tidur {lo.Sleep_Hours.mean():.1f} jam, hadir {lo.Attendance.mean():.0f}%, layar {lo.Screen_Hours.mean():.1f} jam, kepuasan {lo.Satisfaction.mean():.1f}.",
             k="Gunakan profil ini sebagai kriteria skrining awal semester untuk remedial dan konseling."),
        dict(t="⚠ Catatan kehati-hatian", d="Korelasi sangat tinggi (r > 0.95) antar hampir semua variabel jarang terjadi di data nyata dan menandakan variabel saling tumpang tindih atau data bersifat sintetis. Korelasi juga bukan bukti sebab-akibat (misalnya perbedaan gender ikut mendorong semua pola).",
             k="Lakukan program percontohan (pilot) dan evaluasi sebelum kebijakan skala besar; cek lagi dengan data semester berikutnya."),
    ]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def data():
    cols = {}
    for c in NUM:
        cnt, ed = np.histogram(df[c], bins=10)
        cols[c] = dict(stats=desc(df[c]), hist=cnt.tolist(), bins=[f"{a:.1f}-{b:.1f}" for a, b in zip(ed[:-1], ed[1:])])
    sat = df.Satisfaction.value_counts().sort_index()
    age = df.groupby("Age").Exam_Score.mean().round(1)
    r = df[NUM].corr()["Exam_Score"].drop("Exam_Score").round(2)
    return jsonify(
        n=len(df), cols=cols, gender=df.Gender.value_counts().to_dict(),
        sat=dict(labels=[f"Skor {i}" for i in sat.index], values=sat.tolist()),
        age=dict(labels=[str(i) for i in age.index], values=age.tolist()),
        corr=dict(labels=r.index.tolist(), values=r.tolist()),
        gmeans=df.groupby("Gender")[NUM].mean().round(2).to_dict(),
        rows=df[NUM].to_dict("records"), insights=insights())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
