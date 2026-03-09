#!/usr/bin/env python3
"""
Example script demonstrating all AI service features.

Usage:
    export GEMINI_API_KEY="your_api_key_here"
    python example.py
"""

import asyncio
import os
import sys
from gemini_service import GeminiService


async def main():
    """Run complete example of all AI features."""
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("\nPlease set your API key:")
        print("  export GEMINI_API_KEY='your_api_key_here'")
        print("\nGet your API key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)
    
    print("=" * 70)
    print("SIDEKICK AI MEDICAL ASSISTANT - AI SERVICE DEMO")
    print("=" * 70)
    
    # Initialize service
    print("\n📋 Initializing Gemini AI service...")
    try:
        service = GeminiService(api_key=api_key)
        print("✅ Service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize service: {e}")
        sys.exit(1)
    
    # Sample medical conversation
    transcript = """
    Doctor: Good morning. I've reviewed your blood pressure readings. 
    Your BP is 140/90, which indicates hypertension. This means your blood 
    pressure is higher than normal. I'm going to prescribe Lisinopril 10mg 
    to help manage this. You should take it once daily in the morning with food.
    
    Patient: Okay, doctor. What should I watch out for?
    
    Doctor: Monitor your blood pressure at home daily. Common side effects 
    include dizziness and a dry cough. Also, reduce your sodium intake and 
    try to exercise regularly - at least 30 minutes a day, 5 days a week.
    
    Patient: How long until I see improvement?
    
    Doctor: You should see improvement in 2-4 weeks. Come back in 3 months 
    for a follow-up appointment so we can check your progress.
    
    Patient: Thank you, doctor.
    """
    
    print("\n📝 Sample Medical Conversation:")
    print("-" * 70)
    print(transcript.strip())
    print("-" * 70)
    
    # 1. Medical Term Simplification
    print("\n\n1️⃣  MEDICAL TERM SIMPLIFICATION")
    print("=" * 70)
    print("Identifying and explaining medical terms...")
    
    try:
        terms = await service.simplify_terms(transcript)
        
        if terms:
            print(f"\n✅ Found {len(terms)} medical terms:\n")
            for i, term in enumerate(terms, 1):
                print(f"   {i}. {term['term']}")
                print(f"      → {term['explanation']}\n")
        else:
            print("\n⚠️  No medical terms found")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    # 2. Question Suggestions
    print("\n2️⃣  QUESTION SUGGESTIONS")
    print("=" * 70)
    print("Generating helpful questions for the patient...")
    
    try:
        questions = await service.suggest_questions(transcript)
        
        if questions:
            print(f"\n✅ Generated {len(questions)} questions:\n")
            for i, question in enumerate(questions, 1):
                print(f"   {i}. {question}\n")
        else:
            print("\n⚠️  No questions generated (may need more context)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    # 3. Visit Summary
    print("\n3️⃣  VISIT SUMMARY")
    print("=" * 70)
    print("Creating structured summary of the visit...")
    
    try:
        summary = await service.generate_summary(transcript)
        
        print("\n✅ Summary generated:\n")
        print(f"   📌 Title: {summary['title']}")
        print(f"   🏥 Diagnosis: {summary['diagnosis']}")
        
        if summary['medications']:
            print(f"\n   💊 Medications:")
            for med in summary['medications']:
                print(f"      • {med}")
        
        if summary['instructions']:
            print(f"\n   📋 Instructions:")
            for inst in summary['instructions']:
                print(f"      • {inst}")
        
        if summary['follow_up']:
            print(f"\n   📅 Follow-up: {summary['follow_up']}")
        
        if summary['key_points']:
            print(f"\n   🔑 Key Points:")
            for point in summary['key_points']:
                print(f"      • {point}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    # 4. Translation
    print("\n\n4️⃣  TRANSLATION")
    print("=" * 70)
    print("Translating medical explanation to Spanish...")
    
    try:
        if terms:
            first_term = terms[0]
            translated = await service.translate_text(
                first_term['explanation'],
                "es"
            )
            
            print(f"\n✅ Translation:\n")
            print(f"   English: {first_term['explanation']}")
            print(f"   Spanish: {translated}")
        else:
            print("\n⚠️  No terms to translate")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    # 5. Performance Statistics
    print("\n\n5️⃣  PERFORMANCE STATISTICS")
    print("=" * 70)
    
    stats = service.get_performance_stats()
    print(f"\n📊 Service Performance:\n")
    print(f"   Total API Requests: {stats['total_requests']}")
    print(f"   Average Response Time: {stats['average_response_time']:.2f}s")
    print(f"   Slow Requests: {stats['slow_requests']}")
    print(f"   Slow Request %: {stats['slow_request_percentage']:.1f}%")
    
    # Summary
    print("\n\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\n✅ All AI features demonstrated successfully!")
    print("\n📚 Next Steps:")
    print("   1. Review the code in example.py")
    print("   2. Read docs/API.md for complete API reference")
    print("   3. Read docs/INTEGRATION.md to integrate with backend")
    print("   4. Run tests: pytest tests/")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
