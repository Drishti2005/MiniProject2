#!/usr/bin/env python3
"""
Check available Gemini models for your API key.
"""

import os
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        exit(1)
    
    print("🔍 Checking available Gemini models...\n")
    
    genai.configure(api_key=api_key)
    
    print("Available models:")
    print("-" * 60)
    
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✓ {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description[:100]}...")
            print()
    
    print("-" * 60)
    print("\n💡 Update ai_service/config.py with one of the model names above")
    print("   Example: GEMINI_MODEL = 'models/gemini-1.5-pro'")
    
except ImportError:
    print("❌ google-generativeai package not installed")
    print("   Run: pip install google-generativeai")
except Exception as e:
    print(f"❌ Error: {e}")
