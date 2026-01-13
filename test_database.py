"""
Script Test Koneksi Database
Skrip untuk menguji koneksi ke PostgreSQL database dan PostGIS
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


async def test_connection():
    """
    Test koneksi dasar ke database
    Mengecek PostgreSQL dan PostGIS sudah terinstall dengan benar
    """
    print("🔍 Menguji Koneksi Database...")
    print("-" * 60)
    
    # URL koneksi database
    DATABASE_URL = "postgresql+asyncpg://postgres:AVATAR23@localhost:5432/tsunamidb"
    print(f"📍 Database URL: {DATABASE_URL}")
    print()
    
    try:
        # Buat engine database
        engine = create_async_engine(DATABASE_URL, echo=False)
        
        # Test koneksi
        async with engine.connect() as conn:
            # Cek versi PostgreSQL
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Versi PostgreSQL: {version[:60]}...")
            
            # Cek versi PostGIS
            try:
                result = await conn.execute(text("SELECT PostGIS_Version()"))
                postgis_version = result.scalar()
                print(f"✅ Versi PostGIS: {postgis_version}")
            except Exception as e:
                print(f"⚠️  PostGIS belum terinstall: {e}")
                return False
            
            # Cek nama database
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"✅ Database Aktif: {db_name}")
            
            # List semua tabel
            result = await conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"\n📊 Tabel dalam database:")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print(f"\n⚠️  Belum ada tabel. Jalankan database_setup.sql terlebih dahulu!")
                return False
            
            # Cek ekstensi PostGIS
            result = await conn.execute(text("""
                SELECT name, default_version, installed_version
                FROM pg_available_extensions 
                WHERE name LIKE 'postgis%' AND installed_version IS NOT NULL
            """))
            extensions = result.fetchall()
            
            if extensions:
                print(f"\n🌍 Ekstensi PostGIS:")
                for ext in extensions:
                    print(f"   - {ext[0]} v{ext[2]}")
            else:
                print(f"\n⚠️  Ekstensi PostGIS belum diaktifkan!")
                return False
            
            # Hitung jumlah record di setiap tabel
            if tables:
                print(f"\n📈 Statistik Tabel:")
                for table in tables:
                    result = await conn.execute(text(f"SELECT COUNT(*) FROM {table[0]}"))
                    count = result.scalar()
                    print(f"   - {table[0]}: {count} baris")
        
        await engine.dispose()
        
        print("\n" + "=" * 60)
        print("✅ Test koneksi database BERHASIL!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Test koneksi database GAGAL!")
        print(f"Error: {e}")
        print("=" * 60)
        print("\n💡 Troubleshooting:")
        print("   1. Cek PostgreSQL sudah berjalan:")
        print("      Get-Service -Name postgresql-x64-15")
        print("   2. Verifikasi database sudah dibuat:")
        print("      psql -U postgres -l")
        print("   3. Periksa username/password di DATABASE_URL")
        print("   4. Jalankan database_setup.sql terlebih dahulu")
        return False


async def test_spatial_query():
    """
    Test query spatial PostGIS
    Menguji fungsi-fungsi spatial seperti calculate_distance
    """
    print("\n🗺️  Menguji Query Spatial PostGIS...")
    print("-" * 60)
    
    DATABASE_URL = "postgresql+asyncpg://postgres:AVATAR23@localhost:5432/tsunamidb"
    
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        
        async with engine.connect() as conn:
            # Test fungsi hitung jarak
            print("📏 Test fungsi calculate_distance:")
            result = await conn.execute(text("""
                SELECT calculate_distance(-6.102, 105.423, -6.200, 105.500) as distance_km
            """))
            distance = result.scalar()
            print(f"   Jarak Anyer ke Carita: {distance:.2f} km")
            
            # Test fungsi cek Selat Sunda
            print("\n🌊 Test fungsi is_in_sunda_strait:")
            result = await conn.execute(text("""
                SELECT is_in_sunda_strait(-6.102, 105.423) as is_in_strait
            """))
            in_strait = result.scalar()
            if in_strait:
                print(f"   Koordinat (-6.102, 105.423): ✅ Di Selat Sunda")
            else:
                print(f"   Koordinat (-6.102, 105.423): ❌ Bukan di Selat Sunda")
            
            # Test data garis pantai
            print("\n🏖️  Data Garis Pantai:")
            result = await conn.execute(text("""
                SELECT name, region, length_km 
                FROM coastlines 
                ORDER BY length_km DESC
            """))
            coastlines = result.fetchall()
            
            if coastlines:
                for coastline in coastlines:
                    print(f"   - {coastline[0]} ({coastline[1]}): {coastline[2]} km")
            else:
                print("   ⚠️  Belum ada data garis pantai")
            
            # Test view simulasi
            print("\n📊 Test View v_recent_simulations:")
            result = await conn.execute(text("""
                SELECT COUNT(*) FROM v_recent_simulations
            """))
            count = result.scalar()
            print(f"   Jumlah simulasi dalam view: {count}")
            
        await engine.dispose()
        
        print("\n✅ Test query spatial BERHASIL!")
        return True
        
    except Exception as e:
        print(f"\n⚠️  Test query spatial GAGAL: {e}")
        print("   Pastikan database_setup.sql sudah dijalankan dengan benar")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("  AVATAR Backend - Test Database")
    print("=" * 60)
    print()
    
    # Jalankan test
    connection_ok = asyncio.run(test_connection())
    
    if connection_ok:
        spatial_ok = asyncio.run(test_spatial_query())
        
        if spatial_ok:
            print("\n" + "🎉" * 20)
            print("SEMUA TEST BERHASIL! Database siap digunakan.")
            print("🎉" * 20)
            print("\n📝 Langkah selanjutnya:")
            print("   1. Update .env dengan DATABASE_URL yang benar")
            print("   2. Uncomment geometry columns di app/database/models.py")
            print("   3. Uncomment geospatial imports di app/database/crud.py")
            print("   4. Install: pip install geoalchemy2 shapely")
            print("   5. Restart backend server")
            print()
            sys.exit(0)
        else:
            print("\n⚠️  Koneksi OK, tapi fitur spatial perlu setup")
            sys.exit(1)
    else:
        print("\n❌ Koneksi database gagal. Perbaiki dan coba lagi.")
        print("\n📖 Baca DATABASE_SETUP.md untuk panduan lengkap")
        sys.exit(1)
