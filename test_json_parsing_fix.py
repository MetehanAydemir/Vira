#!/usr/bin/env python3
"""
Test script to debug and fix JSON parsing issues in the emotional state analysis.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'vira'))

import json
import logging
from vira.utils.llm_client import call_chat_model

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_json_response():
    """Test if LLM returns valid JSON when requested."""
    print("🧪 Testing JSON response from LLM...")
    
    messages = [
        {
            "role": "system",
            "content": """Sen bir duygusal analiz uzmanısın. Verilen metinlerdeki duygusal durumu analiz et.

Yanıtını JSON formatında ver:
{
    "primary": "positive/negative/neutral/excited/anxious/frustrated/happy/sad/angry/curious",
    "intensity": 0.0-1.0 arası sayı (0=çok hafif, 1=çok yoğun)
}"""
        },
        {
            "role": "user",
            "content": "Bu konuşmalardaki duygusal durumu analiz et:\n\nMerhaba, bugün nasılsın? İyi misin?"
        }
    ]
    
    try:
        # Test with JSON format request
        response = call_chat_model(
            messages,
            temperature=0.3,
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        
        print(f"Raw LLM Response: '{response}'")
        print(f"Response type: {type(response)}")
        print(f"Response length: {len(response)}")
        
        # Try to parse as JSON
        try:
            parsed = json.loads(response)
            print(f"✅ Successfully parsed JSON: {parsed}")
            return True, parsed
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Response content: {repr(response)}")
            
            # Try to extract JSON from response if it's embedded in text
            cleaned_response = extract_json_from_text(response)
            if cleaned_response:
                try:
                    parsed = json.loads(cleaned_response)
                    print(f"✅ Successfully parsed cleaned JSON: {parsed}")
                    return True, parsed
                except json.JSONDecodeError:
                    print(f"❌ Even cleaned response is not valid JSON")
            
            return False, None
            
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        return False, None

def extract_json_from_text(text):
    """Extract JSON object from text that might contain other content."""
    import re
    
    # Try to find JSON object in the text
    json_pattern = r'\{[^{}]*\}'
    matches = re.findall(json_pattern, text)
    
    if matches:
        # Return the first match that looks like JSON
        for match in matches:
            try:
                json.loads(match)  # Test if it's valid JSON
                return match
            except:
                continue
    
    # Try to find content between curly braces (more flexible)
    start = text.find('{')
    end = text.rfind('}')
    
    if start != -1 and end != -1 and end > start:
        potential_json = text[start:end+1]
        try:
            json.loads(potential_json)
            return potential_json
        except:
            pass
    
    return None

def test_fallback_parsing():
    """Test fallback parsing mechanism."""
    print("\n🧪 Testing fallback parsing mechanism...")
    
    # Simulate various problematic responses
    test_responses = [
        '{"primary": "neutral", "intensity": 0.5}',  # Valid JSON
        'The emotional state is {"primary": "happy", "intensity": 0.8}',  # JSON embedded in text
        'primary: neutral, intensity: 0.5',  # Key-value pairs without quotes
        'Emotional state: positive with intensity 0.7',  # Natural language
        '',  # Empty response
        'Error: Unable to analyze',  # Error message
    ]
    
    for i, response in enumerate(test_responses):
        print(f"\nTest {i+1}: '{response}'")
        result = parse_emotional_state_with_fallback(response)
        print(f"Result: {result}")

def parse_emotional_state_with_fallback(response):
    """
    Robust parsing function for emotional state with multiple fallback strategies.
    """
    if not response or not response.strip():
        return {"primary": "neutral", "intensity": 0.5}
    
    # Strategy 1: Try direct JSON parsing
    try:
        result = json.loads(response)
        if "primary" in result and "intensity" in result:
            return {
                "primary": result["primary"],
                "intensity": max(0.0, min(1.0, float(result["intensity"])))
            }
    except (json.JSONDecodeError, ValueError, TypeError):
        pass
    
    # Strategy 2: Extract JSON from text
    extracted_json = extract_json_from_text(response)
    if extracted_json:
        try:
            result = json.loads(extracted_json)
            if "primary" in result and "intensity" in result:
                return {
                    "primary": result["primary"],
                    "intensity": max(0.0, min(1.0, float(result["intensity"])))
                }
        except (json.JSONDecodeError, ValueError, TypeError):
            pass
    
    # Strategy 3: Pattern matching for key-value pairs
    import re
    
    # Look for primary emotion
    primary_match = re.search(r'primary["\']?\s*:\s*["\']?(\w+)["\']?', response, re.IGNORECASE)
    primary = primary_match.group(1) if primary_match else "neutral"
    
    # Look for intensity
    intensity_match = re.search(r'intensity["\']?\s*:\s*["\']?([0-9.]+)["\']?', response, re.IGNORECASE)
    intensity = float(intensity_match.group(1)) if intensity_match else 0.5
    
    if primary_match or intensity_match:
        return {
            "primary": primary.lower(),
            "intensity": max(0.0, min(1.0, intensity))
        }
    
    # Strategy 4: Natural language parsing
    emotion_keywords = {
        "happy": ["happy", "joy", "pleased", "content", "cheerful"],
        "sad": ["sad", "depressed", "down", "melancholy"],
        "angry": ["angry", "mad", "furious", "irritated"],
        "excited": ["excited", "enthusiastic", "thrilled"],
        "anxious": ["anxious", "worried", "nervous", "concerned"],
        "frustrated": ["frustrated", "annoyed", "bothered"],
        "curious": ["curious", "interested", "wondering"],
        "positive": ["positive", "good", "great", "excellent"],
        "negative": ["negative", "bad", "poor", "terrible"]
    }
    
    response_lower = response.lower()
    for emotion, keywords in emotion_keywords.items():
        if any(keyword in response_lower for keyword in keywords):
            # Try to extract intensity from numbers in the text
            numbers = re.findall(r'[0-9.]+', response)
            intensity = 0.5
            if numbers:
                try:
                    intensity = max(0.0, min(1.0, float(numbers[0])))
                except:
                    pass
            
            return {"primary": emotion, "intensity": intensity}
    
    # Strategy 5: Default fallback
    return {"primary": "neutral", "intensity": 0.5}

if __name__ == "__main__":
    print("🚀 JSON Parsing Fix Test")
    print("=" * 50)
    
    # Test 1: Direct JSON response
    success, result = test_json_response()
    
    # Test 2: Fallback parsing
    test_fallback_parsing()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ JSON parsing is working correctly")
    else:
        print("⚠️  JSON parsing needs fallback mechanism")
        print("💡 Recommendation: Implement robust fallback parsing in MetaCognitive Engine")