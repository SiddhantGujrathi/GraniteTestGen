# GraniteTestGen – AI-Powered Test Case Generator

## 🔮 Overview
**GraniteTestGen** is an AI-powered web application that automatically generates comprehensive JUnit 5 test cases from OpenAPI (YAML/YML/JSON) specifications using IBM's Granite foundation model. It enhances API quality assurance by reducing manual effort and increasing coverage, speed, and accuracy in test case creation.

---

## ✨ Key Highlights
- ⚡ **Generates executable test cases** in seconds, reducing hours of manual work.
- 🔧 **Supports YAML, YML, and JSON** OpenAPI specs.
- 👩‍💻 Designed for **QA engineers, developers, and DevOps**.
- 🔌 **Powered by IBM's Granite LLM** via Watson AI.
- 📂 **Downloads ready-to-use JUnit 5 `.java` test files**.
- 🔄 **Supports regeneration, feedback, and rollback with Git**.

---

## 📅 Executive Summary
Manual API testing is slow, error-prone, and repetitive. GraniteTestGen automates this by using AI to generate intelligent and production-ready test code. It transforms OpenAPI specifications into executable JUnit 5 test classes, covering all important cases including happy paths, negative scenarios, and boundary values.

---

## 🔹 What It Does
GraniteTestGen intelligently bridges API documentation and automated testing. By uploading OpenAPI/Swagger files, the system generates:
- Positive & Negative Test Cases
- Boundary Value & Edge Case Tests
- JUnit 5 classes with full annotations

---

## ❌ Problems It Solves
Traditional test creation is:
- ⏱ **Time-consuming**
- ❌ **Error-prone**
- ❓ **Incomplete** (often misses edge cases)
- 💬 **Repetitive** (manual repetition across endpoints)

GraniteTestGen solves these by generating high-quality tests in under 30 seconds.

---

## 🚀 Workflow
1. Upload OpenAPI file (YAML/YML/JSON)
2. Parse and validate endpoints, schemas, responses
3. Construct AI prompt with test logic
4. Use IBM Granite model to generate Java test code
5. Format and highlight code
6. Download production-ready `.java` files

---

## 🌐 System Architecture

### Frontend
- HTML/CSS + JavaScript + Bootstrap  
- Drag-and-drop file upload  
- Syntax-highlighted code display  

### Backend
- Python + Flask  
- JSON/YAML parser  
- File manager + Validator  

### AI Layer
- IBM Watson + Granite 3-3-8b-instruct  
- Prompt engineering  
- OAuth-secured requests  

---

## 📊 Technical Features
- 🔢 JSON, YAML, YML support  
- ⛏ Spring Boot compatible  
- 🎨 Syntax-highlighted Java code with Prism.js  
- ⚖️ Error handling and validation  
- ⏩ Instant download and integration  

---

## 📈 Performance Metrics
- ⏰ Avg. generation time: < 30 seconds  
- 📂 File size supported: up to 16MB  
- 🤝 Concurrent multi-user support  
- ✔️ Adheres to Java & JUnit best practices  

---

## 👥 Target Users
- **QA Engineers**: Eliminate manual test writing  
- **Developers**: Validate API implementations  
- **DevOps**: CI/CD-friendly test generation  

---

## 🌍 Use Cases
- Microservices test automation  
- API-first development workflows  
- Third-party API contract testing  
- Rapid prototyping for MVPs/startups  

---

## 🔄 Future Roadmap
- 📊 Multi-language test support (Python, JS, C#)  
- 🤖 Fine-tuned prompt templates & auto-learning  
- 🏗 CI/CD pipeline integration (Jenkins, GitHub Actions)  
- 📈 In-app test execution & reporting  

---

## 🔗 Technologies Used

| Category        | Tech Stack                         |
|----------------|-------------------------------------|
| Frontend       | HTML, CSS, Bootstrap, JS, Prism.js |
| Backend        | Flask, PyYAML, Requests             |
| AI Integration | IBM Watson, Granite, OAuth2         |
| DevOps         | Git, GitHub                         |

---

## ✅ How to Use
1. Clone this repo  
2. Run `pip install -r requirements.txt`  
3. Launch Flask server: `python app.py`  
4. Open in browser and upload OpenAPI spec  
5. Download your generated test code  

---

> _"Turning specs into code. Instantly."_
