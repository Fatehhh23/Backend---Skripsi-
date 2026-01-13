# PostgreSQL + PostGIS Setup Guide

Panduan lengkap instalasi dan konfigurasi PostgreSQL dengan PostGIS extension untuk AVATAR Tsunami Prediction System.

## 📋 Prerequisites

- Windows 10/11
- Hak akses Administrator
- Koneksi internet untuk download

## 🚀 Langkah 1: Install PostgreSQL

### Download PostgreSQL

1. Kunjungi: https://www.postgresql.org/download/windows/
2. Download **PostgreSQL 15** atau versi terbaru (pilih installer dari EnterpriseDB)
3. URL Direct: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

### Install PostgreSQL

1. **Jalankan installer** `postgresql-15.x-windows-x64.exe`

2. **Installation Directory** (default):
   ```
   C:\Program Files\PostgreSQL\15
   ```

3. **Select Components** - Pilih SEMUA:
   - [x] PostgreSQL Server
   - [x] pgAdmin 4
   - [x] Stack Builder
   - [x] Command Line Tools

4. **Data Directory** (default):
   ```
   C:\Program Files\PostgreSQL\15\data
   ```

5. **Password** - Set password untuk user `postgres`:
   ```
   Password: AVATAR23
   ```
   > ⚠️ **PENTING**: Ingat password ini!

6. **Port**: 
   ```
   5432 (default)
   ```

7. **Locale**: 
   ```
   [Default locale]
   ```

8. Klik **Next** → **Next** → **Finish**

9. ⏳ Tunggu hingga instalasi selesai

## 🌍 Langkah 2: Install PostGIS Extension

### Menggunakan Stack Builder

1. Setelah PostgreSQL terinstall, **Stack Builder** akan otomatis terbuka
   - Jika tidak, cari "Stack Builder" di Start Menu

2. **Pilih PostgreSQL Installation**:
   ```
   PostgreSQL 15 (x64) on port 5432
   ```

3. **Expand "Spatial Extensions"**:
   - [x] **PostGIS 3.3 Bundle** for PostgreSQL 15 (x64)

4. Klik **Next** → **Next** → Download

5. Setelah download selesai, installer PostGIS akan otomatis jalan

6. **PostGIS Installation**:
   - Accept license
   - Installation directory (default): `C:\Program Files\PostgreSQL\15`
   - Components:
     - [x] PostGIS
     - [x] Create spatial database
   - Klik **Next** → **Install**

7. **Register Environment Variables**: Yes

8. Klik **Close** saat selesai

### Verifikasi PostGIS

Buka **SQL Shell (psql)** dari Start Menu:

```sql
-- Login
Server [localhost]: 
Database [postgres]: 
Port [5432]: 
Username [postgres]: 
Password for user postgres: AVATAR23

-- Check PostGIS version
SELECT PostGIS_Version();
```

Expected output:
```
 postgis_version 
-----------------
 3.3.x
```

## 🗄️ Langkah 3: Setup Database

### Opsi A: Menggunakan SQL Script (Recommended)

1. Buka **SQL Shell (psql)**

2. Login sebagai postgres:
   ```
   Password for user postgres: AVATAR23
   ```

3. Jalankan script setup:
   ```sql
   \i 'C:/Users/Fatihh/OneDrive/Documents/BISMILLAH SKRIPSI/Fullstack WEB AVATA (AntiGravity)/Backend---Skripsi-/database_setup.sql'
   ```

4. Tunggu hingga selesai. Output harus menampilkan:
   ```
   Database Setup Complete!
   ```

### Opsi B: Manual Setup

1. Buka **pgAdmin 4** dari Start Menu

2. Login (password: `AVATAR23`)

3. **Create Database**:
   - Right-click **Databases** → **Create** → **Database**
   - Name: `tsunamidb`
   - Owner: `postgres`
   - Click **Save**

4. **Enable PostGIS**:
   - Expand `tsunamidb` → Right-click **Extensions**
   - Click **Create** → **Extension**
   - Name: `postgis`
   - Click **Save**
   - Repeat untuk `postgis_topology`

5. **Verify PostGIS**:
   - Tools → Query Tool
   - Run:
     ```sql
     SELECT PostGIS_Version();
     ```

6. **Create Tables**:
   - Tools → Query Tool
   - Copy isi dari `database_setup.sql` (bagian CREATE TABLE)
   - Execute

## 🔧 Langkah 4: Configure Backend Connection

### Update .env File

1. Buka file `.env` di root folder Backend:
   ```
   Backend---Skripsi-\.env
   ```

2. Update DATABASE_URL:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:AVATAR23@localhost:5432/tsunamidb
   ```

### Test Connection

1. Buka terminal di folder Backend

2. Test Python connection:
   ```python
   python -c "from app.database.connection import get_db; print('Connection OK!')"
   ```

3. Atau restart backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Check health endpoint:
   ```bash
   curl http://localhost:8000/api/health
   ```

   Expected: Status should be "healthy" if database connected

## ✅ Verifikasi Setup

### Check Database

```sql
-- Login to psql
psql -U postgres -d tsunamidb

-- Check tables
\dt

-- Check PostGIS functions
SELECT name, default_version 
FROM pg_available_extensions 
WHERE name LIKE 'postgis%';

-- Check sample data
SELECT COUNT(*) FROM coastlines;

-- Test spatial function
SELECT calculate_distance(-6.102, 105.423, -6.200, 105.500);
```

### Check Backend Connection

```bash
# Test via Python
cd Backend---Skripsi-
python -c "import asyncio; from app.database.connection import engine; asyncio.run(engine.dispose())"
```

## 🛠️ Troubleshooting

### PostgreSQL Service Not Running

```powershell
# Check service status
Get-Service -Name postgresql-x64-15

# Start service
Start-Service postgresql-x64-15
```

### Cannot Connect to Database

1. **Check password**: Pastikan menggunakan `AVATAR23`
2. **Check port**: Default 5432
3. **Check pg_hba.conf**:
   ```
   C:\Program Files\PostgreSQL\15\data\pg_hba.conf
   ```
   Pastikan ada line:
   ```
   host    all    all    127.0.0.1/32    md5
   ```

### PostGIS Extension Not Found

Re-install PostGIS via Stack Builder:
1. Buka Stack Builder
2. Pilih PostgreSQL installation
3. Install PostGIS Bundle

## 📊 Database Schema

### Tables Created

| Table | Description | Geometry Type |
|-------|-------------|---------------|
| `simulations` | Simulation history | Point (epicenter) |
| `earthquakes` | Earthquake data | Point (location) |
| `inundation_zones` | Tsunami inundation areas | Polygon |
| `coastlines` | Reference coastline data | LineString |

### Views Created

- `v_recent_simulations` - 100 simulasi terbaru
- `v_earthquake_stats` - Statistik gempa

### Functions Created

- `calculate_distance(lat1, lon1, lat2, lon2)` - Hitung jarak (km)
- `is_in_sunda_strait(lat, lon)` - Check koordinat di Selat Sunda

## 📚 Useful Commands

### psql Commands

```sql
\l              -- List databases
\c tsunamidb    -- Connect to database
\dt             -- List tables
\d simulations  -- Describe table
\df             -- List functions
\dv             -- List views
\dx             -- List extensions
\q              -- Quit
```

### Backup Database

```powershell
# Backup
pg_dump -U postgres -d tsunamidb -F c -f tsunamidb_backup.dump

# Restore
pg_restore -U postgres -d tsunamidb tsunamidb_backup.dump
```

## 🔗 Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- PostGIS Documentation: https://postgis.net/documentation/
- pgAdmin Documentation: https://www.pgadmin.org/docs/

---

## ✅ Next Steps

Setelah database setup berhasil:

1. ✅ Uncomment geometry columns di `app/database/models.py`
2. ✅ Uncomment geospatial imports di `app/database/crud.py`
3. ✅ Install geospatial Python libraries (optional):
   ```bash
   pip install geoalchemy2 shapely
   ```
4. ✅ Restart backend server
5. ✅ Test simulation endpoints dengan data real

---

**Setup Complete! Database ready untuk Tsunami Prediction System** 🌊
