"""
Script untuk create users table di database
Run setelah Docker container running
"""

from app.database.connection import engine, Base
from app.database.models import User, UserRole
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ All tables created successfully!")
        logger.info("Tables created: users, simulations, earthquakes, inundation_zones, coastlines")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_tables()
