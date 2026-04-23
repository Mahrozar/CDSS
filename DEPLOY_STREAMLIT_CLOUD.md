# Deploy Gratis ke Streamlit Community Cloud

## 1) Siapkan repository GitHub

- Buat repository baru di GitHub.
- Upload file berikut:
  - `app.py`
  - `rules.py`
  - `inference.py`
  - `requirements.txt`
  - `.gitignore`
  - `sample_test_data.csv` (opsional, untuk demo)

## 2) Push project dari lokal

Jalankan di folder project:

```powershell
git init
git add .
git commit -m "Initial CDSS rule-based app"
git branch -M main
git remote add origin https://github.com/USERNAME/NAMA-REPO.git
git push -u origin main
```

Jika repository sudah ada, cukup:

```powershell
git add .
git commit -m "Prepare deployment"
git push
```

## 3) Deploy di Streamlit Community Cloud

- Buka https://share.streamlit.io/
- Login dengan akun GitHub.
- Klik **Create app**.
- Pilih repository, branch `main`, dan file utama `app.py`.
- Klik **Deploy**.

## 4) Verifikasi aplikasi

Setelah build selesai, buka URL aplikasi dan cek:

- Tab **Analisis Individu** berjalan.
- Tab **Analisis Batch CSV** bisa upload file CSV.
- Hasil menampilkan risiko, traceability, dan ringkasan rule.

## 5) Update aplikasi setelah deploy

Setiap ada perubahan kode:

```powershell
git add .
git commit -m "Update CDSS logic/UI"
git push
```

Streamlit Cloud akan otomatis rebuild.

## Catatan penting untuk TA

- Sistem ini **rule-based** dan **tidak menggunakan machine learning**.
- Dataset digunakan sebagai data simulasi inferensi, bukan training model.
- Untuk demo online, gunakan file CSV yang tidak terlalu besar agar respon cepat.
