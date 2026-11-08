import os

# Avoid accidentally making paid LLM requests during setup.
os.environ["OPENAI_API_KEY"] = "sk-placeholder-not-a-real-key"

from crewai import Agent


def create_agents():
    customer_support_agent = Agent(
        role="Customer Support Coordinator",
        goal="Understand customer requests and coordinate safe support responses.",
        backstory="You coordinate customer support for a fictional Nykaa-style e-commerce demonstration.",
        verbose=False,
        allow_delegation=False,
        llm="openai/gpt-4o-mini"
    )

    order_support_agent = Agent(
        role="Order Support Specialist",
        goal="Help customers understand verified order information.",
        backstory="You specialize in customer order tracking and escalation.",
        verbose=False,
        allow_delegation=False,
        llm="openai/gpt-4o-mini"
    )

    policy_support_agent = Agent(
        role="Policy Support Specialist",
        goal="Provide answers grounded in retrieved policy documents.",
        backstory="You specialize in explaining documented customer support policies.",
        verbose=False,
        allow_delegation=False,
        llm="openai/gpt-4o-mini"
    )

    return [
        customer_support_agent,
        order_support_agent,
        policy_support_agent
    ]
