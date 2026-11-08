# Nykaa E-commerce Multi-Agent Customer Support System

## Project Overview

A Python-based e-commerce customer-support capstone demonstrating
policy retrieval, order tracking, security checks, human escalation,
and structured review.

This is an educational prototype using fictional customer orders
and fictional policy documents. It is not affiliated with Nykaa.

## Technologies

- Python 3.11
- FastAPI
- CrewAI
- Microsoft AutoGen AgentChat
- ChromaDB
- Pydantic
- Pytest

## Implemented Features

1. 50 synthetic customer orders.
2. 12 fictional customer-support policy documents.
3. ChromaDB vector search.
4. Full-document and sentence-level retrieval strategies.
5. Customer ID verification for order lookup.
6. Escalation scores for order-status requests.
7. Basic prompt-injection detection.
8. Three CrewAI agent definitions.
9. Two-role mock review stage using AutoGen message objects.
10. FastAPI HTTP and WebSocket endpoints.
11. Structured JSON responses.
12. Nine automated API and workflow tests.

## Architecture

Customer Request
    |
    v
FastAPI
    |
    v
Customer Support Workflow
    |
    +-- Order Status Tool
    |
    +-- ChromaDB Policy Retrieval
    |
    +-- Security Checks
    |
    v
Two-Role Review Stage
    |
    +-- Quality Review
    |
    +-- Safety Review
    |
    v
Approved Response / Human Escalation

## Running the Project

Create a Python 3.11 virtual environment.

Install dependencies:

    python -m pip install -r requirements.txt

Start the API:

    python -m uvicorn app.main:app --reload

Open:

    http://127.0.0.1:8000/docs

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

## Important Implementation Limitations

This project runs in MOCK_LLM mode without paid API calls.

CrewAI agent definitions are implemented and can be initialized,
but the current customer-support workflow uses deterministic Python
routing rather than executing a live CrewAI crew.

The review stage uses AutoGen message objects with deterministic
quality and safety rules. It is not a live AutoGen multi-agent conversation.

The retrieval distance threshold is provisional and has not been
calibrated using a comprehensive evaluation dataset.

Policy documents are fictional examples and must not be interpreted
as official Nykaa policies.

## Security

- Order lookup requires matching customer ID.
- Suspicious requests are blocked by basic pattern checks.
- Sensitive and unresolved requests are escalated.
- No real customer data is included.

## Test Results

9 automated tests passed on Python 3.11.9.

## Future Improvements

- Execute real CrewAI task orchestration.
- Implement a live AutoGen reviewer conversation.
- Add session memory and response caching.
- Expand prompt-injection and PII protection.
- Evaluate retrieval quality using a labeled dataset.
- Add structured request logging and request budgets.
