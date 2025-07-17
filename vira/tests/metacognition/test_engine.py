"""
MetaCognitive Engine testleri.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from vira.metacognition.engine import MetaCognitiveEngine
from vira.metacognition.models import UserMentalModel

class TestMetaCognitiveEngine(unittest.TestCase):
    """MetaCognitiveEngine için test sınıfı."""
    
    def setUp(self):
        """Test öncesi hazırlık."""
        # Mock repository'ler oluştur
        self.memory_repo = MagicMock()
        self.personality_repo = MagicMock()
        self.conversation_repo = MagicMock()
        
        # Mock db_repos nesnesi
        self.db_repos = MagicMock()
        self.db_repos.get_memory_repository.return_value = self.memory_repo
        self.db_repos.get_personality_repository.return_value = self.personality_repo
        self.db_repos.get_conversation_repository.return_value = self.conversation_repo
        
        # Test edilecek nesne
        self.engine = MetaCognitiveEngine(self.db_repos)
    
    def test_build_unified_user_model_creates_valid_model(self):
        """build_unified_user_model geçerli bir model oluşturmalı."""
        # Arrange
        user_id = "test-user-123"
        
        # Mock verileri ayarla
        self.conversation_repo.get_recent_conversations.return_value = []
        self.personality_repo.get_personality_history.return_value = []
        self.memory_repo.get_long_term_memories.return_value = []
        self.conversation_repo.get_all_conversations.return_value = []
        
        # Act
        model = self.engine.build_unified_user_model(user_id)
        
        # Assert
        self.assertEqual(model.user_id, user_id)
        self.assertIsNotNone(model.current_state)
        self.assertIsNotNone(model.personality_trends)
        self.assertIsNotNone(model.memory_themes)
        self.assertIsNotNone(model.conversation_patterns)
    
    def test_to_dict_creates_valid_dict(self):
        """UserMentalModel.to_dict geçerli bir sözlük oluşturmalı."""
        # Arrange
        user_id = "test-user-123"
        model = UserMentalModel(user_id)
        
        # Act
        model_dict = model.to_dict()
        
        # Assert
        self.assertEqual(model_dict["user_id"], user_id)
        self.assertIn("created_at", model_dict)
        self.assertIn("personality_trends", model_dict)
        self.assertIn("memory_themes", model_dict)
        self.assertIn("conversation_patterns", model_dict)
    
    def test_from_dict_creates_valid_model(self):
        """UserMentalModel.from_dict geçerli bir model oluşturmalı."""
        # Arrange
        user_id = "test-user-123"
        now = datetime.now()
        model_dict = {
            "user_id": user_id,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "current_state": {"emotional_state": {}, "topic_focus": [], "interaction_mode": "", "recent_context": {}},
            "personality_trends": {"empathy": {"current": 0.5, "trend": 0.0}},
            "memory_themes": {"dominant_topics": []},
            "conversation_patterns": {"preferred_topics": []}
        }
        
        # Act
        model = UserMentalModel.from_dict(model_dict)
        
        # Assert
        self.assertEqual(model.user_id, user_id)
        self.assertEqual(model.created_at.date(), now.date())
        self.assertEqual(model.personality_trends["empathy"]["current"], 0.5)

if __name__ == "__main__":
    unittest.main()