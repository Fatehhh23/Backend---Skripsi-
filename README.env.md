# Environment Configuration

The `.env` file is required for running the backend application but is gitignored for security.

## Setup Instructions

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your specific configuration:

### Database Configuration
Update the `DATABASE_URL` with your PostgreSQL credentials:
```env
DATABASE_URL=postgresql+asyncpg://postgres:AVATAR23@localhost:5432/tsunamidb
```

Default configuration (from `config.py`):
- **User**: `postgres`
- **Password**: `AVATAR23`
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `tsunamidb`

### Important Configuration Options

- **DEBUG**: Set to `False` in production
- **ALLOWED_ORIGINS**: Add your frontend URL(s)
- **MODEL_PATH**: Path to your trained ONNX model
- **USE_GPU**: Set to `True` if you have CUDA-capable GPU
- **ENABLE_REALTIME_MONITORING**: Enable/disable earthquake monitoring

## Quick Start

For development, you can use the default configuration by simply copying `.env.example`:

```bash
# Windows PowerShell
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

The default configuration will work if you:
1. Have PostgreSQL running on localhost:5432
2. Created database named `tsunamidb`
3. Have user `postgres` with password `AVATAR23`

## Production Deployment

For production, make sure to:
- Set `DEBUG=False`
- Use strong database credentials
- Configure proper CORS origins
- Set up proper logging paths
- Enable security features
