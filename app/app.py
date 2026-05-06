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


@app.route('/predict', methods=['POST'])
def predict():
    """Menerima input dari form, memprediksi jumlah penduduk miskin."""
    try:
        data = request.get_json()

        # Ambil input dari JSON
        wilayah = data.get('wilayah')
        tahun = int(data.get('tahun'))
        ipm = float(data.get('ipm'))
        tpt = float(data.get('tpt'))
        pdrb = float(data.get('pdrb'))
        rls = float(data.get('rls'))

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

        return jsonify({
            'wilayah': wilayah,
            'tahun': tahun,
            'prediksi_penduduk_miskin': round(float(pred_asli), 2),
            'satuan': 'ribuan jiwa',
            'klasifikasi': kelas
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)
