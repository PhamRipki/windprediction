import os
import numpy as np
import pandas as pd
import joblib
from statsmodels.tsa.statespace.sarimax import SARIMAX

def train_and_save_models(csv_path, output_dir="models"):
    """
    Melatih model SARIMA dari file CSV lalu menyimpan modelnya 
    ke dalam direktori output_dir agar bisa 'ditanam' di Streamlit.
    """
    print(f"Membaca dataset dari {csv_path}...")
    
    # 1. Baca Data
    df = pd.read_csv(csv_path)
    
    # Jika masih ada kolom Start_Hour, gabungkan. Jika sudah menjadi index, lewati.
    if 'Start_Hour' in df.columns and 'Date' in df.columns:
        df['DateTime'] = pd.to_datetime(df['Date']) + pd.to_timedelta(df['Start_Hour'], unit='h')
        df.set_index('DateTime', inplace=True)
    elif 'DateTime' in df.columns:
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        df.set_index('DateTime', inplace=True)
        
    df = df.sort_index()
    
    # Ambil nilai Production
    # Jika dataset sangat besar, ambil 1000 atau jumlah wajar agar pelatihan cepat
    # Sesuai preferensi, kita ambil 1000 data terakhir agar model update dengan tren terbaru
    ts_data = df['Production'].tail(1000).replace(0, np.nan).interpolate(method='linear').bfill().values
    
    os.makedirs(output_dir, exist_ok=True)
    
    # ==========================
    # 2. Latih Model SARIMA
    # ==========================
    print("Melatih Model SARIMA: ARIMA(0,1,2)(1,0,1)[24]...")
    sarima_order = (0, 1, 2)
    sarima_seasonal_order = (1, 0, 1, 24)
    sarima_model = SARIMAX(ts_data, order=sarima_order, seasonal_order=sarima_seasonal_order)
    sarima_fit = sarima_model.fit(disp=False)
    
    # Simpan model SARIMA
    sarima_path = os.path.join(output_dir, "sarima_model.pkl")
    sarima_fit.save(sarima_path)
    print(f"Model SARIMA berhasil disimpan di {sarima_path}")
    
    # Ekstraksi Residual untuk context
    residuals = sarima_fit.resid
    
    # Simpan data terakhir (dibutuhkan sebagai context untuk prediksi selanjutnya)
    context = {
        'last_ts_data': ts_data.tolist(),
        'last_residuals': residuals.tolist()
    }
    context_path = os.path.join(output_dir, "model_context.pkl")
    joblib.dump(context, context_path)
    print("Proses Penanaman (Training & Saving) Selesai!")

if __name__ == "__main__":
    # Menjalankan script ini untuk pertama kali dengan data bersih yang sudah ada
    # Path disesuaikan dengan posisi dataset yang dilaporkan user
    default_csv = r"C:\Users\Gopal\Desktop\PJBL\dataset\Wind_Energy_Production_Cleaned.csv"
    train_and_save_models(default_csv)
