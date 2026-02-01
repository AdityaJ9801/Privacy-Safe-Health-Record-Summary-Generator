"""Test streaming endpoints for Medical Report Analysis API."""

import requests
import sys
import time

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

# Test data
MEDICAL_REPORT = """
Patient: John Doe
Age: 45 years
Date: 2024-01-15

Chief Complaint: Persistent cough and fever for 5 days

History of Present Illness:
Patient presents with a 5-day history of productive cough with yellow sputum.
Associated symptoms include fever (max temp 101.5°F), chills, and mild shortness of breath.
No chest pain or hemoptysis reported.

Physical Examination:
- Temperature: 100.8°F
- Heart Rate: 92 bpm
- Respiratory Rate: 20/min
- Blood Pressure: 128/82 mmHg
- Lung auscultation: Decreased breath sounds in right lower lobe with crackles

Assessment:
Community-acquired pneumonia, right lower lobe

Plan:
1. Chest X-ray ordered
2. Started on Azithromycin 500mg daily for 5 days
3. Supportive care with rest and hydration
4. Follow-up in 3 days or sooner if symptoms worsen
"""

QUESTION = "What medication was prescribed and what is the dosage?"


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def test_streaming_summarization():
    """Test streaming summarization endpoint."""
    print_header("TEST 1: Streaming Summarization")
    
    url = f"{BASE_URL}/summarize/stream"
    payload = {
        "text": MEDICAL_REPORT,
        "temperature": 0.7
    }
    
    print("📤 Sending request to:", url)
    print("⏳ Streaming response:\n")
    print("-" * 80)
    
    try:
        # Make streaming request
        response = requests.post(url, json=payload, stream=True, timeout=60)
        
        if response.status_code == 200:
            print("✅ Connected! Receiving tokens...\n")
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        token = decoded_line[6:]  # Remove 'data: ' prefix
                        
                        if token == "[DONE]":
                            print("\n\n✅ Stream completed!")
                            break
                        elif token.startswith("[ERROR"):
                            print(f"\n\n❌ Error: {token}")
                            break
                        else:
                            # Print token without newline for streaming effect
                            print(token, end='', flush=True)
                            time.sleep(0.01)  # Small delay for visual effect
            
            print("\n" + "-" * 80)
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_streaming_question_answering():
    """Test streaming question answering endpoint."""
    print_header("TEST 2: Streaming Question Answering")
    
    url = f"{BASE_URL}/analyze/stream"
    payload = {
        "text": MEDICAL_REPORT,
        "question": QUESTION
    }
    
    print("📤 Sending request to:", url)
    print(f"❓ Question: {QUESTION}")
    print("⏳ Streaming answer:\n")
    print("-" * 80)
    
    try:
        # Make streaming request
        response = requests.post(url, json=payload, stream=True, timeout=60)
        
        if response.status_code == 200:
            print("✅ Connected! Receiving tokens...\n")
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        token = decoded_line[6:]  # Remove 'data: ' prefix
                        
                        if token == "[DONE]":
                            print("\n\n✅ Stream completed!")
                            break
                        elif token.startswith("[ERROR"):
                            print(f"\n\n❌ Error: {token}")
                            break
                        else:
                            # Print token without newline for streaming effect
                            print(token, end='', flush=True)
                            time.sleep(0.01)  # Small delay for visual effect
            
            print("\n" + "-" * 80)
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    """Run all streaming tests."""
    print("\n" + "=" * 80)
    print("  🧪 MEDICAL REPORT API - STREAMING TESTS")
    print("=" * 80)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("\n❌ Server is not responding. Please start the API server:")
            print("   python run.py")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("\n❌ Cannot connect to server. Please start the API server:")
        print("   python run.py")
        sys.exit(1)
    
    print("\n✅ Server is running!")
    
    # Run tests
    results = []
    results.append(("Streaming Summarization", test_streaming_summarization()))
    results.append(("Streaming Question Answering", test_streaming_question_answering()))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

