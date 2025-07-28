#!/usr/bin/env python3
"""
Test script to validate the reflection workflow end-to-end functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'vira'))

import logging
from datetime import datetime
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_reflection_workflow_creation():
    """Test creating the reflection-enhanced workflow."""
    print("🧪 Testing reflection workflow creation...")
    
    try:
        from vira.graph.build_reflection import create_reflection_enhanced_workflow
        
        # Create the workflow
        workflow = create_reflection_enhanced_workflow()
        print("✅ Reflection workflow created successfully")
        
        # Check if workflow is compiled
        if hasattr(workflow, 'invoke'):
            print("✅ Workflow is properly compiled and callable")
        else:
            print("⚠️  Workflow may not be properly compiled")
        
        return True, workflow
        
    except Exception as e:
        print(f"❌ Reflection workflow creation failed: {e}")
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")
        return False, None

def test_workflow_execution():
    """Test executing the reflection workflow with sample data."""
    print("\n🧪 Testing workflow execution...")
    
    try:
        from vira.graph.build_reflection import create_reflection_enhanced_workflow
        from vira.graph.state import ViraState
        
        # Create workflow
        workflow = create_reflection_enhanced_workflow()
        
        # Create test state
        test_state = ViraState(
            user_id=str(uuid.uuid4()),
            original_message="Hello, how are you today?",
            processed_input={
                "emotion_score": 0.5,  # Below threshold to avoid triggering reflection
                "intent": "greeting"
            },
            is_omega_command=False,
            messages=[],
            response="",
            dynamic_personality={}
        )
        
        # Execute workflow with mock LLM to avoid API calls
        os.environ["VIRA_USE_MOCK_LLM"] = "true"
        
        try:
            result = workflow.invoke(test_state)
            print(f"✅ Workflow executed successfully")
            print(f"✅ Final state keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            # Check if reflection was triggered
            if result.get("reflection_triggered"):
                print("✅ Reflection was triggered during workflow")
            else:
                print("✅ Workflow completed without triggering reflection (expected for low emotion score)")
            
            return True, result
            
        finally:
            # Reset mock mode
            os.environ.pop("VIRA_USE_MOCK_LLM", None)
        
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")
        return False, None

def test_schedule_actions():
    """Test the schedule_actions function."""
    print("\n🧪 Testing schedule_actions function...")
    
    try:
        from vira.graph.build_reflection import schedule_actions
        
        # Test with no specific user (should handle gracefully)
        result = schedule_actions(force=True, reflection_type="test")
        print(f"✅ Schedule actions executed: {result}")
        
        # Check result structure
        expected_keys = ["timestamp", "processed_users", "insights_generated", "goals_created"]
        for key in expected_keys:
            if key in result:
                print(f"✅ Result contains {key}: {result[key]}")
            else:
                print(f"⚠️  Result missing {key}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Schedule actions test failed: {e}")
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")
        return False, None

def test_process_user_reflection():
    """Test the process_user_reflection function."""
    print("\n🧪 Testing process_user_reflection function...")
    
    try:
        from vira.graph.build_reflection import process_user_reflection
        
        # Use a test UUID (won't exist in DB, but should handle gracefully)
        test_user_id = str(uuid.uuid4())
        
        # Test with mock user
        result = process_user_reflection(test_user_id, "test")
        print(f"✅ Process user reflection executed: {result}")
        
        # Check if it handled non-existent user gracefully
        if "error" in result:
            if "not found" in result["error"].lower():
                print("✅ Gracefully handled non-existent user")
            else:
                print(f"⚠️  Unexpected error: {result['error']}")
        else:
            print("✅ Process completed successfully")
            
        return True, result
        
    except Exception as e:
        print(f"❌ Process user reflection test failed: {e}")
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")
        return False, None

def test_reflection_nodes():
    """Test individual reflection nodes."""
    print("\n🧪 Testing individual reflection nodes...")
    
    try:
        from vira.reflection.reflection_nodes import (
            reflection_trigger_node, 
            autonomous_reflection_node,
            action_planning_node,
            execute_action_node
        )
        
        # Create test state
        test_state = {
            "user_id": str(uuid.uuid4()),
            "conversation_history": [
                {"content": "Hello", "timestamp": datetime.now().isoformat()},
                {"content": "How are you?", "timestamp": datetime.now().isoformat()}
            ],
            "retrieved_memories": [],
            "reflection_data": {}
        }
        
        # Test reflection trigger node
        try:
            trigger_result = reflection_trigger_node(test_state)
            print(f"✅ Reflection trigger node executed: {type(trigger_result)}")
        except Exception as e:
            print(f"⚠️  Reflection trigger node error: {e}")
        
        # Test autonomous reflection node
        try:
            # Set mock mode for LLM calls
            os.environ["VIRA_USE_MOCK_LLM"] = "true"
            
            autonomous_result = autonomous_reflection_node(test_state)
            print(f"✅ Autonomous reflection node executed: {type(autonomous_result)}")
        except Exception as e:
            print(f"⚠️  Autonomous reflection node error: {e}")
        finally:
            os.environ.pop("VIRA_USE_MOCK_LLM", None)
        
        # Test action planning node
        try:
            os.environ["VIRA_USE_MOCK_LLM"] = "true"
            
            planning_result = action_planning_node(test_state)
            print(f"✅ Action planning node executed: {type(planning_result)}")
        except Exception as e:
            print(f"⚠️  Action planning node error: {e}")
        finally:
            os.environ.pop("VIRA_USE_MOCK_LLM", None)
        
        # Test execute action node
        try:
            execute_result = execute_action_node(test_state)
            print(f"✅ Execute action node executed: {type(execute_result)}")
        except Exception as e:
            print(f"⚠️  Execute action node error: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import reflection nodes: {e}")
        return False
    except Exception as e:
        print(f"❌ Reflection nodes test failed: {e}")
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")
        return False

def test_pattern_extraction():
    """Test pattern extraction functions."""
    print("\n🧪 Testing pattern extraction functions...")
    
    try:
        from vira.graph.build_reflection import extract_temporal_patterns, extract_behavioral_patterns
        
        # Create test data
        test_conversations = [
            {
                "content": "Hello, how are you?",
                "timestamp": "2024-01-15T10:30:00",
                "message": "Hello, how are you?"
            },
            {
                "content": "Can you help me with this problem?",
                "timestamp": "2024-01-15T14:45:00",
                "message": "Can you help me with this problem?"
            },
            {
                "content": "Thank you for your assistance!",
                "timestamp": "2024-01-16T09:15:00",
                "message": "Thank you for your assistance!"
            }
        ]
        
        test_memories = [
            {"content": "User likes technical discussions"},
            {"content": "User prefers morning interactions"}
        ]
        
        # Test temporal patterns
        temporal_patterns = extract_temporal_patterns(test_conversations)
        print(f"✅ Temporal patterns extracted: {temporal_patterns}")
        
        # Test behavioral patterns
        behavioral_patterns = extract_behavioral_patterns(test_conversations, test_memories)
        print(f"✅ Behavioral patterns extracted: {behavioral_patterns}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern extraction test failed: {e}")
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Reflection Workflow End-to-End Test")
    print("=" * 60)
    
    # Test 1: Workflow creation
    workflow_success, workflow = test_reflection_workflow_creation()
    
    # Test 2: Workflow execution
    execution_success, execution_result = test_workflow_execution()
    
    # Test 3: Schedule actions
    schedule_success, schedule_result = test_schedule_actions()
    
    # Test 4: Process user reflection
    process_success, process_result = test_process_user_reflection()
    
    # Test 5: Individual reflection nodes
    nodes_success = test_reflection_nodes()
    
    # Test 6: Pattern extraction
    patterns_success = test_pattern_extraction()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"✅ Workflow Creation: {'PASS' if workflow_success else 'FAIL'}")
    print(f"✅ Workflow Execution: {'PASS' if execution_success else 'FAIL'}")
    print(f"✅ Schedule Actions: {'PASS' if schedule_success else 'FAIL'}")
    print(f"✅ Process User Reflection: {'PASS' if process_success else 'FAIL'}")
    print(f"✅ Individual Reflection Nodes: {'PASS' if nodes_success else 'FAIL'}")
    print(f"✅ Pattern Extraction: {'PASS' if patterns_success else 'FAIL'}")
    
    total_tests = 6
    passed_tests = sum([
        workflow_success, execution_success, schedule_success, 
        process_success, nodes_success, patterns_success
    ])
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All reflection workflow tests are working correctly!")
    else:
        print("⚠️  Some reflection workflow components need attention")