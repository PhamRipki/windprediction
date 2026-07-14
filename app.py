import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import joblib
import os
import tempfile

# Import fungsi training dari file terpisah
from trainer import train_and_save_models

st.set_page_config(page_title="Prediksi Wind Energy", page_icon="⚡", layout="wide")

MODEL_DIR = "models"
SARIMA_PATH = os.path.join(MODEL_DIR, "sarima_model.pkl")
CONTEXT_PATH = os.path.join(MODEL_DIR, "model_context.pkl")
HISTORY_PATH = os.path.join(MODEL_DIR, "dataset_history.txt")

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
    if not (os.path.exists(SARIMA_PATH)):
        return None, None
        
    try:
        from statsmodels.tsa.statespace.sarimax import SARIMAXResultsWrapper
        sarima_fit = SARIMAXResultsWrapper.load(SARIMA_PATH)
        context = joblib.load(CONTEXT_PATH)
        return sarima_fit, context
    except Exception as e:
        st.error(f"Gagal memuat model: {e}")
        return None, None

# Muat model
sarima_fit, context = load_pretrained_models()

@st.cache_resource(show_spinner=False)
def calculate_metrics(_sarima_fit, _context):
    if _sarima_fit is None:
        return None
    try:
        ts_data = np.array(_context['last_ts_data'])
        residuals = np.array(_context['last_residuals'])
        sarima_fitted = ts_data - residuals
        
        def calc_error(true, pred):
            mae = np.mean(np.abs(true - pred))
            rmse = np.sqrt(np.mean((true - pred)**2))
            mape = np.mean(np.abs((true - pred) / np.where(true==0, 1e-10, true))) * 100
            return mae, rmse, mape

        sarima_mae, sarima_rmse, sarima_mape = calc_error(ts_data, sarima_fitted)
        
        return {
            "SARIMA": {"MAE": sarima_mae, "RMSE": sarima_rmse, "MAPE": sarima_mape}
        }
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        return None

metrics = calculate_metrics(sarima_fit, context)


st.title("⚡ Dashboard Prediksi Wind Energy (SARIMA Model)")
st.markdown("Aplikasi prediksi instan menggunakan model **SARIMA** yang sudah **ditanam**.")

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
        st.write(f"Sistem siap memprediksi **{steps_forecast} jam ke depan** menggunakan model SARIMA.")
        
        if st.button("Jalankan Prediksi!", type="primary"):
            with st.spinner("Memproses prediksi dalam hitungan detik..."):
                # Data historis terakhir untuk konteks
                ts_data = np.array(context['last_ts_data'])
                
                # Prediksi SARIMA
                sarima_forecast = sarima_fit.forecast(steps=steps_forecast)
                
                # Plot Interaktif
                fig = go.Figure()
                # Tampilkan 100 data historis terakhir
                history_window = 100
                x_hist = np.arange(-history_window, 0)
                x_fut = np.arange(0, steps_forecast)
                
                fig.add_trace(go.Scatter(x=x_hist, y=ts_data[-history_window:], mode='lines', name='Data Historis Terakhir', line=dict(color='#1f77b4')))
                fig.add_trace(go.Scatter(x=x_fut, y=sarima_forecast, mode='lines', name='Prediksi SARIMA (Masa Depan)', line=dict(color='green', dash='dot')))

                
                fig.update_layout(
                    title=f'Grafik Hasil Prediksi Energi Angin - SARIMA ({steps_forecast} Jam ke Depan)',
                    xaxis_title='Jam (0 = Sekarang)',
                    yaxis_title='Produksi (MW)',
                    hovermode='x unified',
                    template='plotly_white'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("Lihat Rincian Data Prediksi (Tabel)"):
                    df_res = pd.DataFrame({
                        "Jam Ke-": x_fut + 1,
                        "Prediksi SARIMA (MW)": sarima_forecast
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
