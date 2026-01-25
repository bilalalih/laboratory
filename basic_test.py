import crewai
from crewai import Agent, Task, Crew

print(crewai.__version__)  # should be 1.x now

# Minimal agent test (no API key needed yet)
researcher = Agent(
    role='Researcher',
    goal='Find cool facts',
    backstory='You love facts.',
    verbose=True
)

task = Task(
    description='Find 3 facts about Lagos, Nigeria',
    agent=researcher
)

crew = Crew(agents=[researcher], tasks=[task])
# Don't run .kickoff() yet — just check syntax
print("Crew syntax OK")