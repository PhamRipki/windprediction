import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import joblib
import os
import tempfile
from tensorflow.keras.models import load_model

# Import fungsi training dari file terpisah
from trainer import train_and_save_models

st.set_page_config(page_title="Prediksi Wind Energy", page_icon="⚡", layout="wide")

MODEL_DIR = "models"
SARIMA_PATH = os.path.join(MODEL_DIR, "sarima_model.pkl")
LSTM_PATH = os.path.join(MODEL_DIR, "lstm_model.keras")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
CONTEXT_PATH = os.path.join(MODEL_DIR, "model_context.pkl")
HISTORY_PATH = os.path.join(MODEL_DIR, "dataset_history.txt")

# Lags sudah dikunci (di-hardcode) sesuai perintah dosen
N_LAGS = 72

def init_history():
    os.makedirs(MODEL_DIR, exist_ok=True)
    if not os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "w") as f:
            f.write("Wind_Energy_Production_Cleaned.csv (Data Awal)\n")

init_history()

def get_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r") as f:
            return [line.strip() for line in f.readlines()]
    return []

def add_history(filename):
    with open(HISTORY_PATH, "a") as f:
        f.write(f"{filename}\n")


@st.cache_resource(show_spinner=False)
def load_pretrained_models():
    """Fungsi untuk memuat model yang ditanam dari memori lokal (Hanya dieksekusi sekali)"""
    if not (os.path.exists(SARIMA_PATH) and os.path.exists(LSTM_PATH) and os.path.exists(SCALER_PATH)):
        return None, None, None, None
        
    try:
        from statsmodels.tsa.statespace.sarimax import SARIMAXResultsWrapper
        sarima_fit = SARIMAXResultsWrapper.load(SARIMA_PATH)
        lstm_model = load_model(LSTM_PATH)
        scaler = joblib.load(SCALER_PATH)
        context = joblib.load(CONTEXT_PATH)
        return sarima_fit, lstm_model, scaler, context
    except Exception as e:
        st.error(f"Gagal memuat model: {e}")
        return None, None, None, None

# Muat model
sarima_fit, lstm_model, scaler, context = load_pretrained_models()

@st.cache_resource(show_spinner=False)
def calculate_metrics(_sarima_fit, _lstm_model, _scaler, _context):
    if _sarima_fit is None or _lstm_model is None:
        return None
    try:
        ts_data = np.array(_context['last_ts_data'])
        residuals = np.array(_context['last_residuals'])
        sarima_fitted = ts_data - residuals
        
        n_lags = N_LAGS
        scaled_res = _scaler.transform(residuals.reshape(-1, 1))
        
        X_lstm = []
        for i in range(n_lags, len(scaled_res)):
            X_lstm.append(scaled_res[i-n_lags:i, 0])
        X_lstm = np.array(X_lstm)
        X_lstm = np.reshape(X_lstm, (X_lstm.shape[0], X_lstm.shape[1], 1))
        
        lstm_pred_scaled = _lstm_model.predict(X_lstm, verbose=0)
        lstm_pred = _scaler.inverse_transform(lstm_pred_scaled).flatten()
        
        hybrid_fitted = sarima_fitted[n_lags:] + lstm_pred
        actuals = ts_data[n_lags:]
        
        def calc_error(true, pred):
            mae = np.mean(np.abs(true - pred))
            rmse = np.sqrt(np.mean((true - pred)**2))
            mape = np.mean(np.abs((true - pred) / np.where(true==0, 1e-10, true))) * 100
            return mae, rmse, mape

        sarima_mae, sarima_rmse, sarima_mape = calc_error(ts_data[n_lags:], sarima_fitted[n_lags:])
        lstm_mae, lstm_rmse, lstm_mape = calc_error(residuals[n_lags:], lstm_pred)
        hybrid_mae, hybrid_rmse, hybrid_mape = calc_error(actuals, hybrid_fitted)
        
        return {
            "SARIMA": {"MAE": sarima_mae, "RMSE": sarima_rmse, "MAPE": sarima_mape},
            "LSTM (Residual)": {"MAE": lstm_mae, "RMSE": lstm_rmse, "MAPE": lstm_mape},
            "Hybrid": {"MAE": hybrid_mae, "RMSE": hybrid_rmse, "MAPE": hybrid_mape}
        }
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        return None

metrics = calculate_metrics(sarima_fit, lstm_model, scaler, context)


st.title("⚡ Dashboard Prediksi Wind Energy (Pre-trained)")
st.markdown("Aplikasi prediksi instan menggunakan model terbaik Hybrid (SARIMA + LSTM) yang sudah **ditanam**.")

# ==========================================
# NAVIGASI TAB
# ==========================================
tab1, tab2 = st.tabs(["🚀 Prediksi Instan", "🔄 Perbarui (Regenerate) Model"])

# --- TAB 1: PREDIKSI INSTAN ---
with tab1:
    if sarima_fit is None:
        st.warning("⚠️ Model belum ditanam atau tidak ditemukan. Silakan ke tab 'Perbarui Model' untuk melakukan Inisialisasi awal.")
    else:
        st.sidebar.header("Konfigurasi Prediksi")
        steps_forecast = st.sidebar.number_input("Langkah Prediksi (Jam ke depan):", min_value=1, max_value=168, value=24)
        
        # --- HISTORI DATASET ---
        st.subheader("📚 Histori Dataset")
        history = get_history()
        for idx, item in enumerate(history):
            st.markdown(f"- {item}")
            
        # --- EVALUASI MODEL ---
        if metrics:
            st.subheader("📊 Evaluasi Model (Training Data)")
            metrics_df = pd.DataFrame(metrics).T
            st.dataframe(metrics_df.style.format("{:.4f}"))
            
        st.subheader("🔮 Lakukan Prediksi Ke Masa Depan")
        st.write(f"Sistem siap memprediksi **{steps_forecast} jam ke depan** secara langsung tanpa memuat ulang proses *training*.")
        
        if st.button("Jalankan Prediksi!", type="primary"):
            with st.spinner("Memproses prediksi dalam hitungan detik..."):
                # Data historis terakhir untuk konteks
                ts_data = np.array(context['last_ts_data'])
                residuals = np.array(context['last_residuals'])
                
                # 1. Prediksi SARIMA
                sarima_forecast = sarima_fit.forecast(steps=steps_forecast)
                
                # 2. Prediksi LSTM
                scaled_residuals = scaler.transform(residuals.reshape(-1, 1))
                lstm_input = scaled_residuals[-N_LAGS:].reshape(1, N_LAGS, 1)
                lstm_forecast_res = []
                
                for i in range(steps_forecast):
                    pred_residual = lstm_model.predict(lstm_input, verbose=0)
                    lstm_forecast_res.append(pred_residual[0, 0])
                    lstm_input = np.append(lstm_input[:, 1:, :], np.reshape(pred_residual[0, 0], (1, 1, 1)), axis=1)
                
                lstm_forecast_res = scaler.inverse_transform(np.array(lstm_forecast_res).reshape(-1, 1)).flatten()
                
                # 3. Prediksi Gabungan
                hybrid_forecast = sarima_forecast + lstm_forecast_res
                
                # Plot Interaktif
                fig = go.Figure()
                # Tampilkan 100 data historis terakhir
                history_window = 100
                x_hist = np.arange(-history_window, 0)
                x_fut = np.arange(0, steps_forecast)
                
                fig.add_trace(go.Scatter(x=x_hist, y=ts_data[-history_window:], mode='lines', name='Data Historis Terakhir', line=dict(color='#1f77b4')))
                fig.add_trace(go.Scatter(x=x_fut, y=sarima_forecast, mode='lines', name='Prediksi SARIMA', line=dict(color='green', dash='dot')))
                fig.add_trace(go.Scatter(x=x_fut, y=lstm_forecast_res, mode='lines', name='Prediksi LSTM (Residual)', line=dict(color='red', dash='dot')))
                fig.add_trace(go.Scatter(x=x_fut, y=hybrid_forecast, mode='lines', name='Prediksi HYBRID (Masa Depan)', line=dict(color='orange')))

                
                fig.update_layout(
                    title=f'Grafik Hasil Prediksi Energi Angin ({steps_forecast} Jam ke Depan)',
                    xaxis_title='Jam (0 = Sekarang)',
                    yaxis_title='Produksi (MW)',
                    hovermode='x unified',
                    template='plotly_white'
                )
                st.plotly_chart(fig, width='stretch')
                
                with st.expander("Lihat Rincian Data Prediksi (Tabel)"):
                    df_res = pd.DataFrame({
                        "Jam Ke-": x_fut + 1,
                        "Prediksi SARIMA (MW)": sarima_forecast,
                        "Prediksi LSTM (Residual)": lstm_forecast_res,
                        "Prediksi Hybrid (MW)": hybrid_forecast
                    }).set_index("Jam Ke-")
                    st.dataframe(df_res.style.format("{:.2f}"))
                
                st.success("✅ Prediksi berhasil ditampilkan secara instan!")

# --- TAB 2: REGENERATE MODEL ---
with tab2:
    st.subheader("Unggah Dataset Baru untuk Memperbarui Model")
    st.markdown("""
    Gunakan fitur ini jika ada **data periode terbaru** (dataset baru).  
    Sistem akan otomatis melatih ulang (*Retrain*) model dengan data tersebut lalu menanam (menyimpan) ulang model barunya agar sistem tetap *up-to-date*.
    """)
    
    uploaded_file = st.file_uploader("Upload File CSV Dataset Baru:", type=['csv'])
    
    if uploaded_file is not None:
        if st.button("Mulai Regenerasi Model", type="primary"):
            st.info("Mohon tunggu, proses regenerasi (pelatihan ulang SARIMA & LSTM) membutuhkan waktu beberapa menit...")
            
            # Simpan file upload ke temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
                
            try:
                # Panggil fungsi training dari file eksternal (yang menyembunyikan logika epoch/lag)
                train_and_save_models(tmp_path, MODEL_DIR)
                
                # Tambahkan ke history
                add_history(uploaded_file.name)
                
                st.success("🎉 Regenerasi berhasil! Model terbaru telah ditanam. Anda perlu membersihkan (clear cache) atau muat ulang aplikasi untuk menggunakan model terbaru ini.")
                # Clear cache Streamlit
                st.cache_resource.clear()
            except Exception as e:
                st.error(f"Terjadi kesalahan saat melatih model: {e}")
            finally:
                os.remove(tmp_path)
