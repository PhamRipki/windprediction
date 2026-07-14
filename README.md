# ⚡ Wind Energy Prediction Dashboard

Aplikasi prediksi produksi energi angin menggunakan Hybrid Model (SARIMA + LSTM).

## Features
- 🚀 Prediksi instan menggunakan pre-trained models
- 📊 Evaluasi model dengan MAE, RMSE, dan MAPE
- 🔄 Kemampuan retrain model dengan dataset baru
- 📈 Visualisasi interaktif dengan Plotly

## Tech Stack
- Streamlit
- TensorFlow/Keras (LSTM)
- Statsmodels (SARIMA)
- Plotly (Visualisasi)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Model Architecture
- **SARIMA**: ARIMA(0,1,2)(1,0,1)[24]
- **LSTM**: 2 layers dengan Dropout
- **Hybrid**: Kombinasi SARIMA + LSTM untuk residual correction
