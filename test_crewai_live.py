from crewai import Agent, Task, Crew, Process, LLM

llm = LLM(
    model="ollama/qwen2.5:1.5b",
    base_url="http://localhost:11434",
    temperature=0
)

agent = Agent(
    role="Customer Support Assistant",
    goal="Answer customer questions using only the supplied policy.",
    backstory="You are a careful e-commerce customer support assistant.",
    llm=llm,
    verbose=False,
    allow_delegation=False
)

task = Task(
    description=(
        "Policy: Unused products may be returned within 7 days "
        "if the original packaging is intact. "
        "Question: Can I return an unused product? "
        "Answer using ONLY the policy provided. "
        "Do not invent additional conditions."
    ),
    expected_output="One short answer grounded in the supplied policy.",
    agent=agent
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential,
    verbose=False,
    memory=False
)

print("Starting real CrewAI execution...")
result = crew.kickoff()
print("CREWAI RESULT:")
print(result.raw)
