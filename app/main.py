
import os
import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.services.support_workflow import CustomerSupportWorkflow
from app.review.autogen_review import AutoGenReviewStage
from app.review.live_autogen import LiveAutoGenReviewStage
from app.agents.live_crew import LiveCrewAIWorkflow, live_crewai_enabled


app = FastAPI(
    title="Nykaa E-commerce Multi-Agent Support System",
    description=(
        "E-commerce support with RAG, order lookup, "
        "CrewAI, AutoGen review, and human escalation."
    ),
    version="1.3.0",
)

workflow = CustomerSupportWorkflow()
reviewer = AutoGenReviewStage()


class SupportRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    order_id: str = ""
    customer_id: str = ""


def prepare_support_response(
    question: str,
    order_id: str = "",
    customer_id: str = "",
):
    response = workflow.process(question, order_id, customer_id)

    if live_crewai_enabled() and not response["requires_human"]:
        try:
            verified_response = response.copy()

            live_crew = LiveCrewAIWorkflow()
            response = live_crew.process(question, verified_response)

            verified_answer = verified_response["answer"].strip()
            generated_answer = response["answer"].strip()

            # Conservative grounding safeguard.
            if verified_answer.lower() not in generated_answer.lower():
                response = {
                    **response,
                    "answer": (
                        "The AI-generated response could not be verified "
                        "against the retrieved information. "
                        "Your request has been escalated to human support."
                    ),
                    "requires_human": True,
                    "escalation_score": 1.0,
                    "mode": "LIVE_CREWAI_GROUNDING_FAILED",
                }

        except Exception:
            response = {
                **response,
                "answer": (
                    "Automated AI processing is temporarily unavailable. "
                    "Your request has been escalated to human support."
                ),
                "requires_human": True,
                "escalation_score": 1.0,
                "mode": "LIVE_CREWAI_ERROR",
            }

    return response


async def review_support_response(question: str, response: dict):
    live_review_enabled = (
        os.getenv("REVIEW_MODE", "MOCK_LLM").upper()
        == "LIVE_AUTOGEN"
    )

    if live_review_enabled and not response["requires_human"]:
        try:
            return await LiveAutoGenReviewStage().review_async(
                question, response
            )
        except Exception:
            return {
                "approved": False,
                "requires_human": True,
                "quality_review": "ESCALATE: AutoGen review failed.",
                "safety_review": "ESCALATE: Automated review unavailable.",
                "reviewers": [
                    "quality_reviewer",
                    "safety_reviewer",
                ],
                "mode": "LIVE_AUTOGEN_ERROR",
            }

    return reviewer.review(question, response)


async def process_support_request_async(
    question: str,
    order_id: str = "",
    customer_id: str = "",
):
    response = await asyncio.to_thread(
        prepare_support_response,
        question,
        order_id,
        customer_id,
    )

    review = await review_support_response(question, response)

    return {
        "response": response,
        "review": review,
        "final_status": (
            "human_review"
            if response["requires_human"] or review["requires_human"]
            else "approved"
        ),
    }


def process_support_request(
    question: str,
    order_id: str = "",
    customer_id: str = "",
):
    return asyncio.run(
        process_support_request_async(
            question,
            order_id,
            customer_id,
        )
    )


@app.get("/")
def home():
    return {
        "message": "Welcome to Nykaa E-commerce Support System",
        "mode": (
            "LIVE_CREWAI"
            if live_crewai_enabled()
            else "MOCK_LLM"
        ),
        "review_mode": os.getenv("REVIEW_MODE", "MOCK_LLM"),
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/support/chat")
async def support_chat(request: SupportRequest):
    return await process_support_request_async(
        request.question,
        request.order_id,
        request.customer_id,
    )


@app.get("/support/order-status")
async def order_status(order_id: str, customer_id: str):
    return await process_support_request_async(
        "Where is my order?",
        order_id,
        customer_id,
    )


@app.websocket("/support/ws")
async def support_websocket(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            request = SupportRequest.model_validate(data)

            result = await process_support_request_async(
                request.question,
                request.order_id,
                request.customer_id,
            )

            await websocket.send_json(result)

    except WebSocketDisconnect:
        pass
    except Exception:
        await websocket.send_json({
            "error": "Invalid request or processing failure.",
            "final_status": "human_review",
        })
        await websocket.close()
