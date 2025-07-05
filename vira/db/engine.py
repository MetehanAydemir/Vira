from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from vira.config import settings
from vira.utils.logger import get_logger
from contextlib import contextmanager

logger = get_logger(__name__)

# Create database URL
DB_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# Create engine
engine = create_engine(DB_URL)

# Create session factory
session_factory = sessionmaker(bind=engine)
SessionLocal = scoped_session(session_factory)

# Base class for models
Base = declarative_base()


def get_db_session():
    """Get a new database session."""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        pass  # Don't close the session here, let the caller close it


@contextmanager
def db_session():
    """
    Context manager for database sessions.

    Usage:
        with db_session() as session:
            # Use session for database operations
            result = session.query(Model).filter(Model.id == 1).first()

    The session will be automatically committed if no exceptions occur,
    rolled back if an exception occurs, and always closed at the end.
    """
    session = SessionLocal()
    try:
        # Provide the session to the caller
        yield session

        # If we get here, no exception was raised, so commit the transaction
        session.commit()
        logger.debug("Database transaction committed successfully")
    except Exception as e:
        # An exception occurred, roll back the transaction
        session.rollback()
        logger.error(f"Database transaction rolled back due to error: {e}")
        # Re-raise the exception to be handled by the caller
        raise
    finally:
        # Always close the session
        session.close()
        logger.debug("Database session closed")


def drop_all_tables():
    """Tüm tabloları sil."""
    try:
        with engine.connect() as connection:
            # Önce indeksleri sil
            connection.execute(text("DROP INDEX IF EXISTS idx_long_term_memory_metadata_gin"))
            connection.execute(text("DROP INDEX IF EXISTS idx_long_term_memory_embedding"))
            connection.commit()

        # Sonra tabloları sil
        Base.metadata.drop_all(bind=engine)
        logger.info("Tüm tablolar başarıyla silindi")
    except Exception as e:
        logger.error(f"Tablolar silinirken hata oluştu: {e}")
        raise


def init_db(force_recreate=False):
    """
    Initialize database schema.

    Args:
        force_recreate (bool): If True, drop all tables and recreate them
    """
    # Import all models to ensure they are registered with Base.metadata
    from vira.db.models import Base, LongTermMemory, ShortTermMemory, User, Interaction

    try:
        # Eğer force_recreate True ise, tüm tabloları sil ve yeniden oluştur
        if force_recreate:
            drop_all_tables()
            logger.info("Tüm tablolar silindi, yeniden oluşturuluyor...")

        # Create vector extension
        with engine.connect() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            connection.commit()
            logger.info("Vector extension created successfully")

        # Create all tables from SQLAlchemy models
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created from SQLAlchemy models")

        # Create GIN index for metadatas
        try:
            with engine.connect() as connection:
                sql = text("""
                CREATE INDEX IF NOT EXISTS idx_long_term_memory_metadata_gin 
                ON long_term_memory USING gin (metadatas)
                """)
                connection.execute(sql)
                connection.commit()
                logger.info("GIN index created successfully")
        except Exception as e:
            logger.warning(f"GIN indeksi oluşturulurken hata oluştu: {e}")
            # Bu hatayı yut ve devam et, çünkü bu kritik bir hata değil

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def create_ivfflat_index():
    """
    Create the ivfflat index for vector similarity search.
    This should be called after the table has data.
    """
    try:
        with engine.connect() as connection:
            # Önce tabloda veri olup olmadığını kontrol et
            count_sql = text("SELECT COUNT(*) FROM long_term_memory")
            count = connection.execute(count_sql).scalar()

            if count > 10:  # En az 10 veri olsun
                sql = text("""
                CREATE INDEX IF NOT EXISTS idx_long_term_memory_embedding 
                ON long_term_memory USING ivfflat (embedding vector_l2_ops) 
                WITH (lists = 100)
                """)
                connection.execute(sql)
                connection.commit()
                logger.info("ivfflat index created successfully")
            else:
                logger.warning(f"Not enough data to create ivfflat index. Current count: {count}, required: 10")
    except Exception as e:
        logger.error(f"Failed to create ivfflat index: {e}")
        raise