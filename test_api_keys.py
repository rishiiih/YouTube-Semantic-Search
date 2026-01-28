"""
Test API keys to verify they work
Run: python test_api_keys.py
"""
import sys
from pathlib import Path
import requests

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.app.config import settings


def test_groq_api():
    """Test Groq API key"""
    print("✓ Testing Groq API key...")
    
    if not settings.groq_api_key:
        print("  ✗ GROQ_API_KEY not set in .env")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": settings.llm_model,
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"]
            print(f"  ✓ Groq API working! Response: {result[:50]}")
            return True
        elif response.status_code == 401:
            print(f"  ✗ Invalid Groq API key (401 Unauthorized)")
            return False
        else:
            print(f"  ✗ Groq API error: {response.status_code} - {response.text[:100]}")
            return False
        
    except Exception as e:
        print(f"  ✗ Groq API failed: {e}")
        return False


def test_openai_api():
    """Test OpenAI API key"""
    print("\n✓ Testing OpenAI API key...")
    
    if not settings.openai_api_key:
        print("  ✗ OPENAI_API_KEY not set in .env")
        return False
    
    if settings.openai_api_key == "your_openai_api_key_here":
        print("  ✗ OPENAI_API_KEY still has default value. Please update .env")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        # Test with models endpoint (lightweight)
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            models = response.json()["data"]
            model_ids = [m["id"] for m in models]
            
            print(f"  ✓ OpenAI API working! Found {len(model_ids)} models")
            
            # Check for Whisper
            whisper_available = any('whisper' in m for m in model_ids)
            print(f"  - Whisper API available: {whisper_available}")
            
            return True
        elif response.status_code == 401:
            print(f"  ✗ Invalid OpenAI API key (401 Unauthorized)")
            return False
        else:
            print(f"  ✗ OpenAI API error: {response.status_code} - {response.text[:100]}")
            return False
        
    except Exception as e:
        print(f"  ✗ OpenAI API failed: {e}")
        return False


def main():
    print("=" * 60)
    print("API Key Validation")
    print("=" * 60)
    
    groq_ok = test_groq_api()
    openai_ok = test_openai_api()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"Groq API............ {'✓ PASS' if groq_ok else '✗ FAIL'}")
    print(f"OpenAI API.......... {'✓ PASS' if openai_ok else '✗ FAIL'}")
    print("=" * 60)
    
    if groq_ok and openai_ok:
        print("\n🎉 All API keys valid! Ready to proceed.")
    else:
        print("\n⚠ Fix API key issues before proceeding.")
        if not openai_ok:
            print("\nTo fix OpenAI key:")
            print("1. Get key from: https://platform.openai.com/api-keys")
            print("2. Update OPENAI_API_KEY in .env file")
    
    return groq_ok and openai_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
