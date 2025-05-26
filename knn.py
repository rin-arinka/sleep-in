import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from models import DataTraining

MODEL = None
MODEL_PATH = "model_knn.pkl"
ENCODER_PATH = "model/label_encoder.joblib"

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    print("⚠️ Model belum dilatih. Fungsi prediksi tidak bisa digunakan sampai pelatihan selesai.")

def preprocess_data_training():
    # Ambil semua data dari tabel DataTraining
    data = DataTraining.query.all()

    # Konversi ke list of dict
    data_list = [{
        'jenis_kelamin': d.jenis_kelamin,
        'usia': d.usia,
        'durasi_tidur': d.durasi_tidur,
        'kualitas_tidur': d.kualitas_tidur,
        'tingkat_stres': d.tingkat_stres,
        'kategori_bmi' : d.kategori_bmi,
        'denyut_jantung': d.denyut_jantung,
        'langkah_harian': d.langkah_harian,
        'sistolik': d.sistolik,
        'diastolik': d.diastolik,
        'gangguan_tidur': d.gangguan_tidur
    } for d in data]

    # Buat dataframe
    df = pd.DataFrame(data_list)

    # Label Encoding untuk jenis_kelamin, kategori_bmi dan gangguan_tidur
    label_encoder_gender = LabelEncoder()
    label_encoder_bmi = LabelEncoder()
    label_encoder_label = LabelEncoder()

    df['jenis_kelamin'] = label_encoder_gender.fit_transform(df['jenis_kelamin'])
    df['kategori_bmi'] = label_encoder_bmi.fit_transform(df['kategori_bmi'])
    df['gangguan_tidur'] = label_encoder_label.fit_transform(df['gangguan_tidur'])

    # Pisahkan fitur dan label
    X = df.drop(columns=['gangguan_tidur'])  # fitur
    y = df['gangguan_tidur']  # label

    return X, y, label_encoder_label  # kembalikan encoder label kalau nanti ingin decode prediksi

# Fungsi prediksi
def predict_sleep_disorder(input_data: dict):
    # Load model dan encoder
    knn = joblib.load(MODEL_PATH)
    label_encoder = joblib.load(ENCODER_PATH)

    # Konversi jenis_kelamin ke numerik seperti di preprocessing
    gender_map = {'Laki-laki': 1, 'Perempuan': 0}  # pastikan sesuai hasil LabelEncoder

    # Konversi kategori_BMI ke numerik
    bmi_map = {
        'Underweight': 0,
        'Normal': 1,
        'Overweight': 2,
        'Obesitas': 3
    }

    input_vector = np.array([[
        gender_map.get(input_data['jenis_kelamin'], 0),
        input_data['usia'],
        input_data['durasi_tidur'],
        input_data['kualitas_tidur'],
        input_data['tingkat_stres'],
        bmi_map.get(input_data['kategori_bmi'], 1),  # Default ke 'Normal'
        input_data['detak_jantung'],
        input_data['langkah_kaki'],
        input_data['sistolik'],
        input_data['diastolik']
    ]])

    # Prediksi
    prediction_encoded = knn.predict(input_vector)[0]
    prediction_label = label_encoder.inverse_transform([prediction_encoded])[0]

    return prediction_label

def train_and_save_knn_model():
    # Preprocessing
    X, y, label_encoder = preprocess_data_training()

    # Melatih model KNN
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X, y)

    # Buat folder model kalau belum ada
    os.makedirs("model", exist_ok=True)

    # Simpan model dan label encoder
    joblib.dump(knn, MODEL_PATH)
    joblib.dump(label_encoder, ENCODER_PATH)

    return f"Model dan encoder disimpan ke {MODEL_PATH} & {ENCODER_PATH}"