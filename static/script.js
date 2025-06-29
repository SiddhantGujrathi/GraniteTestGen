document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const generateBtn = document.getElementById('generateBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('resultsSection');
    const errorSection = document.getElementById('errorSection');
    const testOutput = document.getElementById('testOutput');
    const apiInfo = document.getElementById('apiInfo');
    const downloadBtn = document.getElementById('downloadBtn');
    const feedbackInput = document.getElementById('feedbackInput');
    const regenerateBtn = document.getElementById('regenerateBtn');
    
    let currentFilename = '';
    
    // After successful generation, store the API spec and generated code
    let lastApiSpec = '';
    let lastApiSpecType = '';
    let lastGeneratedCode = '';

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        
        if (!file) {
            showError('Please select a file');
            return;
        }
        
        generateBtn.disabled = true;
        loadingSpinner.classList.remove('d-none');
        hideResults();
        hideError();
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                showResults(data);
            } else {
                showError(data.error || 'Failed to generate test cases');
            }
        } catch (error) {
            showError('Network error: ' + error.message);
        } finally {
            generateBtn.disabled = false;
            loadingSpinner.classList.add('d-none');
        }
    });
    
    downloadBtn.addEventListener('click', function() {
        if (currentFilename) {
            window.location.href = `/download/${currentFilename}`;
        }
    });
    
    feedbackInput.addEventListener('input', function() {
        regenerateBtn.disabled = !feedbackInput.value.trim() || !currentFilename || !lastGeneratedCode;
    });
    
    function showResults(data) {
        currentFilename = data.filename;
        lastGeneratedCode = data.test_cases;
        downloadBtn.disabled = false;
        regenerateBtn.disabled = !feedbackInput.value.trim() || !currentFilename || !lastGeneratedCode;

        apiInfo.innerHTML = `
            <strong>API:</strong> ${data.api_title}<br>
            <strong>Endpoints:</strong> ${data.endpoints_count}<br>
            <strong>Generated File:</strong> ${data.filename}
        `;

        testOutput.textContent = data.test_cases;
        if (window.Prism) Prism.highlightElement(testOutput);
        resultsSection.classList.remove('d-none');
    }
    
    function showError(message) {
        document.getElementById('errorMessage').textContent = message;
        errorSection.classList.remove('d-none');
    }
    
    function hideResults() {
        resultsSection.classList.add('d-none');
    }
    
    function hideError() {
        errorSection.classList.add('d-none');
    }
    
    // When uploading, store the spec content and type
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            lastApiSpecType = file.name.split('.').pop();
            const reader = new FileReader();
            reader.onload = function(evt) {
                lastApiSpec = evt.target.result;
            };
            reader.readAsText(file);
        }
    });
    
    regenerateBtn.addEventListener('click', async function() {
        const feedback = feedbackInput.value.trim();
        if (!feedback || !currentFilename) return;

        regenerateBtn.disabled = true;
        downloadBtn.disabled = true;
        showError(""); // Clear previous errors

        try {
            const response = await fetch('/regenerate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    filename: currentFilename,
                    suggestions: feedbackInput.value.trim(),
                    api_spec: lastApiSpec,
                    api_spec_type: lastApiSpecType,
                    previous_code: lastGeneratedCode
                })
            });
            const data = await response.json();
            if (response.ok && data.success) {
                showResults(data);
            } else {
                showError(data.error || 'Failed to regenerate test cases');
            }
        } catch (error) {
            showError('Network error: ' + error.message);
        } finally {
            regenerateBtn.disabled = false;
            downloadBtn.disabled = false;
        }
    });
});
