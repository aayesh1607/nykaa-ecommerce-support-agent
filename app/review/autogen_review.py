from autogen_agentchat.messages import TextMessage


class AutoGenReviewStage:
    """
    Two-role review stage using AutoGen message objects.
    MOCK_LLM mode uses deterministic review rules.
    """

    def review(self, question: str, response: dict) -> dict:
        answer = response.get("answer", "")
        category = response.get("category", "")
        sources = response.get("sources", [])
        requires_human = response.get("requires_human", False)

        quality_approved = bool(answer.strip())

        if category == "policy" and not sources and not requires_human:
            quality_approved = False

        quality_message = TextMessage(
            content=(
                "APPROVED: Response has sufficient evidence."
                if quality_approved
                else "REJECTED: Response is missing or lacks required evidence."
            ),
            source="quality_reviewer"
        )

        safety_approved = (
            category != "security"
            and not requires_human
        )

        safety_message = TextMessage(
            content=(
                "APPROVED: Response may be delivered automatically."
                if safety_approved
                else "ESCALATE: Human review or security handling required."
            ),
            source="safety_reviewer"
        )

        approved = quality_approved and safety_approved

        return {
            "approved": approved,
            "requires_human": not approved or requires_human,
            "quality_review": quality_message.content,
            "safety_review": safety_message.content,
            "reviewers": [
                quality_message.source,
                safety_message.source
            ],
            "mode": "MOCK_LLM"
        }
