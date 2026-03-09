#!/usr/bin/env python3
"""
Simple script to test if Gemini API key is working
Run this before starting the backend server
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
    print("\nPlease create a .env file with your API key:")
    print("GEMINI_API_KEY=your_actual_api_key_here")
    print("\nGet your API key from: https://makersuite.google.com/app/apikey")
    sys.exit(1)

print(f"✓ Found GEMINI_API_KEY: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")
print("\nTesting Gemini API connection...")

try:
    import google.generativeai as genai
    
    # Configure the API
    genai.configure(api_key=GEMINI_API_KEY)
    
    # List available models
    print("\nFetching available models...")
    models = genai.list_models()
    
    available_models = []
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            available_models.append(model.name)
            print(f"  ✓ {model.name}")
    
    if not available_models:
        print("\n❌ No models available for content generation")
        sys.exit(1)
    
    # Use the first available model
    model_name = available_models[0].replace('models/', '')
    print(f"\nUsing model: {model_name}")
    
    model = genai.GenerativeModel(model_name)
    
    # Test with a simple prompt
    print("\nSending test request to Gemini API...")
    response = model.generate_content("Say 'Hello, I am working!' in exactly 5 words.")
    
    print("\n✅ SUCCESS! Gemini API is working!")
    print(f"\nResponse from Gemini: {response.text}")
    print("\n" + "="*60)
    print("Your Gemini API key is valid and working correctly!")
    print(f"Available model: {model_name}")
    print("You can now start the backend server.")
    print("="*60)
    
except ImportError:
    print("\n❌ ERROR: google-generativeai package not installed")
    print("\nInstall it with:")
    print("pip install google-generativeai")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ ERROR: Failed to connect to Gemini API")
    print(f"\nError details: {str(e)}")
    print("\nPossible issues:")
    print("1. Invalid API key - Get a new one from https://makersuite.google.com/app/apikey")
    print("2. API key doesn't have proper permissions")
    print("3. Network connectivity issues")
    print("4. Rate limit exceeded (wait a minute and try again)")
    sys.exit(1)
