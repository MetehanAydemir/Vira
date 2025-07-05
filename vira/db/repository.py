import numpy as np
from sqlalchemy import text
from contextlib import contextmanager
from vira.db.engine import db_session
from vira.db.models import LongTermMemory
from vira.utils.logger import get_logger
from sqlalchemy import text, select, and_

logger = get_logger(__name__)


class MemoryRepository:
    """Repository for memory operations using SQLAlchemy."""

    def store_memory(self, user_id: str, content: str, embedding: np.ndarray):
        """Store a memory entry with its embedding in the database."""
        try:
            # Use the context manager for session management
            with db_session() as session:
                # Store user_id in meta_data field
                metadatas = {'user_id': user_id}

                memory = LongTermMemory(
                    content=content,
                    metadatas=metadatas,  # Changed from metadata to meta_data
                    embedding=embedding.tolist()
                )
                session.add(memory)
                # No need to commit here, the context manager will do it

                # Refresh to get the ID (still within the transaction)
                session.flush()
                memory_id = memory.id

            # Session is now committed and closed
            logger.info(f"Memory stored with ID: {memory_id}")
            return memory_id
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise

    def retrieve_similar_memories(self, user_id: str, embedding: np.ndarray, top_k: int = 3):
        """Retrieve the most similar memories based on embedding similarity."""
        try:
            with db_session() as session:
                # Using raw SQL with SQLAlchemy for vector similarity search
                # Filter by user_id in meta_data field
                memories = session.scalars(
                    select(LongTermMemory)
                    .filter(LongTermMemory.metadatas['user_id'].astext == user_id)
                    .order_by(LongTermMemory.embedding.cosine_distance(embedding.tolist()))
                    .limit(top_k)
                ).all()
                result = []
                for memory in memories:
                    # Cosine similarity = 1 - cosine distance
                    distance = session.scalar(
                        select(LongTermMemory.embedding.cosine_distance(embedding.tolist()))
                        .where(LongTermMemory.id == memory.id)
                    )
                    similarity = 1 - distance
                    result.append((memory.content, float(similarity)))

            logger.info(f"Retrieved {len(result)} similar memories for user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to retrieve similar memories: {e}")
            return []