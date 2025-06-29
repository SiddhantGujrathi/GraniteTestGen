from dotenv import load_dotenv
load_dotenv()
import requests
import json
import os

api_key = os.environ.get("IBM_API_KEY")
project_id = os.environ.get("IBM_PROJECT_ID")
base_url = "https://us-south.ml.cloud.ibm.com"

# Check for required environment variables
if not api_key or not project_id:
    print("❌ ERROR: IBM_API_KEY or IBM_PROJECT_ID is not set.")
    exit(1)

def test_1_api_key_validity():
    """Test if API key can generate IAM token"""
    print("=== TEST 1: API Key Validity ===")
    try:
        url = "https://iam.cloud.ibm.com/identity/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key
        }
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ API Key is VALID")
            print(f"Token expires in: {token_data.get('expires_in', 'Unknown')} seconds")
            return token_data["access_token"]
        else:
            print(f"❌ API Key INVALID: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing API key: {e}")
        return None

def test_2_project_access(token):
    """Test if project ID is accessible"""
    print("\n=== TEST 2: Project Access ===")
    try:
        url = f"https://api.dataplatform.cloud.ibm.com/v2/projects/{project_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            project_data = response.json()
            print("✅ Project ID is ACCESSIBLE")
            print(f"Project Name: {project_data.get('entity', {}).get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Project access failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error accessing project: {e}")
        return False

def test_3_available_models(token):
    """Test what models are available"""
    print("\n=== TEST 3: Available Models ===")
    try:
        url = f"{base_url}/ml/v1/foundation_model_specs?version=2023-05-29"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            models_data = response.json()
            print("✅ Successfully retrieved model list")
            
            # Look for Granite models
            granite_models = []
            for model in models_data.get('resources', []):
                model_id = model.get('model_id', '')
                if 'granite' in model_id.lower():
                    granite_models.append(model_id)
            
            if granite_models:
                print("Available Granite models:")
                for model in granite_models:
                    print(f"  - {model}")
                return granite_models
            else:
                print("❌ No Granite models found")
                return []
        else:
            print(f"❌ Failed to get models: {response.status_code}")
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting models: {e}")
        return []

def test_4_granite_model_access(token, model_id="ibm/granite-8b-code-instruct"):
    """Test specific Granite model access"""
    print(f"\n=== TEST 4: Granite Model Access ({model_id}) ===")
    try:
        url = f"{base_url}/ml/v1/text/generation?version=2023-05-29"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": "Hello, respond with 'OK' if you can process this request.",
            "parameters": {
                "max_new_tokens": 10,
                "temperature": 0.1
            },
            "model_id": model_id,
            "project_id": project_id
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result["results"][0]["generated_text"]
            print("✅ Granite model is WORKING")
            print(f"Model response: {generated_text}")
            return True
        else:
            print(f"❌ Granite model access failed: {response.status_code}")
            print(f"Error: {response.text}")
            
            # Try to parse error for more details
            try:
                error_data = response.json()
                if "errors" in error_data:
                    for error in error_data["errors"]:
                        print(f"Error detail: {error.get('message', 'Unknown error')}")
            except:
                pass
            return False
    except Exception as e:
        print(f"❌ Error testing Granite model: {e}")
        return False

def test_5_alternative_models(token, available_models):
    """Test alternative Granite models if main one fails"""
    print("\n=== TEST 5: Alternative Granite Models ===")
    
    # Common Granite model variations to try
    models_to_try = [
        "ibm/granite-8b-code-instruct",
        "ibm/granite-20b-code-instruct",
    ]
    
    # Add any models we found in the available list
    for model in available_models:
        if model not in models_to_try:
            models_to_try.append(model)
    
    for model_id in models_to_try:
        print(f"\nTrying model: {model_id}")
        if test_4_granite_model_access(token, model_id):
            print(f"✅ SUCCESS! Use this model: {model_id}")
            return model_id
    
    print("❌ No working Granite models found")
    return None

def main():
    print("🔍 Testing IBM Granite API Connection...")
    print(f"API Key: {api_key[:10]}...")
    print(f"Project ID: {project_id}")
    print(f"Base URL: {base_url}")
    print("=" * 50)
    
    # Test 1: API Key
    token = test_1_api_key_validity()
    if not token:
        print("\n❌ CRITICAL: API Key is invalid. Cannot proceed.")
        return
    
    # Test 2: Project Access
    project_ok = test_2_project_access(token)
    if not project_ok:
        print("\n⚠️  WARNING: Project access issues detected")
    
    # Test 3: Available Models
    available_models = test_3_available_models(token)
    
    # Test 4: Main Granite Model
    main_model_works = test_4_granite_model_access(token)
    
    # Test 5: Alternative Models (if main fails)
    working_model = None
    if not main_model_works:
        working_model = test_5_alternative_models(token, available_models)
    
    # Final Summary
    print("\n" + "=" * 50)
    print("🎯 FINAL SUMMARY:")
    print("=" * 50)
    
    if token:
        print("✅ API Key: WORKING")
    else:
        print("❌ API Key: FAILED")
    
    if project_ok:
        print("✅ Project Access: WORKING")
    else:
        print("❌ Project Access: FAILED")
    
    if main_model_works:
        print("✅ Granite Model: WORKING")
        print("🚀 You can proceed with your AI Test Generator!")
    elif working_model:
        print(f"✅ Alternative Model Found: {working_model}")
        print(f"💡 Update your .env file to use: GRANITE_MODEL={working_model}")
    else:
        print("❌ Granite Models: ALL FAILED")
        print("📞 Contact IBM Support for model access")

if __name__ == "__main__":
    main()
