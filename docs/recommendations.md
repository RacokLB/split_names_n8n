# Architecture & Security Recommendations

This document provides architectural guidance and specialized prompt templates to ensure the **n8n Name Splitter Automation** is robust, secure, and scalable.

---

## 🏗️ Recommended Architecture

To move from a developer tool to a production-ready internal service, consider the following architectural adjustments:

### 1. Security Layer (Critical)

- **Authentication**: Currently, the FastAPI endpoint is exposed. Implement a simple header-based API Key validation (`X-API-Key`) or use FastAPI's `OAuth2` with scopes.
- **Tunnel Security**: If using Localtunnel/Ngrok for production, use a persistent domain and restricted IP access if possible.
- **Environment Secrets**: Ensure all Google Credentials and API URLs are stored in n8n's Credential Manager and the FastAPI `.env` file, never hardcoded.

### 2. Scalability & Reliability

- **Batch Processing**: The current n8n workflow uses an `Aggregate` node. For very large files (5k+ rows), consider using **n8n's Batching** (Split in Batches) to avoid timeouts in the HTTP Request node.
- **Asynchronous Processing**: If name splitting becomes more complex (e.g., calling an LLM), switch the FastAPI endpoint to return a `task_id` and have n8n poll for the result.
- **Dead Letter Queue**: Implement an "Error Folder" in Google Drive. If the workflow fails, move the file there and notify the user via Gmail (you already have a basic version of this).

### 3. Observability

- **Structured Logging**: Implement logging in `main.py` using `logging` or `structlog` to track which rows failed processing.
- **Status Endpoint**: Keep the `/` root endpoint for health checks by monitoring tools.

---

## 📝 Prompt Template: Security & Testing Audit

Copy and paste the prompt below into an LLM (like Antigravity or ChatGPT) along with your code to perform a deep audit.

### The Prompt

> [!TIP]
> **Instructions**: Paste the content of `main.py`, `Dockerfile`, and `n8n_workflow.json` before sending this prompt.

```markdown
Act as a Senior Security Engineer and SDET. Analyze the following project components (FastAPI Backend, n8n Workflow, and Docker setup) for the "Spanish Name Splitter" project.

Please provide a detailed report covering:

1. **Security Vulnerabilities**:
   - Check for missing authentication/authorization in the FastAPI endpoints.
   - Evaluate data validation (Pydantic models) for potential injection or malformed data issues.
   - Analyze the Docker configuration for "Run as Root" issues or exposed ports.
   - Review n8n workflow for sensitive data handling in logs.

2. **Testing Strategy**:
   - Generate a list of 10 complex Spanish name edge cases (e.g., "Maria del Pilar de la Rosa", "Juan O'Brian", "Jose Maria de los Angeles").
   - Suggest a Pytest suite structure for the `split_names` logic.
   - Propose an integration test to simulate the n8n-to-FastAPI request.

3. **Error Handling**:
   - Identify points of failure in the n8n workflow (e.g., Google API rate limits, HTTP timeouts).
   - Suggest improvements to the current `If` node logic for error detection.

4. **Architecture Refactoring**:
   - How would this architecture change if we needed to process 100,000 names per hour?
```

---

## 🛠️ Testing Edge Cases (Immediate Use)

Use these test cases to validate your `split_names` function manually or in a unit test:

| Input                          | Expected P_APELLIDO | Expected S_APELLIDO | Note                       |
| :----------------------------- | :------------------ | :------------------ | :------------------------- |
| `JUAN DE LA CRUZ PEREZ GARCIA` | `Perez`             | `Garcia`            | Compound first name prefix |
| `MARIA DEL PILAR RUIZ`         | `Ruiz`              | (Empty)             | Compound middle name       |
| `CARLOS SAN ROMAN DEL VALLE`   | `San Roman`         | `Del Valle`         | Compound surnames          |
| `DIEGO VELAZQUEZ`              | `Velazquez`         | (Empty)             | Single surname             |
| `LUIS DE TORRES`               | `De Torres`         | (Empty)             | Surname with prefix        |
