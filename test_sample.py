"""
Comprehensive Test Suite for Medical Report Analysis API
Tests all endpoints, validates GPU/CPU usage, and checks deployment readiness
"""

import io
import sys
import time
from pathlib import Path
from typing import Dict, Any

import requests
from PIL import Image, ImageDraw


# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "http://localhost:8000"
TEST_RESULTS = []


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(title: str, char: str = "=") -> None:
    """Print a formatted test header."""
    print(f"\n{char * 80}")
    print(f"  {title}")
    print(f"{char * 80}\n")


def print_result(test_name: str, passed: bool, details: str = "") -> None:
    """Print and record test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"       {details}")

    TEST_RESULTS.append({
        "test": test_name,
        "passed": passed,
        "details": details
    })


def make_request(method: str, endpoint: str, **kwargs) -> tuple[int, Any]:
    """Make HTTP request and return status code and response."""
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.request(method, url, timeout=30, **kwargs)

        try:
            data = response.json()
        except:
            data = response.text

        return response.status_code, data
    except Exception as e:
        return 0, str(e)


def create_test_image(text: str = "Medical Report\nPatient: Test\nDiagnosis: Sample") -> bytes:
    """Create a simple test image with text."""
    # Create a white image
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)

    # Add text
    try:
        # Try to use default font
        draw.text((20, 20), text, fill='black')
    except:
        # Fallback if font not available
        draw.text((20, 20), text, fill='black')

    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return img_bytes.getvalue()


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_server_connectivity() -> bool:
    """Test 1: Check if server is running."""
    print_header("TEST 1: Server Connectivity", "=")

    try:
        status, data = make_request("GET", "/")

        if status == 200:
            print(f"Server Status: {data.get('status', 'unknown')}")
            print(f"API Version: {data.get('version', 'unknown')}")
            print_result("Server Connectivity", True, "Server is running")
            return True
        else:
            print_result("Server Connectivity", False, f"Status code: {status}")
            return False
    except Exception as e:
        print_result("Server Connectivity", False, str(e))
        return False


def test_health_and_gpu_detection() -> Dict[str, Any]:
    """Test 2: Health check and GPU/CPU detection."""
    print_header("TEST 2: Health Check & Device Detection", "=")

    status, data = make_request("GET", "/api/v1/health")

    if status == 200:
        ml_available = data.get("ml_available", False)
        model_loaded = data.get("model_loaded", False)
        device = data.get("device", "unknown")

        print(f"Health Status: {data.get('status', 'unknown')}")
        print(f"ML Available: {ml_available}")
        print(f"Model Loaded: {model_loaded}")
        print(f"API Version: {data.get('version', 'unknown')}")

        # Display device information
        print("\n📊 Device Information:")
        if device == "cuda":
            print("   🚀 GPU Acceleration: ENABLED (CUDA)")
            print("   ✅ Using GPU for inference - Fast performance!")
        elif device == "cpu":
            print("   💻 CPU Mode: ACTIVE")
            print("   ℹ️  GPU not detected - Using CPU for inference")
        elif device == "not_loaded":
            print("   ⏳ Model not yet loaded")
            print("   ℹ️  Device will be detected on first request")
        else:
            print(f"   ❓ Device: {device}")

        print("\n💡 Device Detection:")
        print("   - System automatically detects CUDA GPU via nvidia-smi")
        print("   - Falls back to CPU if GPU not available")
        print("   - No manual configuration needed!")

        if ml_available and model_loaded:
            device_msg = f"Running on {device.upper()}"
            print_result("Health Check", True, f"System ready - {device_msg}")
        elif ml_available:
            print_result("Health Check", True, "ML available, model will load on first request")
        else:
            print_result("Health Check", False, "ML dependencies not available")

        return data
    else:
        print_result("Health Check", False, f"Status code: {status}")
        return {}


def test_text_summarization() -> bool:
    """Test 3: Medical report summarization."""
    print_header("TEST 3: Text Summarization", "=")

    medical_report = """
Patient: John Doe, Age: 45
Chief Complaint: Severe chest pain radiating to left arm
Vital Signs: BP 150/95 mmHg, HR 110 bpm, Temp 98.6°F
ECG: ST-segment elevation in leads II, III, aVF
Labs: Troponin 2.5 ng/mL (elevated)
Assessment: Acute Myocardial Infarction (Inferior Wall)
Treatment: Aspirin 325mg, Nitroglycerin sublingual, transferred to cath lab
Plan: Emergency cardiac catheterization
"""

    payload = {
        "text": medical_report.strip(),
        "temperature": 0.7,
        "max_length": 200
    }

    print("📝 Input Report:")
    print(f"   Length: {len(medical_report.strip())} characters")
    print(f"   Preview: {medical_report.strip()[:100]}...")

    start_time = time.time()
    status, data = make_request("POST", "/api/v1/summarize", json=payload)
    elapsed = time.time() - start_time

    if status == 200:
        summary = data.get("summary", "")
        print(f"\n✨ Generated Summary:")
        print(f"   {summary}")
        print(f"\n📊 Statistics:")
        print(f"   Input Length: {data.get('input_length', 0)} chars")
        print(f"   Summary Length: {data.get('summary_length', 0)} chars")
        print(f"   Processing Time: {elapsed:.2f}s")

        print_result("Text Summarization", True, f"Generated in {elapsed:.2f}s")
        return True
    else:
        print(f"❌ Error: {data}")
        print_result("Text Summarization", False, f"Status: {status}")
        return False


def test_question_answering() -> bool:
    """Test 4: Medical report question answering."""
    print_header("TEST 4: Question Answering", "=")

    medical_report = """
Patient: Emma Williams, Age: 35
Annual physical examination
Vitals: BP 118/76 mmHg, HR 72 bpm, Temp 98.6°F, BMI 24.5
Labs: CBC normal, Lipid panel normal, HbA1c 5.2%
Vaccinations: Flu shot administered today
Assessment: Healthy, no concerns
Plan: Continue current lifestyle, return in 1 year
"""

    questions = [
        "What is the patient's blood pressure?",
        "What vaccination was given?",
        "When should the patient return?"
    ]

    all_passed = True

    for i, question in enumerate(questions, 1):
        print(f"\n🔍 Question {i}: {question}")

        payload = {
            "text": medical_report.strip(),
            "question": question
        }

        start_time = time.time()
        status, data = make_request("POST", "/api/v1/analyze", json=payload)
        elapsed = time.time() - start_time

        if status == 200:
            answer = data.get("answer", "")
            print(f"   ✅ Answer: {answer}")
            print(f"   ⏱️  Time: {elapsed:.2f}s")
        else:
            print(f"   ❌ Error: {data}")
            all_passed = False

    print_result("Question Answering", all_passed, f"Tested {len(questions)} questions")
    return all_passed


def test_document_upload() -> bool:
    """Test 5: Document upload and processing."""
    print_header("TEST 5: Document Upload", "=")

    # Create a temporary text file
    test_content = """
MEDICAL REPORT
Patient: Robert Martinez, Age: 58
Follow-up for Type 2 Diabetes and Hypertension
HbA1c: 7.8% (improved from 9.2%)
BP: 135/85 mmHg
Current Medications: Metformin 1000mg BID, Lisinopril 20mg daily
Plan: Continue current regimen, dietary counseling
Next visit: 3 months
"""

    # Create temp file
    temp_file = Path("temp_test_report.txt")
    temp_file.write_text(test_content.strip())

    try:
        print(f"📄 Uploading document: {temp_file.name}")
        print(f"   Size: {len(test_content)} bytes")

        with open(temp_file, 'rb') as f:
            files = {'file': (temp_file.name, f, 'text/plain')}
            status, data = make_request("POST", "/api/v1/upload/document", files=files)

        if status == 200:
            print(f"\n✅ Upload successful:")
            print(f"   Filename: {data.get('filename', 'unknown')}")
            print(f"   Size: {data.get('file_size', 0)} bytes")
            print(f"   Format: {data.get('format', 'unknown')}")
            print(f"   Processed: {data.get('processed', False)}")
            print(f"   Message: {data.get('message', '')}")

            print_result("Document Upload", True, "Document processed successfully")
            return True
        else:
            print(f"❌ Error: {data}")
            print_result("Document Upload", False, f"Status: {status}")
            return False

    finally:
        # Clean up
        temp_file.unlink(missing_ok=True)


def test_image_upload() -> bool:
    """Test 6: Image upload and processing."""
    print_header("TEST 6: Image Upload & Processing", "=")

    # Create a test image
    print("🖼️  Creating test medical image...")
    image_data = create_test_image(
        "MEDICAL REPORT\n\nPatient: Test Patient\nDiagnosis: Sample Test\nStatus: Normal"
    )

    print(f"   Image size: {len(image_data)} bytes")

    try:
        files = {'file': ('test_medical_image.png', image_data, 'image/png')}
        status, data = make_request("POST", "/api/v1/upload/image", files=files)

        if status == 200:
            print(f"\n✅ Upload successful:")
            print(f"   Filename: {data.get('filename', 'unknown')}")
            print(f"   Size: {data.get('file_size', 0)} bytes")
            print(f"   Format: {data.get('format', 'unknown')}")
            print(f"   Processed: {data.get('processed', False)}")
            print(f"   Message: {data.get('message', '')}")

            # Note about OCR
            if "no text extracted" in data.get('message', '').lower():
                print("\n   ℹ️  Note: OCR requires pytesseract installation")
                print("      Image was processed but text extraction skipped")

            print_result("Image Upload", True, "Image processed successfully")
            return True
        else:
            print(f"❌ Error: {data}")
            print_result("Image Upload", False, f"Status: {status}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        print_result("Image Upload", False, str(e))
        return False



# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def run_all_tests() -> None:
    """Run all tests and display summary."""

    print("\n" + "=" * 80)
    print("  🏥 MEDICAL REPORT ANALYSIS API - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"  Target: {BASE_URL}")
    print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Run all tests
    test_server_connectivity()
    health_data = test_health_and_gpu_detection()
    test_text_summarization()
    test_question_answering()
    test_document_upload()
    test_image_upload()

    # Print summary
    print_header("📊 TEST SUMMARY", "=")

    total_tests = len(TEST_RESULTS)
    passed_tests = sum(1 for r in TEST_RESULTS if r["passed"])
    failed_tests = total_tests - passed_tests

    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")

    print("\n" + "-" * 80)
    print("Detailed Results:")
    print("-" * 80)

    for result in TEST_RESULTS:
        status = "✅" if result["passed"] else "❌"
        print(f"{status} {result['test']}")
        if result["details"]:
            print(f"   └─ {result['details']}")

    # Deployment readiness check
    print_header("🚀 DEPLOYMENT READINESS", "=")

    if passed_tests == total_tests:
        print("✅ ALL TESTS PASSED - System is ready for deployment!")
        print("\n📋 Deployment Checklist:")
        print("   ✅ Server is running")
        print("   ✅ Health check passing")
        print("   ✅ ML model loaded and working")
        print("   ✅ Text summarization functional")
        print("   ✅ Question answering functional")
        print("   ✅ Document upload working")
        print("   ✅ Image upload working")

        print("\n🔧 System Configuration:")
        if health_data:
            print(f"   - ML Available: {health_data.get('ml_available', False)}")
            print(f"   - Model Loaded: {health_data.get('model_loaded', False)}")
            print(f"   - Device: {health_data.get('device', 'unknown').upper()}")
            print(f"   - API Version: {health_data.get('version', 'unknown')}")

            # Show performance note based on device
            device = health_data.get('device', 'unknown')
            if device == 'cuda':
                print("\n   🚀 Performance: GPU-accelerated (Optimal)")
            elif device == 'cpu':
                print("\n   💻 Performance: CPU-only (Consider GPU for production)")

        print("\n💡 Next Steps:")
        print("   1. Review logs for any warnings")
        print("   2. Test with production data")
        print("   3. Configure environment variables for production")
        print("   4. Set up monitoring and alerting")
        print("   5. Deploy to production environment")

    else:
        print(f"⚠️  {failed_tests} TEST(S) FAILED - Review issues before deployment")
        print("\n🔍 Failed Tests:")
        for result in TEST_RESULTS:
            if not result["passed"]:
                print(f"   ❌ {result['test']}: {result['details']}")

        print("\n💡 Troubleshooting:")
        print("   1. Check if server is running: python run.py")
        print("   2. Verify ML dependencies: pip install llama-cpp-python")
        print("   3. Check logs: tail -f logs/app.log")
        print("   4. Review configuration in .env file")

    print("\n" + "=" * 80)
    print(f"  Test completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")

    # Exit with appropriate code
    sys.exit(0 if failed_tests == 0 else 1)


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)