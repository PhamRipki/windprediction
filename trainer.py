import os
import numpy as np
import pandas as pd
import joblib
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

def train_and_save_models(csv_path, output_dir="models"):
    """
    Melatih model SARIMA dan LSTM dari file CSV lalu menyimpan modelnya 
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
    # statsmodels punya method save, atau pakai joblib
    sarima_fit.save(sarima_path)
    print(f"Model SARIMA berhasil disimpan di {sarima_path}")
    
    # Ekstraksi Residual untuk LSTM
    residuals = sarima_fit.resid
    
    # ==========================
    # 3. Persiapan Data LSTM
    # ==========================
    print("Mempersiapkan data residual untuk LSTM...")
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(residuals.reshape(-1, 1))
    
    # Simpan Scaler (agar bisa dipakai untuk inverse_transform nanti)
    scaler_path = os.path.join(output_dir, "scaler.pkl")
    joblib.dump(scaler, scaler_path)
    
    # Parameter fix (di-hardcode sesuai instruksi dosen)
    n_lags = 72
    epochs = 50
    
    X, y = [], []
    for i in range(n_lags, len(scaled_data)):
        X.append(scaled_data[i-n_lags:i, 0])
        y.append(scaled_data[i, 0])
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    
    # ==========================
    # 4. Latih Model LSTM
    # ==========================
    print(f"Melatih Model LSTM (Lags={n_lags}, Epochs={epochs})...")
    lstm_model = Sequential()
    lstm_model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)))
    lstm_model.add(Dropout(0.2))
    lstm_model.add(LSTM(units=50))
    lstm_model.add(Dropout(0.2))
    lstm_model.add(Dense(1))
    lstm_model.compile(optimizer='adam', loss='mean_squared_error')
    
    lstm_model.fit(X, y, epochs=epochs, batch_size=32, verbose=1)
    
    # Simpan model LSTM
    lstm_path = os.path.join(output_dir, "lstm_model.keras")
    lstm_model.save(lstm_path)
    print(f"Model LSTM berhasil disimpan di {lstm_path}")
    
    # Simpan data terakhir (dibutuhkan sebagai context sliding window untuk prediksi selanjutnya)
    # Kita butuh residual lag terakhir dan ts_data asli
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
