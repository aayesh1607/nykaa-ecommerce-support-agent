
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.services.support_workflow import CustomerSupportWorkflow
from app.review.autogen_review import AutoGenReviewStage
from app.agents.live_crew import LiveCrewAIWorkflow, live_crewai_enabled


app = FastAPI(
    title="Nykaa E-commerce Multi-Agent Support System",
    description="E-commerce support with RAG, order lookup, CrewAI, and review.",
    version="1.2.0",
)

workflow = CustomerSupportWorkflow()
reviewer = AutoGenReviewStage()


class SupportRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    order_id: str = ""
    customer_id: str = ""


def process_support_request(
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

            # Conservative grounding safeguard:
            # The original verified answer must be preserved.
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

    review = reviewer.review(question, response)

    return {
        "response": response,
        "review": review,
        "final_status": (
            "human_review"
            if response["requires_human"] or review["requires_human"]
            else "approved"
        ),
    }


@app.get("/")
def home():
    return {
        "message": "Welcome to Nykaa E-commerce Support System",
        "mode": "LIVE_CREWAI" if live_crewai_enabled() else "MOCK_LLM",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/support/chat")
def support_chat(request: SupportRequest):
    return process_support_request(
        request.question,
        request.order_id,
        request.customer_id,
    )


@app.get("/support/order-status")
def order_status(order_id: str, customer_id: str):
    return process_support_request(
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

            result = process_support_request(
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
