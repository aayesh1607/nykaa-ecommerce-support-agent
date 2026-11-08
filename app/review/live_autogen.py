
import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily


class LiveAutoGenReviewStage:
    """
    Two real AutoGen reviewers using local Ollama.
    AI reviewer approval is advisory, not a guarantee
    of factual correctness.
    """

    async def review_async(self, question: str, response: dict) -> dict:
        if response.get("requires_human", False):
            return {
                "approved": False,
                "requires_human": True,
                "quality_review": "ESCALATE: Existing human review requirement.",
                "safety_review": "ESCALATE: Existing human review requirement.",
                "reviewers": ["quality_reviewer", "safety_reviewer"],
                "mode": "LIVE_AUTOGEN",
            }

        model_client = OpenAIChatCompletionClient(
            model="qwen2.5:1.5b",
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            model_info={
                "vision": False,
                "function_calling": False,
                "json_output": False,
                "structured_output": False,
                "family": ModelFamily.UNKNOWN,
            },
        )

        try:
            quality_agent = AssistantAgent(
                name="quality_reviewer",
                model_client=model_client,
                system_message=(
                    "You are a strict customer-support quality reviewer. "
                    "Check the answer against the supplied verified evidence. "
                    "Reject unsupported promises, missing restrictions, "
                    "or fabricated policies. "
                    "Reply with APPROVED or ESCALATE, followed by a reason."
                ),
            )

            safety_agent = AssistantAgent(
                name="safety_reviewer",
                model_client=model_client,
                system_message=(
                    "You are a strict customer-support safety reviewer. "
                    "Check for privacy violations, unsupported actions, "
                    "unsafe instructions, and misleading claims. "
                    "Never override an existing escalation. "
                    "Reply with APPROVED or ESCALATE, followed by a reason."
                ),
            )

            team = RoundRobinGroupChat(
                participants=[quality_agent, safety_agent],
                termination_condition=MaxMessageTermination(3),
            )

            task = (
                f"Customer question: {question}\n"
                f"Category: {response.get('category', '')}\n"
                f"Answer: {response.get('answer', '')}\n"
                f"Sources: {response.get('sources', [])}\n\n"
                "Both reviewers must independently evaluate this answer. "
                "Use only the supplied information. "
                "If evidence is insufficient, respond ESCALATE."
            )

            result = await team.run(task=task)

            reviews = {
                message.source: str(message.content)
                for message in result.messages
                if message.source in ("quality_reviewer", "safety_reviewer")
            }

            quality_text = reviews.get(
                "quality_reviewer", "ESCALATE: Missing quality review."
            )
            safety_text = reviews.get(
                "safety_reviewer", "ESCALATE: Missing safety review."
            )

            def is_approved(text: str) -> bool:
                return text.strip().upper().startswith("APPROVED")

            approved = (
                is_approved(quality_text)
                and is_approved(safety_text)
            )

            return {
                "approved": approved,
                "requires_human": not approved,
                "quality_review": quality_text,
                "safety_review": safety_text,
                "reviewers": ["quality_reviewer", "safety_reviewer"],
                "mode": "LIVE_AUTOGEN",
            }

        finally:
            await model_client.close()

    def review(self, question: str, response: dict) -> dict:
        return asyncio.run(self.review_async(question, response))
