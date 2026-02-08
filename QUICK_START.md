# 🚀 Quick Start - AVATAR Tsunami System

## 1️⃣ Start Docker Desktop
- Cari "Docker Desktop" di Start Menu
- Tunggu icon hijau di taskbar

## 2️⃣ Start Backend + Database
```powershell
cd "c:\Skripsi_Fatihh\Fullstack WEB AVATA (AntiGravity)\Backend---Skripsi-"
docker-compose up -d
```

## 3️⃣ Start Frontend (Terminal Baru)
```powershell
cd "c:\Skripsi_Fatihh\Fullstack WEB AVATA (AntiGravity)\Frontend-Skripsi-"
npm run dev
```

## 4️⃣ Buka Browser
- URL: `http://localhost:3000`
- Hard Refresh: `Ctrl + Shift + R`

## 5️⃣ Test Simulasi
- Isi form dengan data gempa
- Klik "Jalankan Simulasi"
- Lihat hasil prediksi

## 6️⃣ Verify Database
```powershell
docker exec tsunami_db psql -U tsunami_user -d tsunami_db -c "SELECT COUNT(*) FROM simulations;"
```

---

## 🔑 Credentials Quick Ref

**Database:**
- Host: `localhost`
- Port: `5432`
- DB: `tsunami_db`
- User: `tsunami_user`
- Pass: `tsunami_password`

**pgAdmin:**
- URL: `http://localhost:5050`
- Email: `admin@avatar.com`
- Pass: `admin`

---

## ⚠️ Troubleshoot

**Data tidak masuk?**
→ Hard refresh browser (`Ctrl + Shift + R`)

**Port 5432 conflict?**
→ Stop PostgreSQL Windows service

**Container error?**
→ `docker-compose down && docker-compose up -d`

---

📖 **Panduan lengkap:** [PANDUAN_MENJALANKAN_APLIKASI.md](./PANDUAN_MENJALANKAN_APLIKASI.md)
