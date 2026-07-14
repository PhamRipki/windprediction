# 🚀 Panduan Deploy ke Streamlit Cloud

## Status Repository
✅ **Repository GitHub**: https://github.com/PhamRipki/windprediction.git
✅ **Branch**: main
✅ **Git LFS**: Aktif untuk file model besar
✅ **File Requirements**: Sudah tersedia

---

## Langkah Deploy ke Streamlit Cloud

### 1. Akses Streamlit Cloud
Buka browser dan kunjungi: **https://share.streamlit.io**

### 2. Login dengan GitHub
- Klik tombol **"Sign in"**
- Pilih **"Continue with GitHub"**
- Authorize Streamlit Cloud untuk mengakses repository GitHub Anda
- Pastikan memberikan akses ke repository **PhamRipki/windprediction**

### 3. Deploy Aplikasi Baru
1. Setelah login, klik tombol **"New app"** atau **"Create app"**
2. Isi form deployment:
   - **Repository**: `PhamRipki/windprediction`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (optional): Pilih nama custom atau biarkan default

### 4. Advanced Settings (Optional tapi Direkomendasikan)
Klik **"Advanced settings"** dan sesuaikan:
- **Python version**: `3.9` atau `3.10` (recommended)
- **Secrets**: Tidak diperlukan untuk aplikasi ini
- **Resources**: Biarkan default (kecuali jika perlu lebih)

### 5. Deploy!
- Klik tombol **"Deploy!"**
- Tunggu proses deployment (5-10 menit pertama kali)
- Streamlit Cloud akan:
  - Clone repository dari GitHub
  - Install dependencies dari `requirements.txt`
  - Download file LFS (model files)
  - Menjalankan aplikasi

### 6. Monitoring Deployment
Anda bisa melihat log proses deployment di panel sebelah kanan:
- ✅ Installing dependencies...
- ✅ Downloading LFS files...
- ✅ Running app.py...
- ✅ App is live! 🎉

---

## URL Aplikasi
Setelah berhasil deploy, aplikasi dapat diakses di:
```
https://phamripki-windprediction-app-xxxxx.streamlit.app
```

Atau URL custom jika Anda set saat deployment.

---

## Troubleshooting

### Problem: Error saat install TensorFlow
**Solusi**: TensorFlow terlalu besar untuk Streamlit Cloud free tier.
Ganti di `requirements.txt`:
```
tensorflow-cpu>=2.13.0
```
Lalu push perubahan:
```cmd
git add requirements.txt
git commit -m "Use tensorflow-cpu for smaller footprint"
git push origin main
```

### Problem: Out of Memory
**Solusi**: Streamlit Cloud free tier memiliki limit 1GB RAM.
Kurangi `history_window` di `app.py` line 129 dari 100 ke 50:
```python
history_window = 50  # Kurangi dari 100
```

### Problem: Model tidak ter-load
**Solusi**: Pastikan Git LFS berfungsi:
```cmd
git lfs ls-files
```
Harus menampilkan 4 file model.

### Problem: Deployment Failed
**Solusi**: 
1. Cek Streamlit Cloud logs untuk error spesifik
2. Pastikan repository public (bukan private)
3. Restart deployment dari dashboard Streamlit Cloud

---

## Update Aplikasi
Setiap kali Anda push perubahan ke GitHub, Streamlit Cloud akan otomatis:
1. Detect perubahan di branch `main`
2. Re-deploy aplikasi secara otomatis
3. Update aplikasi dalam 2-3 menit

Untuk push update:
```cmd
git add .
git commit -m "Update: deskripsi perubahan"
git push origin main
```

---

## Resource Limits (Free Tier)
- **RAM**: 1 GB
- **CPU**: 1 shared core
- **Storage**: 1 GB
- **Bandwidth**: Fair use policy
- **Apps**: Max 3 apps per account

---

## Upgrade ke Paid Plan (Jika Diperlukan)
Jika aplikasi membutuhkan resource lebih:
- **Starter**: $20/month - 2GB RAM, 2 apps
- **Teams**: $250/month - 4GB RAM, unlimited apps

---

## Support & Help
- Dokumentasi: https://docs.streamlit.io/streamlit-community-cloud
- Forum: https://discuss.streamlit.io
- GitHub Issues: https://github.com/streamlit/streamlit/issues

---

✅ **Repository sudah siap untuk di-deploy!**
Silakan ikuti langkah-langkah di atas untuk mendeploy aplikasi ke Streamlit Cloud.
