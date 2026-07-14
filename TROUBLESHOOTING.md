# 🔧 Troubleshooting Guide - Streamlit Cloud Deployment

## ✅ Perbaikan yang Sudah Dilakukan

### Problem: Python 3.14 tidak kompatibel dengan TensorFlow
**Error Log:**
```
ERROR: Could not find a version that satisfies the requirement tensorflow>=2.13.0
```

**Solusi yang Diterapkan:**
1. ✅ Membuat file `.python-version` untuk memaksa Python 3.11.11
2. ✅ Pin versi TensorFlow ke 2.15.0 (stabil dan kompatibel)
3. ✅ Pin versi dependencies lainnya untuk menghindari konflik
4. ✅ Menambahkan `packages.txt` untuk system dependencies

### Files yang Ditambahkan/Diupdate:

#### 1. `.python-version`
```
3.11.11
```
File ini memaksa Streamlit Cloud menggunakan Python 3.11 alih-alih 3.14.

#### 2. `requirements.txt` (Updated)
```
streamlit>=1.28.0
numpy>=1.24.0,<2.0.0
pandas>=2.0.0,<2.1.0
plotly>=5.17.0
scikit-learn>=1.3.0,<1.4.0
tensorflow==2.15.0
statsmodels>=0.14.0,<0.15.0
joblib>=1.3.0
protobuf>=3.20.0,<4.24.0
h5py>=3.10.0
keras>=2.15.0,<3.0.0
```

#### 3. `packages.txt` (System Dependencies)
```
libgomp1
```

#### 4. `.streamlit/config.toml`
```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

---

## 🚀 Langkah Selanjutnya

### Streamlit Cloud akan otomatis re-deploy setelah push ini!

1. **Buka Dashboard Streamlit Cloud**: https://share.streamlit.io
2. **Lihat App Anda**: `windprediction-dpv4uttlhgel3n3433fwho`
3. **Monitor Logs** untuk memastikan tidak ada error lagi
4. **Tunggu 5-10 menit** untuk deployment selesai

---

## 📊 Expected Deployment Log (Success)

Setelah fix ini, log deployment seharusnya seperti ini:

```
🚀 Starting up repository: 'windprediction', branch: 'main', main module: 'app.py'
🐙 Cloning repository...
🐙 Cloned repository!
📦 Processing dependencies...
──── Using Python 3.11.11 ────
✅ Successfully installed streamlit
✅ Successfully installed numpy
✅ Successfully installed pandas
✅ Successfully installed plotly
✅ Successfully installed scikit-learn
✅ Successfully installed tensorflow==2.15.0
✅ Successfully installed statsmodels
✅ Successfully installed joblib
🎉 App is running!
```

---

## ⚠️ Jika Masih Ada Error Setelah Fix Ini

### Error 1: Out of Memory (OOM)
**Gejala:**
```
MemoryError: Unable to allocate array
```

**Solusi:**
Edit `app.py`, kurangi penggunaan memori:

```python
# Line 129, kurangi history_window
history_window = 50  # dari 100

# Line 1000 di trainer.py, kurangi dataset
ts_data = df['Production'].tail(500).replace(0, np.nan).interpolate(method='linear').bfill().values
# dari tail(1000) menjadi tail(500)
```

### Error 2: TensorFlow Tidak Bisa Load Model
**Gejala:**
```
ValueError: No model config found
```

**Solusi:**
Pastikan semua file di folder `models/` ter-upload dengan Git LFS:

```cmd
git lfs ls-files
```

Harus menampilkan:
```
4ee819842d * models/lstm_model.keras
b9b379ae20 * models/model_context.pkl
1fd8281991 * models/sarima_model.pkl
36b45d5eb2 * models/scaler.pkl
```

### Error 3: statsmodels SARIMAXResultsWrapper Error
**Gejala:**
```
AttributeError: 'SARIMAXResultsWrapper' object has no attribute 'forecast'
```

**Solusi:**
Ini karena perbedaan versi statsmodels. Update `app.py`:

```python
# Ganti line forecast
# Dari:
sarima_forecast = sarima_fit.forecast(steps=steps_forecast)

# Menjadi:
sarima_forecast = sarima_fit.get_forecast(steps=steps_forecast).predicted_mean
```

---

## 🔄 Cara Re-deploy Manual (Jika Perlu)

Jika aplikasi tidak otomatis update:

1. Buka **Streamlit Cloud Dashboard**
2. Klik aplikasi `windprediction`
3. Klik tombol **"Reboot app"** atau **"⋮" → "Reboot"**
4. Tunggu beberapa menit

---

## 📝 Alternatif: Gunakan TensorFlow CPU (Lebih Ringan)

Jika masih ada masalah dengan resource, coba gunakan TensorFlow CPU:

**Update `requirements.txt`:**
```
tensorflow-cpu==2.15.0
```

TensorFlow CPU lebih kecil (~100MB vs ~500MB) dan cocok untuk inference-only.

**Push update:**
```cmd
git add requirements.txt
git commit -m "Switch to tensorflow-cpu for lighter footprint"
git push origin main
```

---

## 🎯 Verifikasi Deployment Berhasil

Setelah deployment selesai, cek ini:

### 1. Homepage Loading
- ✅ Halaman utama muncul tanpa error
- ✅ Tab "Prediksi Instan" dan "Perbarui Model" ada

### 2. Pre-trained Model Loading
- ✅ Tidak ada warning "Model belum ditanam"
- ✅ Histori dataset muncul
- ✅ Evaluasi model muncul (MAE, RMSE, MAPE)

### 3. Prediksi Berfungsi
- ✅ Klik "Jalankan Prediksi!" tidak error
- ✅ Grafik Plotly muncul
- ✅ Tabel prediksi muncul di expander

### 4. Performance Check
- ⏱️ Prediksi selesai dalam < 10 detik
- 📊 Grafik interaktif smooth
- 💾 Memory usage < 1GB

---

## 📞 Jika Semua Gagal

### Opsi 1: Deploy Lokal Dulu untuk Testing
```cmd
cd c:\Users\x\Downloads\Streamlit_App
streamlit run app.py
```

Jika lokal berfungsi tapi cloud tidak, masalahnya di environment Streamlit Cloud.

### Opsi 2: Simplify Model
Hapus LSTM, pakai hanya SARIMA untuk mengurangi dependency TensorFlow:
- Lebih ringan
- Lebih cepat
- Lebih stable di cloud

### Opsi 3: Upgrade Streamlit Cloud Plan
- **Free Tier**: 1GB RAM, 1 CPU shared
- **Starter Plan** ($20/month): 2GB RAM, 2 apps
- Link: https://streamlit.io/cloud/pricing

---

## ✅ Checklist Deployment

- [x] Repository pushed ke GitHub
- [x] Git LFS configured untuk file besar
- [x] `.python-version` file created (Python 3.11)
- [x] `requirements.txt` updated dengan versi compatible
- [x] `packages.txt` added untuk system dependencies
- [x] `.streamlit/config.toml` configured
- [ ] **Tunggu auto re-deploy dari Streamlit Cloud**
- [ ] Monitor logs untuk memastikan no error
- [ ] Test aplikasi setelah deployment selesai

---

## 🎉 Setelah Berhasil

URL Aplikasi Anda:
```
https://windprediction-dpv4uttlhgel3n3433fwho.streamlit.app
```

Share link ini untuk akses aplikasi dari mana saja!

---

**Last Updated**: 2026-07-14
**Status**: ✅ Fixes pushed, waiting for auto re-deploy
