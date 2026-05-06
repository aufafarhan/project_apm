# PROJECT CONTEXT — AI Agent Reference File

> File ini dibuat agar AI agent dapat langsung memahami konteks proyek tanpa penjelasan ulang.
> Baca seluruh file ini sebelum membantu pengerjaan proyek.

---

## 1. IDENTITAS PROYEK

| Field | Detail |
|---|---|
| **Mata Kuliah** | (sesuaikan dengan nama mata kuliah) |
| **Dosen Pengampu** | Febby Apri Wenando & Aina Hubby Aziira |
| **Institusi** | Departemen Sistem Informasi, Universitas Andalas |
| **Anggota Tim** | Annisa Revalina Harahap, Reva Hanum Salsabila, Farhan Aufa, Nailah Khaira Ahmad |
| **Topik** | Prediksi Jumlah Penduduk Miskin Kabupaten/Kota di Provinsi Jawa Barat Menggunakan Machine Learning Berdasarkan Indikator Makro Pembangunan (Tahun 2018–2024) |

---

## 2. ARSITEKTUR SISTEM

```
project-root/
│
├── ml/
│   ├── apm.ipynb               # Notebook utama ML (SUDAH SELESAI)
│   ├── model_rfr.pkl           # Model terbaik hasil training (akan di-generate)
│   └── data/
│       └── dataset.csv         # Dataset BPS format long (sudah dirapikan)
│
├── app/
│   ├── app.py                  # Backend Flask (PERLU DIBUAT)
│   ├── templates/
│   │   └── index.html          # Frontend HTML/CSS (PERLU DIBUAT)
│   └── static/
│       └── style.css           # (opsional, bisa inline di HTML)
│
├── requirements.txt            # Dependencies Python
├── Procfile                    # Untuk deploy ke Heroku/Railway (opsional)
└── PROJECT_CONTEXT.md          # File ini
```

---

## 3. DATASET

- **Sumber:** Badan Pusat Statistik (BPS)
- **Format:** CSV, Long Format (sudah dirapikan)
- **Cakupan:** 27 Kabupaten/Kota di Provinsi Jawa Barat, Tahun 2018–2024

### Fitur / Kolom Dataset

| Kolom | Tipe | Keterangan |
|---|---|---|
| `Wilayah` | Kategorikal | Nama 27 Kabupaten/Kota di Jawa Barat |
| `Tahun` | Numerik | 2018 – 2024 |
| `IPM` | Numerik | Indeks Pembangunan Manusia |
| `TPT` | Numerik | Tingkat Pengangguran Terbuka (%) |
| `PDRB` | Numerik | Produk Domestik Regional Bruto |
| `RLS` | Numerik | Rata-rata Lama Sekolah (tahun) |
| `Penduduk_Miskin` | Numerik | **TARGET** — Jumlah penduduk miskin (ribuan jiwa) |

### Daftar 27 Wilayah (untuk One-Hot Encoding)

Bandung, Bandung Barat, Bekasi, Bogor, Ciamis, Cianjur, Cirebon, Garut, Indramayu, Karawang, Kuningan, Majalengka, Pangandaran, Purwakarta, Subang, Sukabumi, Sumedang, Tasikmalaya, Kota Bandung, Kota Banjar, Kota Bekasi, Kota Bogor, Kota Cimahi, Kota Cirebon, Kota Depok, Kota Sukabumi, Kota Tasikmalaya

> ⚠️ Wilayah kabupaten di dataset **TIDAK** menggunakan prefix "Kabupaten" (contoh: `Bogor`, bukan `Kabupaten Bogor`). Hanya wilayah kota yang menggunakan prefix `Kota`. Dropdown di frontend dan input JSON ke `/predict` harus menggunakan nama persis seperti di atas.

---

## 4. PIPELINE MACHINE LEARNING (SUDAH SELESAI)

### 4.1 Preprocessing
- Kolom `Wilayah` → **One-Hot Encoding** menggunakan `pd.get_dummies()` (drop_first=False)
- Variabel target `Penduduk_Miskin` → **Log Transform**: `np.log1p(y)` saat training
- Split data: **80% train / 20% test**

### 4.2 Algoritma
- **Model:** `sklearn.ensemble.RandomForestRegressor`
- **Alasan pemilihan:** Mampu menangani pola non-linear pada data ekonomi/sosial dan mengurangi risiko overfitting

### 4.3 Hyperparameter Tuning
- **Metode:** `GridSearchCV` dengan 5-fold Cross Validation
- **Parameter yang di-search:**
  - `n_estimators`
  - `max_depth`
  - `min_samples_split`
  - `max_features`

### 4.4 Prediksi & Re-transform
- Hasil prediksi model (dalam skala log) dikembalikan ke nilai asli dengan: `np.expm1(y_pred_log)`

### 4.5 Metrik Evaluasi (Hasil Terbaik)

| Metrik | Nilai |
|---|---|
| **MAE** | 29.95 |
| **RMSE** | 41.08 |
| **MAPE** | 24.65% |
| **R² Score** | 81.61% |

### 4.6 Feature Importance
Fitur yang paling berpengaruh (urutan signifikansi):
1. **RLS** (Rata-rata Lama Sekolah) — paling dominan
2. **IPM** (Indeks Pembangunan Manusia) — sangat signifikan
3. TPT, PDRB, Tahun, dan Wilayah (one-hot) mengikuti

### 4.7 Klasifikasi Output
Hasil prediksi dikategorikan ke dalam kelas kemiskinan:
- **Rendah**
- **Sedang**
- **Tinggi**

Wilayah **Kabupaten Bogor** diprediksi menempati peringkat tertinggi jumlah penduduk miskin.

---

## 5. STATUS PENGERJAAN

| Tahap | Status | Keterangan |
|---|---|---|
| EDA (Exploratory Data Analysis) | ✅ Selesai | Di dalam `apm.ipynb` |
| Pemodelan ML & Evaluasi | ✅ Selesai | R² = 81.61% |
| Simpan model ke `.pkl` | 🔜 Perlu dibuat | Gunakan `joblib` |
| Backend Flask (`app.py`) | 🔜 Perlu dibuat | Load `.pkl`, endpoint prediksi |
| Frontend HTML/CSS | 🔜 Perlu dibuat | Form input indikator makro |
| Deployment | 🔜 Opsional | Lokal (localhost) atau cloud |

---

## 6. SPESIFIKASI TEKNIS WEB APP

### 6.1 Stack

**Backend:**
- Python + Flask
- `joblib.load()` untuk load file `.pkl`
- Deployment target: fleksibel (localhost / Heroku / Railway)

**Frontend — semua via CDN, tanpa npm/install:**

| Library | Versi | Fungsi |
|---|---|---|
| **Tailwind CSS** | CDN (latest) | Base styling, layout, spacing, responsif |
| **DaisyUI** | CDN (latest) | Komponen siap pakai: card, badge, button, alert, modal |
| **Chart.js** | CDN (latest) | Visualisasi bar chart hasil prediksi per wilayah |
| **AOS.js** | CDN (latest) | Animasi scroll yang elegan |
| **Font Awesome** | CDN (latest) | Icon indikator, status kemiskinan, navigasi |

**CDN snippet untuk `<head>` di `index.html`:**
```html
<!-- Tailwind CSS + DaisyUI -->
<link href="https://cdn.jsdelivr.net/npm/daisyui@latest/dist/full.min.css" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com"></script>

<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- AOS.js -->
<link href="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.css" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js"></script>

<!-- Font Awesome -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet"/>
```

> ⚠️ AI agent WAJIB menggunakan kombinasi library di atas untuk memastikan tampilan semenarik dan seprofesional mungkin — jangan hanya pakai plain CSS.

### 6.2 Alur Prediksi di Web App
```
User input form (Wilayah, Tahun, IPM, TPT, PDRB, RLS)
    ↓
Flask menerima POST request
    ↓
Input di-encode (One-Hot untuk Wilayah, numerik untuk lainnya)
    ↓
Model .pkl memprediksi dalam skala log
    ↓
Hasil di-retransform: np.expm1(hasil_prediksi)
    ↓
Klasifikasi: Rendah / Sedang / Tinggi
    ↓
Response JSON → ditampilkan di frontend
```

### 6.3 Endpoint API
| Method | Route | Fungsi |
|---|---|---|
| `GET` | `/` | Render halaman utama (form input) |
| `POST` | `/predict` | Menerima input, return hasil prediksi (JSON) |

### 6.4 Format Input JSON (ke `/predict`)
```json
{
  "wilayah": "Bogor",
  "tahun": 2024,
  "ipm": 72.5,
  "tpt": 8.2,
  "pdrb": 150000,
  "rls": 8.5
}
```

### 6.5 Format Output JSON (dari `/predict`)
```json
{
  "wilayah": "Bogor",
  "tahun": 2024,
  "prediksi_penduduk_miskin": 412.7,
  "satuan": "ribuan jiwa",
  "klasifikasi": "Tinggi"
}
```

---

## 7. MODUL APLIKASI WEB

### Modul Wajib

| Kode | Nama Modul | Halaman/Route | Deskripsi |
|---|---|---|---|
| M1 | Beranda | `GET /` | Halaman intro, deskripsi aplikasi, navigasi ke form prediksi |
| M2 | Form Prediksi | `GET /` (bagian bawah) | Input 6 variabel: Wilayah (dropdown 27 kab/kota), Tahun, IPM, RLS, TPT, PDRB — lalu tombol "Prediksi" |
| M3 | Hasil Prediksi | `POST /predict` (response) | Menampilkan: angka prediksi (ribuan jiwa), kelas kemiskinan (Rendah/Sedang/Tinggi), dan catatan indikator dominan (RLS & IPM) |

#### Detail Input M2 — Form Prediksi
| Field | Tipe Input | Keterangan |
|---|---|---|
| Wilayah | Dropdown / `<select>` | 27 pilihan kabupaten/kota Jawa Barat |
| Tahun | Number input / slider | Rentang 2018–2024 (atau bebas untuk simulasi) |
| IPM | Number input | Indeks Pembangunan Manusia (misal: 70.5) |
| RLS | Number input | Rata-rata Lama Sekolah dalam tahun (misal: 8.5) |
| TPT | Number input | Tingkat Pengangguran Terbuka dalam % (misal: 8.2) |
| PDRB | Number input | Produk Domestik Regional Bruto (misal: 150000) |

#### Detail Output M3 — Hasil Prediksi
| Field | Keterangan |
|---|---|
| Angka prediksi | Hasil `np.expm1()` dari output model, dalam satuan ribuan jiwa |
| Kelas kemiskinan | Rendah / Sedang / Tinggi (berdasarkan threshold yang disepakati tim) |
| Indikator dominan | Catatan bahwa RLS dan IPM adalah fitur paling berpengaruh |

### Modul Opsional (Nilai Tambah)

| Kode | Nama Modul | Deskripsi |
|---|---|---|
| M4 | Visualisasi Chart | Bar chart hasil prediksi semua wilayah untuk tahun tertentu |
| M5 | Tabel Perbandingan | Ranking 27 kabupaten/kota berdasarkan prediksi penduduk miskin |
| M6 | About / Metodologi | Halaman penjelasan model, metrik evaluasi, dataset, dan profil tim |

---

## 8. DEPENDENCIES (requirements.txt)

> ⚠️ Versi `scikit-learn` WAJIB ditulis eksplisit agar model `.pkl` tidak crash saat di-load di environment berbeda (versi sklearn mempengaruhi format serialisasi model).

```
flask
numpy
pandas
scikit-learn==1.6.1
joblib
gunicorn
```

> **Cara cek versi:** Tambahkan cell berikut di `apm_training.ipynb` lalu jalankan, catat outputnya:
> ```python
> import sklearn
> print(sklearn.__version__)
> ```
> Notebook dijalankan di Google Colab — versi scikit-learn tidak tercatat di metadata. Tim **wajib** mengecek dan mengisi versi yang tepat sebelum deploy.

---

## 9. CATATAN TEKNIS WAJIB UNTUK AI AGENT

> Semua poin di bawah ini bersifat **WAJIB DIIKUTI** — menyimpang dari ketentuan ini akan menyebabkan error saat runtime.

### 9.1 Temuan Kritis dari Notebook (`apm_training.ipynb`) & Dataset

- **`drop_first=True`** — One-Hot Encoding di notebook menggunakan `pd.get_dummies(..., drop_first=True)`, bukan `drop_first=False`. AI agent WAJIB menggunakan parameter yang sama persis saat membangun input di `app.py`.
- **Wilayah yang di-drop (baseline)** — Karena `drop_first=True`, wilayah `Bandung` (urutan pertama secara alfabetis) otomatis menjadi baseline dan tidak memiliki kolom dummy tersendiri. Total kolom setelah encoding: **31 kolom**.
- **Kolom hasil One-Hot Encoding (urutan wajib dipertahankan):**
  ```
  Tahun, IPM, TPT, PDRB, RLS,
  Wilayah_Bandung Barat, Wilayah_Bekasi, Wilayah_Bogor, Wilayah_Ciamis,
  Wilayah_Cianjur, Wilayah_Cirebon, Wilayah_Garut, Wilayah_Indramayu,
  Wilayah_Karawang, Wilayah_Kota Bandung, Wilayah_Kota Banjar,
  Wilayah_Kota Bekasi, Wilayah_Kota Bogor, Wilayah_Kota Cimahi,
  Wilayah_Kota Cirebon, Wilayah_Kota Depok, Wilayah_Kota Sukabumi,
  Wilayah_Kota Tasikmalaya, Wilayah_Kuningan, Wilayah_Majalengka,
  Wilayah_Pangandaran, Wilayah_Purwakarta, Wilayah_Subang,
  Wilayah_Sukabumi, Wilayah_Sumedang, Wilayah_Tasikmalaya
  ```
- **Threshold `pd.cut(bins=3)` — nilai aktual dari dataset:**
  ```
  Rendah : ≤ 145.48 ribu jiwa
  Sedang : 145.48 – 277.47 ribu jiwa
  Tinggi : > 277.47 ribu jiwa
  ```
  Nilai bins lengkap: `[13.09, 145.48, 277.47, 409.47]`

### 9.2 Penyelarasan One-Hot Encoding (WAJIB)

Saat mengekspor model, AI agent WAJIB sekaligus mengekspor struktur kolom hasil training:

```python
import joblib
joblib.dump(best_rf, 'model_rfr.pkl')
joblib.dump(list(X.columns), 'model_columns.pkl')  # WAJIB diekspor
```

Di `app.py`, input dari user harus diproses seperti ini:

```python
model_columns = joblib.load('model_columns.pkl')

# Buat DataFrame dari input user
input_df = pd.DataFrame([data])

# One-Hot Encoding dengan drop_first=True (sama seperti training)
input_encoded = pd.get_dummies(input_df, columns=['Wilayah'], drop_first=True)

# Reindex agar kolom sama persis dengan saat training (isi 0 jika kolom tidak ada)
input_encoded = input_encoded.reindex(columns=model_columns, fill_value=0)
```

Tanpa langkah reindex ini, model akan error karena jumlah/urutan kolom tidak cocok.

### 9.3 Replikasi Threshold Klasifikasi (WAJIB)

Nilai bins sudah dikonfirmasi dari dataset aktual. Hardcode langsung di `app.py`:

```python
# Threshold klasifikasi berdasarkan pd.cut(bins=3) dari dataset aktual
BINS = [13.09, 145.48, 277.47, 409.47]

def klasifikasi(nilai):
    if nilai <= BINS[1]:
        return 'Rendah'
    elif nilai <= BINS[2]:
        return 'Sedang'
    else:
        return 'Tinggi'
```

### 9.4 Catatan Tambahan

- **Satuan target** — `Penduduk_Miskin` dalam satuan **ribuan jiwa** (bukan jiwa).
- **Model terbaik** disimpan dari `grid_search.best_estimator_` (variabel bernama `best_rf` di notebook).
- **Jangan ubah** `random_state=42` dan `test_size=0.2` jika perlu melatih ulang model.

---

*File ini dibuat sebagai referensi konteks proyek. Perbarui setiap kali ada perubahan signifikan pada pipeline atau spesifikasi teknis.*