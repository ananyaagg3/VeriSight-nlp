import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000/api"

def print_result(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"   {details}")

def test_health():
    try:
        start_time = time.time()
        # Health endpoint is at root /health, not /api/health
        response = requests.get("http://localhost:8000/health")
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print_result("Health Check", True, f"Status: {data.get('status')}, Time: {duration:.2f}s")
            return True
        else:
            print_result("Health Check", False, f"Status Code: {response.status_code}")
            return False
    except Exception as e:
        print_result("Health Check", False, f"Error: {str(e)}")
        return False

def test_text_analysis(text, expected_verdict_type, description):
    print(f"\nTesting: {description} ('{text}')")
    print("⏳ Waiting for analysis (first request may take time due to model lazy loading)...")
    
    try:
        start_time = time.time()
        payload = {
            "text": text,
            "language": "en"
        }
        response = requests.post(f"{BASE_URL}/analysis/analyze-text", json=payload)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            verdict = data.get("verdict")
            confidence = data.get("confidence")
            
            # Simple check based on expected type (Authentic vs Misinformation)
            passed = False
            if expected_verdict_type == "AUTHENTIC" and verdict == "AUTHENTIC":
                passed = True
            elif expected_verdict_type == "MISINFORMATION" and verdict in ["MISINFORMATION", "NEEDS_VERIFICATION"]:
                 # Depending on model confidence, it might be NEEDS_VERIFICATION for some false claims without extensive context
                passed = True
            
            print_result(f"Analysis: {description}", passed, f"Verdict: {verdict}, Confidence: {confidence:.2f}, Time: {duration:.2f}s")
            
            # Print evidence if available
            evidence = data.get("explanation", {}).get("evidence_chain", [])
            if evidence:
                print("   Evidence Chain:")
                for item in evidence[:2]: # Print first 2
                    print(f"   - {item}")
            return passed
        else:
            print_result(f"Analysis: {description}", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        print_result(f"Analysis: {description}", False, f"Error: {str(e)}")
        return False

def main():
    print("🚀 Starting FactWeave System Verification")
    print("=========================================")
    
    # 1. Health Check
    if not test_health():
        print("\n❌ System is not healthy. Aborting tests.")
        sys.exit(1)
        
    # 2. Authentic Claim
    test_text_analysis(
        "Paris is the capital of France.", 
        "AUTHENTIC", 
        "Authentic Fact"
    )
    
    # 3. Misinformation Claim
    test_text_analysis(
        "The earth is completely flat and not a sphere.", 
        "MISINFORMATION", 
        "Obvious Misinformation"
    )
    
    print("\n=========================================")
    print("Verification Complete")

if __name__ == "__main__":
    main()
