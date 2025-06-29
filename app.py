from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import traceback
import uuid
from werkzeug.utils import secure_filename
from granite_client import GraniteClient
from spec_parser import SpecParser
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to save uploaded files
app.config['GENERATED_TESTS_FOLDER'] = 'generated_tests'  # Folder to save generated test files

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_TESTS_FOLDER'], exist_ok=True)

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'json', 'yaml', 'yml'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_test_generation_prompt(api_info):
    """
    Create a prompt for the AI model using API information.
    This prompt tells the model to generate JUnit 5 test cases for the given API.
    """
    endpoints_summary = ""
    for endpoint in api_info['endpoints']:
        params = ", ".join([p.get('name', '') for p in endpoint.get('parameters', [])])
        responses = ", ".join(endpoint.get('responses', {}).keys())
        endpoints_summary += f"""
- {endpoint['method']} {endpoint['path']}
  Summary: {endpoint.get('summary', 'N/A')}
  Parameters: {params if params else 'None'}
  Responses: {responses if responses else 'N/A'}"""
    
    schemas_summary = ""
    for name, schema in api_info.get('schemas', {}).items():
        properties = schema.get('properties', {})
        prop_list = ", ".join([f"{k}: {v.get('type', 'unknown')}" for k, v in properties.items()])
        schemas_summary += f"- {name}: {prop_list}\n"
    
    # The prompt sent to the AI model
    prompt = f"""You are an expert QA engineer specializing in API testing. Generate comprehensive JUnit 5 test cases for this REST API.

API Information:
- Title: {api_info['title']}
- Version: {api_info['version']}
- Description: {api_info['description']}
- Base URL: {api_info['base_url']}

Endpoints:{endpoints_summary}

Data Models:
{schemas_summary if schemas_summary else 'No schemas defined'}

Requirements:
1. Generate complete JUnit 5 test classes with proper annotations
2. Include positive test cases for valid inputs
3. Include negative test cases for invalid data and error conditions
4. Add boundary value testing for numeric fields
5. Test edge cases (empty strings, null values, special characters)
6. Generate realistic test data matching API schemas
7. Use proper assertions for status codes, headers, and response body
8. Use RestTemplate or TestRestTemplate for API calls
9. Include setup and teardown methods
10. Follow Spring Boot testing best practices

Generate complete, runnable Java test classes:

package com.example.api.test;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.reactive.server.WebTestClient;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class {api_info['title'].replace(' ', '')}ApiTest {{

text

Generate the complete test implementation now:"""
    return prompt

# Initialize the GraniteClient (reads credentials from .env)
granite_client = GraniteClient()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_tests():
    """
    Handle file upload, parse the API spec, generate test cases using the AI model,
    save the generated test file, and return the result to the frontend.
    """
    try:
        # Check if a file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload JSON, YAML, or YML files.'}), 400
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Read the file content
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Parse the API spec
        file_extension = filename.rsplit('.', 1)[1].lower()
        api_info = SpecParser.parse_openapi_spec(file_content, file_extension)
        
        # Create the prompt and generate test cases
        prompt = create_test_generation_prompt(api_info)
        generated_tests = granite_client.generate_test_cases(prompt)
        
        # If generation failed, return error
        if not generated_tests or not generated_tests.strip():
            return jsonify({'error': 'Test generation failed or returned empty result.'}), 500
        
        # Save the generated test cases to a file
        test_filename = f"{api_info['title'].replace(' ', '_')}_Tests.java"
        test_filepath = os.path.join(app.config['GENERATED_TESTS_FOLDER'], test_filename)
        with open(test_filepath, 'w', encoding='utf-8') as f:
            f.write(generated_tests)

        # Remove the uploaded file after processing
        os.remove(filepath)
        
        # Debug: print files in the generated_tests folder
        print("Files in generated_tests:", os.listdir(app.config['GENERATED_TESTS_FOLDER']))
        print("Expected filename:", test_filename)
        
        # Return the result to the frontend
        return jsonify({
            'success': True,
            'test_cases': generated_tests,
            'filename': test_filename,
            'api_title': api_info['title'],
            'endpoints_count': len(api_info['endpoints'])
        })
    
    except Exception as e:
        # Return error details if something goes wrong
        return jsonify({
            'error': f'Failed to generate tests: {str(e)}',
            'details': traceback.format_exc()
        }), 500

@app.route('/download/<filename>')
def download_tests(filename):
    """
    Allow the user to download the generated Java test file.
    """
    try:
        abs_generated_tests = os.path.abspath(app.config['GENERATED_TESTS_FOLDER'])
        print("Download requested for:", filename)
        print("Serving from:", abs_generated_tests)
        print("Full file path:", os.path.join(abs_generated_tests, filename))
        return send_from_directory(abs_generated_tests, filename, as_attachment=True)
    except Exception as e:
        print("Download error:", str(e))
        return jsonify({'error': f'File not found: {str(e)}'}), 404

@app.route('/health')
def health_check():
    """
    Simple health check endpoint to verify the app and Granite model are working.
    """
    try:
        test_prompt = "Hello, respond with 'OK' if you can process this request."
        response = granite_client.generate_test_cases(test_prompt)
        return jsonify({
            'status': 'healthy',
            'granite_model': granite_client.model_id,
            'project_id': granite_client.project_id,
            'test_response': response.strip()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/regenerate', methods=['POST'])
def regenerate_tests():
    try:
        data = request.get_json()
        filename = data.get('filename')
        suggestions = data.get('suggestions', '').strip()
        api_spec = data.get('api_spec', '')
        api_spec_type = data.get('api_spec_type', '')
        previous_code = data.get('previous_code', '')

        if not filename or not suggestions or not api_spec or not previous_code:
            return jsonify({'error': 'Missing required data for regeneration'}), 400

        # Parse the API spec again
        api_info = SpecParser.parse_openapi_spec(api_spec, api_spec_type)

        # Build a new prompt
        prompt = create_test_generation_prompt(api_info)
        prompt += f"\n\nUser Feedback: {suggestions}\n\nPrevious Generated Code:\n```java\n{previous_code}\n```\nPlease update the test cases accordingly."

        improved_tests = granite_client.generate_test_cases(prompt)
        if not improved_tests or not improved_tests.strip():
            return jsonify({'error': 'Test regeneration failed or returned empty result.'}), 500

        # Overwrite the generated test file
        test_path = os.path.join(app.config['GENERATED_TESTS_FOLDER'], filename)
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(improved_tests)

        return jsonify({
            'success': True,
            'test_cases': improved_tests,
            'filename': filename,
            'api_title': api_info['title'],
            'endpoints_count': len(api_info['endpoints'])
        })
    except Exception as e:
        print("Regenerate error:", str(e))
        return jsonify({
            'error': f'Failed to regenerate tests: {str(e)}',
            'details': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

# Example fetch call for regenerate
fetch('/regenerate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        filename: currentFilename, # must be set after generation
        suggestions: feedbackInput.value.trim() # or whatever your textarea id is
    })
})