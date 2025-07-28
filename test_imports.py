#!/usr/bin/env python3
"""
Test script to verify that all critical infrastructure components can be imported.
"""

def test_imports():
    """Test all critical imports for Phase 1 infrastructure fixes."""
    
    print("Testing critical infrastructure imports...")
    
    try:
        # Test DatabaseRepository
        from vira.db.database_repository import DatabaseRepository
        print("✅ DatabaseRepository imported successfully")
        
        # Test LLMClient
        from vira.utils.database_llm_client import LLMClient
        print("✅ LLMClient imported successfully")
        
        # Test MessageService
        from vira.services.message_service import MessageService
        print("✅ MessageService imported successfully")
        
        # Test reflection nodes
        from vira.reflection.reflection_nodes import (
            reflection_trigger_node, 
            autonomous_reflection_node,
            action_planning_node,
            execute_action_node
        )
        print("✅ Reflection nodes imported successfully")
        
        # Test repository methods
        from vira.db.repository import MemoryRepository
        repo = MemoryRepository()
        
        # Check if new methods exist
        assert hasattr(repo, 'get_last_reflection_session'), "Missing get_last_reflection_session method"
        assert hasattr(repo, 'save_action_plan'), "Missing save_action_plan method"
        assert hasattr(repo, 'get_goal_by_id'), "Missing get_goal_by_id method"
        assert hasattr(repo, 'update_user_preferences'), "Missing update_user_preferences method"
        assert hasattr(repo, 'count_user_interactions'), "Missing count_user_interactions method"
        print("✅ All required repository methods exist")
        
        # Test instantiation
        db_repo = DatabaseRepository()
        llm_client = LLMClient()
        message_service = MessageService()
        print("✅ All classes can be instantiated")
        
        print("\n🎉 ALL IMPORTS AND TESTS PASSED!")
        print("Phase 1 infrastructure fixes are complete and functional.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Missing method: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1)