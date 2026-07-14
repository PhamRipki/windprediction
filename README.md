# ⚡ Wind Energy Prediction Dashboard

Aplikasi prediksi produksi energi angin menggunakan SARIMA Model.

## 🚀 Quick Start

### Cara Menggunakan Aplikasi (Deployed di Streamlit Cloud):

1. **Buka aplikasi** di browser
2. **Pergi ke tab "Perbarui (Regenerate) Model"**
3. **Upload file CSV** dengan format:
   ```csv
   Date,Start_Hour,Production
   2024-01-01,0,145.5
   2024-01-01,1,142.3
   ```
4. **Klik "Mulai Training Model"**
5. **Tunggu 2-3 menit** untuk training selesai
6. **Refresh aplikasi** (tekan C di keyboard)
7. **Pergi ke tab "Prediksi Instan"** 
8. **Klik "Jalankan Prediksi!"** untuk prediksi 24 jam ke depan

## 📊 Features

- ✅ **SARIMA Time Series Forecasting** - Proven algorithm
- ✅ **Grafik Interaktif** - Plotly visualization
- ✅ **Upload Dataset** - Train dengan data Anda sendiri
- ✅ **Model Evaluation** - MAE, RMSE, MAPE metrics
- ✅ **24-Hour Seasonality** - Capture daily patterns

## 🛠️ Tech Stack

- **Streamlit** - Web framework
- **Statsmodels** - SARIMA implementation
- **Plotly** - Interactive charts
- **Pandas & NumPy** - Data processing

## 📦 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
```

## 🌐 Deployment

Aplikasi ini di-deploy di Streamlit Cloud dengan Python 3.14.

### Requirements:
- Python 3.14 compatible
- No TensorFlow (untuk compatibility)
- Lightweight dependencies only

## 📝 Model Architecture

**SARIMA: Seasonal AutoRegressive Integrated Moving Average**
- Order: ARIMA(0,1,2)
- Seasonal Order: (1,0,1)[24]
- Optimized for hourly wind energy data
- Captures daily seasonality (24-hour cycle)

## ⚠️ Important Notes

1. **First Time Use**: Anda HARUS upload dataset dan training model dulu sebelum bisa prediksi
2. **Model Persistence**: Model tersimpan di folder `models/` dan akan bertahan antar session
3. **Re-training**: Bisa upload dataset baru kapan saja untuk update model

## 🎯 URL

Production: `https://windprediction-dpv4uttlhgel3n3433fwho.streamlit.app`

## 📄 License

MIT License

## 👨‍💻 Author

Wind Energy Prediction Team
