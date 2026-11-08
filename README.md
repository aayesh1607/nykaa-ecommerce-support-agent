
# Nykaa E-commerce Multi-Agent Customer Support System

## Project Overview

A Python-based multi-agent e-commerce customer-support capstone
demonstrating policy retrieval, order tracking, security checks,
human escalation, and structured response review.

The system combines FastAPI, CrewAI, Microsoft AutoGen,
ChromaDB, and local Ollama models.

This is an educational prototype using fictional customer orders
and fictional policy documents. It is not affiliated with Nykaa.

## Technologies

- Python 3.11.9
- FastAPI and WebSockets
- CrewAI
- Microsoft AutoGen AgentChat 0.7.5
- AutoGen OpenAI Extension
- Ollama with qwen2.5:1.5b
- ChromaDB
- Pydantic
- Pytest

## Implemented Features

1. 50 synthetic customer orders.
2. 12 fictional customer-support policy documents.
3. ChromaDB vector-based policy retrieval.
4. Full-document and sentence-level retrieval strategies.
5. Customer ID verification for order lookup.
6. Escalation scoring for order-status requests.
7. Basic prompt-injection detection.
8. Three-agent CrewAI customer-support workflow.
9. Two-agent AutoGen review workflow.
10. Optional live agent execution using local Ollama.
11. Deterministic mock execution without paid API calls.
12. FastAPI HTTP and WebSocket endpoints.
13. Structured JSON responses.
14. Human escalation for unresolved or unsafe requests.
15. Nine automated API and workflow tests.
16. RAG evaluation using 15 predefined questions.

## System Architecture

Customer Request
    |
    v
FastAPI HTTP / WebSocket
    |
    v
Customer Support Workflow
    |
    +-- Order Status Lookup
    |
    +-- ChromaDB Policy Retrieval
    |
    +-- Customer Verification
    |
    +-- Security Checks
    |
    +-- Optional Live CrewAI Workflow
    |
    v
Response Generation
    |
    v
Review Stage
    |
    +-- Quality Review
    |
    +-- Safety Review
    |
    +-- Optional Live AutoGen Review
    |
    v
Final Response / Human Escalation

## Execution Modes

The system supports deterministic mock execution and optional
live multi-agent execution using local Ollama models.

### Default Mock Mode

The default configuration uses MOCK_LLM mode.

This allows the application to run without paid API keys
or live LLM inference.

### Live CrewAI Mode

The project implements a three-agent CrewAI workflow.

To enable live CrewAI execution in PowerShell:

    $env:SUPPORT_MODE="LIVE_CREWAI"

The workflow uses the local Ollama qwen2.5:1.5b model.

Live CrewAI execution has been tested successfully.

### Live AutoGen Review Mode

The project implements a two-agent review workflow using
Microsoft AutoGen AgentChat 0.7.5.

To enable live AutoGen review:

    $env:REVIEW_MODE="LIVE_AUTOGEN"

The review uses Ollama's OpenAI-compatible API endpoint:

    http://localhost:11434/v1

Live AutoGen review has been tested independently and
through the FastAPI application.

### Start Ollama

Install Ollama separately and ensure the service is running.

Download the local model:

    ollama pull qwen2.5:1.5b

The default mock mode does not require Ollama inference.

## Installation and Setup

Use Python 3.11.

Create a virtual environment:

    py -3.11 -m venv .venv311

Activate it in PowerShell:

    .\.venv311\Scripts\Activate.ps1

Install dependencies:

    python -m pip install -r requirements.txt

## Running the Application

Start the FastAPI server:

    python -m uvicorn app.main:app --reload

Open the interactive API documentation:

    http://127.0.0.1:8000/docs

Health endpoint:

    http://127.0.0.1:8000/health

## Generate Sample Data

    python generate_data.py

## Build and Test RAG

    python test_rag_demo.py

## Run Automated Tests

    python -m pytest tests/test_api.py -v

## API Endpoints

- GET /
- GET /health
- POST /support/chat
- GET /support/order-status
- WebSocket /support/ws

## Example Request

POST /support/chat

    {
      "question": "Can I return an unused product?",
      "order_id": "",
      "customer_id": ""
    }

## RAG Retrieval Evaluation

The project evaluates two ChromaDB retrieval strategies
using 15 predefined customer-support questions and
12 fictional e-commerce policy documents.

### Retrieval Strategies

1. Full-document retrieval:
   Each policy document is indexed as a complete document.

2. Sentence-chunk retrieval:
   Policy documents are split into sentence-level chunks.

### Evaluation Results

| Metric | Full Documents | Sentence Chunks |
|---|---:|---:|
| Hit@1 | 100.00% | 100.00% |
| Hit@3 | 100.00% | 100.00% |
| Average Retrieval Latency | 639.42 ms | 598.46 ms |

Both strategies retrieved the expected policy source
within the top three results for all 15 test questions.

Sentence-chunk retrieval demonstrated approximately
6.4% lower average latency in this evaluation run.

### Evaluation Methodology

- Evaluation questions: 15
- Policy documents: 12
- Full-document index entries: 12
- Sentence-chunk index entries: 16
- Metrics: Hit@1, Hit@3, average latency
- Vector database: ChromaDB

These results measure retrieval performance on a small,
predefined evaluation set. They do not establish 100%
answer accuracy or guarantee performance on unseen queries.

### Reproduce the Evaluation

    python -m evaluation.evaluate_rag

Generated evaluation files:

- evaluation/rag_evaluation_results.csv
- evaluation/rag_evaluation_summary.json

## Security

- Order lookup requires matching customer ID.
- Suspicious requests are blocked by basic pattern checks.
- Sensitive and unresolved requests are escalated.
- No real customer data is included.
- Security protections are prototype-level.

## Test Results

Nine automated API and workflow tests passed on Python 3.11.9.

Live CrewAI execution and live AutoGen review have also
been tested separately.

## Important Implementation Limitations

- The system is an educational prototype, not a
  production customer-support platform.
- All customer orders and policy documents are fictional.
- Live local model responses can be inaccurate.
- A conservative grounding safeguard escalates generated
  answers that do not contain the complete verified
  reference answer; valid paraphrases may be escalated.
- The live AutoGen reviewer receives the response and
  policy source filename, but not the complete underlying
  policy text. Policy verification is therefore limited.
- The retrieval distance threshold is provisional.
- The RAG evaluation uses only 15 predefined questions.
- Retrieval scores do not measure end-to-end answer quality.
- Security checks are basic and require strengthening
  before any production use.

## Future Improvements

- Add session memory and response caching.
- Expand prompt-injection and PII protection.
- Evaluate retrieval on larger and more diverse datasets.
- Add structured request logging and request budgets.
- Improve policy-grounded AutoGen review.
- Strengthen live response generation and validation.
- Expand automated testing and failure-case coverage.
