"""
Here the auction system definition is created.
It will be called from the exec file main_auction_system.py
It builds the whole agent system with the orchestrator and the buyer agents

All communication will be happening through the STATE of the agents. 
It is possible for the communication to happen through more production-ready means.
Edges and nodes would be needed. 
If the system descides that transition between the agents is needed, an edge will be used.
This is the classic structure of LangGraph.
Tools have to be defined for more functionality.
"""