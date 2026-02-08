# 🔄 Quick Restart - AVATAR System

## ⚠️ LANGKAH WAJIB #1: Stop PostgreSQL Windows

**Pilih salah satu:**

### Otomatis (Run as Administrator):
```powershell
cd "c:\Skripsi_Fatihh\Fullstack WEB AVATA (AntiGravity)\Backend---Skripsi-"
.\fix_port_conflict.ps1
```

### Manual:
1. `Win + R` → `services.msc`
2. Cari `postgresql-x64-16`
3. Klik kanan → **Stop**
4. (Optional) Properties → Startup: **Disabled**

---

## 🚀 Start Aplikasi

### 1. Start Docker Desktop
- Cari "Docker Desktop" di Start Menu
- Tunggu icon hijau di taskbar

### 2. Start Containers
```powershell
cd "c:\Skripsi_Fatihh\Fullstack WEB AVATA (AntiGravity)\Backend---Skripsi-"
docker-compose up -d
```

### 3. Start Frontend (Terminal Baru)
```powershell
cd "c:\Skripsi_Fatihh\Fullstack WEB AVATA (AntiGravity)\Frontend-Skripsi-"
npm run dev
```

### 4. Buka Browser
- `http://localhost:3000`
- atau `http://192.168.x.x:3000`

---

## 🔐 pgAdmin Access

URL: `http://localhost:5050`

**Login:**
- Email: `admin@avatar.com`
- Password: `admin`

**Connect Database (Pertama Kali):**
- Host: `tsunami_db` (atau `localhost`)
- Port: `5432`
- DB: `tsunami_db`
- User: `tsunami_user`
- Pass: `tsunami_password`
- ✅ Save password

**Setelah pertama kali:**
- Klik server "Tsunami DB"
- Masukkan password jika diminta
- ✅ Langsung connect!

---

## 🎯 One-Click Start (Bonus)

**Double-click:**
```
start_avatar.bat
```

Otomatis start semua!

---

## 📞 Troubleshoot

**Port conflict?** → Jalankan `fix_port_conflict.ps1`  
**pg password failed?** → Stop PostgreSQL Windows  
**CORS error?** → `Ctrl + Shift + R` (hard refresh)

---

📖 **Panduan lengkap:** [PANDUAN_RESTART.md](file:///C:/Users/Fatihh/.gemini/antigravity/brain/564cd8f8-dca1-45c7-95f7-d0de74e4e3ec/PANDUAN_RESTART.md)
