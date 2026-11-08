import os

from crewai import Agent, Crew, LLM, Process, Task


class LiveCrewAIWorkflow:
    """
    Real three-agent CrewAI execution using local Ollama.

    This workflow receives an already-validated support response.
    It must not independently access orders or invent policy details.
    """

    def __init__(self):
        self.llm = LLM(
            model="ollama/qwen2.5:1.5b",
            base_url="http://localhost:11434",
            temperature=0,
            context_window_size=4096,
        )

    def process(self, question: str, verified_response: dict) -> dict:
        if verified_response.get("requires_human"):
            return verified_response

        category = verified_response.get("category", "")
        evidence = verified_response.get("answer", "")
        sources = verified_response.get("sources", [])

        coordinator = Agent(
            role="Customer Support Coordinator",
            goal="Produce clear customer support responses grounded in verified evidence.",
            backstory="You coordinate safe e-commerce customer support.",
            llm=self.llm,
            verbose=False,
            allow_delegation=False,
        )

        specialist = Agent(
            role=(
                "Order Support Specialist"
                if category == "order"
                else "Policy Support Specialist"
            ),
            goal="Verify that support answers contain only supplied facts.",
            backstory="You carefully check customer support evidence.",
            llm=self.llm,
            verbose=False,
            allow_delegation=False,
        )

        quality_agent = Agent(
            role="Response Quality Specialist",
            goal="Check answers for accuracy, completeness, and unsupported claims.",
            backstory="You review e-commerce support responses for quality.",
            llm=self.llm,
            verbose=False,
            allow_delegation=False,
        )

        evidence_task = Task(
            description=(
                "Customer question: {question}\n"
                "Verified evidence: {evidence}\n"
                "Sources: {sources}\n\n"
                "Check the evidence. Do not add facts, conditions, "
                "dates, or policies that are not explicitly provided. "
                "Identify all important details that must be preserved."
            ),
            expected_output="A concise summary of verified facts.",
            agent=specialist,
        )

        response_task = Task(
            description=(
                "Answer the customer question using ONLY the verified evidence "
                "and the preceding specialist's findings. "
                "Preserve all relevant conditions and restrictions. "
                "Do not invent information."
            ),
            expected_output="A short, helpful, evidence-grounded customer response.",
            agent=coordinator,
            context=[evidence_task],
        )

        quality_task = Task(
            description=(
                "Review the proposed answer against the verified evidence. "
                "Correct omissions and remove unsupported claims. "
                "Return only the final customer-facing answer. "
                "If the evidence is insufficient, say that human support is needed."
            ),
            expected_output="A final grounded customer response without extra commentary.",
            agent=quality_agent,
            context=[evidence_task, response_task],
        )

        crew = Crew(
            agents=[specialist, coordinator, quality_agent],
            tasks=[evidence_task, response_task, quality_task],
            process=Process.sequential,
            verbose=False,
            memory=False,
        )

        result = crew.kickoff(
            inputs={
                "question": question,
                "evidence": evidence,
                "sources": ", ".join(sources) if sources else "Verified order data",
            }
        )

        final_answer = str(result.raw).strip()

        if not final_answer:
            raise RuntimeError("CrewAI returned an empty response.")

        return {
            **verified_response,
            "answer": final_answer,
            "mode": "LIVE_CREWAI",
        }


def live_crewai_enabled() -> bool:
    return os.getenv("SUPPORT_MODE", "MOCK_LLM").upper() == "LIVE_CREWAI"
