import requests
from io import BytesIO

# Sample OpenAPI spec content
sample_openapi_spec = '''
openapi: 3.0.0
info:
  title: Pet Store API
  version: 1.0.0
  description: A sample API for pet store operations
servers:
  - url: https://api.petstore.com/v1
paths:
  /pets:
    get:
      summary: List all pets
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            maximum: 100
      responses:
        '200':
          description: A list of pets
    post:
      summary: Create a pet
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Pet'
      responses:
        '201':
          description: Pet created
  /pets/{petId}:
    get:
      summary: Get a pet by ID
      parameters:
        - name: petId
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Pet details
        '404':
          description: Pet not found
components:
  schemas:
    Pet:
      type: object
      required:
        - name
        - status
      properties:
        id:
          type: integer
        name:
          type: string
        status:
          type: string
          enum: [available, pending, sold]
'''

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:5000/health')
        print("=== HEALTH CHECK ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_generate_endpoint():
    """Test the test case generation endpoint"""
    try:
        # Convert string to bytes and create a file-like object
        file_like = BytesIO(sample_openapi_spec.encode('utf-8'))
        
        files = {'file': ('petstore.yaml', file_like, 'application/x-yaml')}
        
        response = requests.post('http://localhost:5000/generate', files=files)
        
        print("=== GENERATE TEST CASES ===")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success', False)}")
            print(f"API Title: {data.get('api_title', 'N/A')}")
            print(f"Endpoints Count: {data.get('endpoints_count', 0)}")
            print(f"Generated Filename: {data.get('filename', 'N/A')}")
            print("\n=== GENERATED TEST CASES (First 500 chars) ===")
            test_cases = data.get('test_cases', '')
            print(test_cases[:500] + "..." if len(test_cases) > 500 else test_cases)
        else:
            print(f"Error Response: {response.json()}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Generate endpoint test failed: {e}")
        return False

def test_home_page():
    """Test the home page"""
    try:
        response = requests.get('http://localhost:5000/')
        print("=== HOME PAGE ===")
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text)} characters")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Home page test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing AI Test Case Generator API...")
    print("Make sure your Flask app is running on http://localhost:5000\n")
    
    # Run all tests
    tests = [
        ("Home Page", test_home_page),
        ("Health Check", test_health_endpoint),
        ("Generate Test Cases", test_generate_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
        print("-" * 50)
    
    # Summary
    print("\n=== TEST SUMMARY ===")
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
