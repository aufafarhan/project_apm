from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import joblib
import os

app = Flask(__name__)

# Load model dan kolom training
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR = os.path.join(BASE_DIR, '..', 'ml')

model = joblib.load(os.path.join(ML_DIR, 'model_rfr.pkl'))
model_columns = joblib.load(os.path.join(ML_DIR, 'model_columns.pkl'))

BINS = [13.09, 145.48, 277.47, 409.47]  # Dari pd.cut(bins=3) dataset aktual

# Load dataset untuk rata-rata regional
dataset_path = os.path.join(ML_DIR, 'data', 'dataset.csv')
if os.path.exists(dataset_path):
    try:
        df_dataset = pd.read_csv(dataset_path)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        df_dataset = None
else:
    df_dataset = None

# Hitung rata-rata dan standar deviasi dataset untuk penjelasan kontribusi fitur
if df_dataset is not None:
    STATS = {
        'ipm_mean': float(df_dataset['IPM'].mean()),
        'ipm_std': float(df_dataset['IPM'].std()) or 1.0,
        'rls_mean': float(df_dataset['RLS'].mean()),
        'rls_std': float(df_dataset['RLS'].std()) or 1.0,
        'tpt_mean': float(df_dataset['TPT'].mean()),
        'tpt_std': float(df_dataset['TPT'].std()) or 1.0,
        'pdrb_mean': float(df_dataset['PDRB'].mean()),
        'pdrb_std': float(df_dataset['PDRB'].std()) or 1.0
    }
else:
    STATS = {
        'ipm_mean': 71.3, 'ipm_std': 4.8,
        'rls_mean': 8.3, 'rls_std': 1.3,
        'tpt_mean': 7.5, 'tpt_std': 2.5,
        'pdrb_mean': 4.5, 'pdrb_std': 2.2
    }

# Ekstrak feature importances dari model RFR
FEATURE_IMPORTANCES = {}
try:
    if hasattr(model, 'feature_importances_'):
        for col, imp in zip(model_columns, model.feature_importances_):
            if col in ['IPM', 'RLS', 'TPT', 'PDRB']:
                FEATURE_IMPORTANCES[col.lower()] = float(imp)
except Exception as e:
    print(f"Error extracting feature importances: {e}")

# Fallback ke nilai inspected jika gagal
if 'ipm' not in FEATURE_IMPORTANCES:
    FEATURE_IMPORTANCES['ipm'] = 0.1746
if 'rls' not in FEATURE_IMPORTANCES:
    FEATURE_IMPORTANCES['rls'] = 0.1993
if 'tpt' not in FEATURE_IMPORTANCES:
    FEATURE_IMPORTANCES['tpt'] = 0.0848
if 'pdrb' not in FEATURE_IMPORTANCES:
    FEATURE_IMPORTANCES['pdrb'] = 0.0557

VALID_WILAYAH = {
    "Bandung", "Bandung Barat", "Bekasi", "Bogor", "Ciamis", "Cianjur", 
    "Cirebon", "Garut", "Indramayu", "Karawang", "Kota Bandung", "Kota Banjar", 
    "Kota Bekasi", "Kota Bogor", "Kota Cimahi", "Kota Cirebon", "Kota Depok", 
    "Kota Sukabumi", "Kota Tasikmalaya", "Kuningan", "Majalengka", "Pangandaran", 
    "Purwakarta", "Subang", "Sukabumi", "Sumedang", "Tasikmalaya"
}




def klasifikasi(nilai):
    """Klasifikasi jumlah penduduk miskin ke Rendah / Sedang / Tinggi."""
    if nilai <= BINS[1]:
        return 'Rendah'
    elif nilai <= BINS[2]:
        return 'Sedang'
    else:
        return 'Tinggi'


# Routes
@app.route('/')
def index():
    """Render halaman utama dengan form prediksi."""
    return render_template('index.html')


def format_list_id(items):
    """Format list of items into Indonesian grammatically correct list."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} serta {items[1]}"
    return ", ".join(items[:-1]) + f", dan {items[-1]}"


@app.route('/predict', methods=['POST'])
def predict():
    """Menerima input dari form, memprediksi jumlah penduduk miskin."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Data JSON tidak ditemukan atau kosong.'}), 400

        # Validasi field yang diperlukan
        required_fields = ['wilayah', 'tahun', 'ipm', 'tpt', 'pdrb', 'rls']
        for field in required_fields:
            if data.get(field) is None or str(data.get(field)).strip() == '':
                return jsonify({'error': f'Field {field} tidak boleh kosong.'}), 400

        # Ambil input dan pastikan tipe data valid
        wilayah = data.get('wilayah')
        
        try:
            tahun = int(data.get('tahun'))
        except (ValueError, TypeError):
            return jsonify({'error': 'Tahun harus berupa angka bulat (integer).'}), 400

        try:
            ipm = float(data.get('ipm'))
            tpt = float(data.get('tpt'))
            pdrb = float(data.get('pdrb'))
            rls = float(data.get('rls'))
        except (ValueError, TypeError):
            return jsonify({'error': 'IPM, TPT, PDRB, dan RLS harus berupa angka desimal/numerik.'}), 400

        # Validasi batas logis
        if wilayah not in VALID_WILAYAH:
            return jsonify({'error': f'Wilayah "{wilayah}" tidak valid.'}), 400

        if not (2018 <= tahun <= 2035):
            return jsonify({'error': 'Tahun prediksi harus berada di antara tahun 2018 dan 2035.'}), 400

        if not (0.0 <= ipm <= 100.0):
            return jsonify({'error': 'Nilai IPM harus berada di antara 0 dan 100.'}), 400

        if not (0.0 <= rls <= 30.0):
            return jsonify({'error': 'Nilai Rata-rata Lama Sekolah (RLS) harus berada di antara 0 dan 30 tahun.'}), 400

        if not (0.0 <= tpt <= 100.0):
            return jsonify({'error': 'Nilai Tingkat Pengangguran Terbuka (TPT) harus berada di antara 0% dan 100%.'}), 400

        if not (-100.0 <= pdrb <= 100.0):
            return jsonify({'error': 'Nilai Laju Pertumbuhan Ekonomi PDRB harus berada di antara -100% dan 100%.'}), 400

        # Buat DataFrame dari input
        input_df = pd.DataFrame([{
            'Wilayah': wilayah,
            'Tahun': tahun,
            'IPM': ipm,
            'TPT': tpt,
            'PDRB': pdrb,
            'RLS': rls
        }])

        # One-Hot Encoding (drop_first=True — WAJIB sama seperti training)
        input_encoded = pd.get_dummies(input_df, columns=['Wilayah'], drop_first=True)

        # Reindex agar kolom sama persis dengan saat training
        input_encoded = input_encoded.reindex(columns=model_columns, fill_value=0)

        # Prediksi (hasil dalam skala log)
        pred_log = model.predict(input_encoded)

        # Re-transform ke nilai asli
        pred_asli = np.expm1(pred_log)[0]

        # Klasifikasi
        kelas = klasifikasi(pred_asli)

        # Hitung rata-rata regional
        avg_ipm, avg_tpt, avg_pdrb, avg_rls = 0.0, 0.0, 0.0, 0.0
        if df_dataset is not None:
            # Ambil data untuk tahun yang sama jika ada, jika tidak, ambil rata-rata keseluruhan
            df_year = df_dataset[df_dataset['Tahun'] == tahun]
            if not df_year.empty:
                avg_ipm = float(df_year['IPM'].mean())
                avg_tpt = float(df_year['TPT'].mean())
                avg_pdrb = float(df_year['PDRB'].mean())
                avg_rls = float(df_year['RLS'].mean())
            else:
                avg_ipm = float(df_dataset['IPM'].mean())
                avg_tpt = float(df_dataset['TPT'].mean())
                avg_pdrb = float(df_dataset['PDRB'].mean())
                avg_rls = float(df_dataset['RLS'].mean())
        else:
            # Fallback mock data jika file tidak ditemukan
            avg_ipm, avg_tpt, avg_pdrb, avg_rls = 71.3, 7.5, 4.5, 8.3

        # Hitung kontribusi lokal tiap fitur utama
        std_ipm = STATS['ipm_std']
        std_rls = STATS['rls_std']
        std_tpt = STATS['tpt_std']
        std_pdrb = STATS['pdrb_std']

        # Normalisasi selisih input dengan rata-rata regional
        z_ipm = (ipm - avg_ipm) / std_ipm
        z_rls = (rls - avg_rls) / std_rls
        z_tpt = (tpt - avg_tpt) / std_tpt
        z_pdrb = (pdrb - avg_pdrb) / std_pdrb

        effects = {
            'ipm': {
                'name': 'Indeks Pembangunan Manusia (IPM)',
                'effect': z_ipm * FEATURE_IMPORTANCES['ipm'],
                'input': ipm,
                'avg': avg_ipm,
                'unit': ''
            },
            'rls': {
                'name': 'Rata-rata Lama Sekolah (RLS)',
                'effect': z_rls * FEATURE_IMPORTANCES['rls'],
                'input': rls,
                'avg': avg_rls,
                'unit': ' tahun'
            },
            'tpt': {
                'name': 'Tingkat Pengangguran Terbuka (TPT)',
                'effect': -z_tpt * FEATURE_IMPORTANCES['tpt'],
                'input': tpt,
                'avg': avg_tpt,
                'unit': '%'
            },
            'pdrb': {
                'name': 'Pertumbuhan Ekonomi (PDRB)',
                'effect': z_pdrb * FEATURE_IMPORTANCES['pdrb'],
                'input': pdrb,
                'avg': avg_pdrb,
                'unit': '%'
            }
        }

        # Kualitatif deskripsi pemetaan untuk teks penjelasan
        descriptions = {
            'ipm': {
                'positive': "tingkat Indeks Pembangunan Manusia (IPM) yang memuaskan",
                'negative': "tingkat Indeks Pembangunan Manusia (IPM) yang masih di bawah rata-rata regional"
            },
            'rls': {
                'positive': "Rata-rata Lama Sekolah (RLS) yang memadai",
                'negative': "Rata-rata Lama Sekolah (RLS) yang tergolong rendah"
            },
            'tpt': {
                'positive': "Tingkat Pengangguran Terbuka (TPT) yang rendah dan terkendali",
                'negative': "Tingkat Pengangguran Terbuka (TPT) yang tinggi"
            },
            'pdrb': {
                'positive': "Laju Pertumbuhan Ekonomi (PDRB) yang tumbuh positif",
                'negative': "Laju Pertumbuhan Ekonomi (PDRB) yang lambat"
            }
        }

        reducing_factors = []
        increasing_factors = []

        # Urutkan berdasarkan pengaruh absolut terbesar agar narasi lebih fokus pada faktor utama
        sorted_keys = sorted(effects, key=lambda k: abs(effects[k]['effect']), reverse=True)

        for key in sorted_keys:
            val = effects[key]
            # Deviasi diabaikan jika sangat dekat dengan rata-rata (z-score absolut < 0.15)
            if abs(val['effect']) < 0.005:
                continue

            is_pos = val['effect'] >= 0
            desc = descriptions[key]['positive'] if is_pos else descriptions[key]['negative']
            val_str = f"{val['input']:.2f}{val['unit']}"
            desc_formatted = f"{desc} ({val_str})"

            if is_pos:
                reducing_factors.append(desc_formatted)
            else:
                increasing_factors.append(desc_formatted)

        p_reducing = format_list_id(reducing_factors)
        p_increasing = format_list_id(increasing_factors)

        # Sintesis narasi penjelasan model
        if reducing_factors and increasing_factors:
            if kelas == 'Rendah':
                penjelasan_model = (
                    f"Prediksi tingkat kemiskinan di {wilayah} pada tahun {tahun} diklasifikasikan sebagai **Rendah**. "
                    f"Kondisi ini didominasi oleh faktor pendukung berupa {p_reducing}. "
                    f"Kinerja positif dari indikator tersebut berhasil meredam potensi peningkatan kemiskinan yang dipicu oleh {p_increasing}."
                )
            elif kelas == 'Sedang':
                penjelasan_model = (
                    f"Prediksi tingkat kemiskinan di {wilayah} pada tahun {tahun} berada pada tingkat **Sedang**. "
                    f"Meskipun terdapat dampak positif dari {p_reducing}, "
                    f"efek tersebut dinetralkan oleh tekanan dari {p_increasing}, sehingga menghasilkan kondisi keseimbangan di tingkat Sedang."
                )
            else:  # Tinggi
                penjelasan_model = (
                    f"Prediksi tingkat kemiskinan di {wilayah} pada tahun {tahun} masuk dalam kategori **Tinggi**. "
                    f"Meskipun terdapat kontribusi positif dari {p_reducing}, "
                    f"hambatan dari {p_increasing} mendominasi kondisi sosial-ekonomi daerah ini dan mendorong angka kemiskinan ke tingkat yang tinggi."
                )
        elif reducing_factors:
            penjelasan_model = (
                f"Prediksi tingkat kemiskinan di {wilayah} pada tahun {tahun} berhasil ditekan hingga kategori **Rendah**. "
                f"Hal ini didukung penuh oleh keunggulan di beberapa indikator utama, yaitu {p_reducing}, "
                f"tanpa adanya hambatan indikator sosial-ekonomi yang berarti."
            )
        elif increasing_factors:
            prediksi_tingkat = "Tinggi" if kelas == "Tinggi" else ("Sedang" if kelas == "Sedang" else "Rendah")
            penjelasan_model = (
                f"Prediksi tingkat kemiskinan di {wilayah} pada tahun {tahun} tergolong **{prediksi_tingkat}**. "
                f"Kondisi ini disebabkan oleh akumulasi tantangan dari beberapa indikator utama, yaitu {p_increasing}, "
                f"yang secara signifikan memperlemah ketahanan sosial-ekonomi wilayah tersebut."
            )
        else:
            prediksi_tingkat = "Tinggi" if kelas == "Tinggi" else ("Sedang" if kelas == "Sedang" else "Rendah")
            penjelasan_model = (
                f"Prediksi tingkat kemiskinan di {wilayah} pada tahun {tahun} diklasifikasikan sebagai **{prediksi_tingkat}**. "
                f"Kondisi sosial-ekonomi secara umum berjalan stabil mendekati rata-rata provinsi Jawa Barat."
            )

        return jsonify({
            'wilayah': wilayah,
            'tahun': tahun,
            'prediksi_penduduk_miskin': round(float(pred_asli), 2),
            'satuan': 'ribuan jiwa',
            'klasifikasi': kelas,
            'input_data': {
                'ipm': ipm,
                'tpt': tpt,
                'pdrb': pdrb,
                'rls': rls
            },
            'regional_average': {
                'ipm': round(avg_ipm, 2),
                'tpt': round(avg_tpt, 2),
                'pdrb': round(avg_pdrb, 2),
                'rls': round(avg_rls, 2)
            },
            'penjelasan_model': penjelasan_model
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)
