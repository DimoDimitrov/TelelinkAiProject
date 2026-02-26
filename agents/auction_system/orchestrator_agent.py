"""
Here the orchestrator agent definition is created.
It will be called from the auction system definition
It will be used to orchestrate the auction process

The agent will have STATE memory, prompt, and tools if needed.
State will be passed in the prompt as well.
All will go inside 'contents' parameter of the agent.

The orchestrator will be responsible for:
- monitoring the auction process
- communicating with the buyer agents
- updating the state of the auction
- updating the state of the buyer agents
"""