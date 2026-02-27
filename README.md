## Telelink AI – TeleHelper Agents

### Overview

This repository contains the **TeleHelper** AI agents for real‑estate use cases.  
The core of the project is a **Must agent** that:

- Uses **Google Gemini** as the LLM.
- Reads plain‑text **property documents** from `documents/properties`.
- Stores vector embeddings in a **persistent ChromaDB** store.
- Answers user questions about the properties using a simple **RAG pipeline**.

There is also an experimental **auction system** (orchestrator + buyer agents) that will use the same property context to simulate automated bidding between buyers. That part is currently under active development. Testing it is currently not possible.

---

### High‑level architecture

- `agents/must/`
  - `must_agent.py` – `MustAgent` and `MustAgentConfig` (Gemini client + RAG + conversation state).
- `core/state/`
  - `state.py` – lightweight dict‑based state with conversation history helpers.
- `core/prompts/`
  - `prompts.py` – system prompts for the Must agent and auction agents.
  - `prompt_builder.py` – `PromptBuilder` + `make_must_agent_prompt`.
- `core/database/`
  - `embedder.py` – `Embedder` using Gemini text‑embedding model.
  - `vectorstore/prop_chroma.py` – `ChromaOperator` wrapper around **chromadb**.
  - `vectorstore/prop_vectorization.py` – scripts and helpers to vectorize property `.txt` files into Chroma.
  - `vectorstore/prop_retriever.py` – `PropertyRetriever` combining `Embedder` + `ChromaOperator` for RAG.
- `documents/properties/`
  - Sample property descriptions as `.txt` files.
- `exec/`
  - `main_must_agent.py` – CLI entrypoint for the TeleHelper Must agent.
  - `main_auction_system.py` – placeholder entrypoint for the auction system (WIP).

---

### Requirements

- **Python**: 3.10+ recommended
- **System**: Tested primarily on Windows, but logic is platform‑agnostic except for hard‑coded paths in `prop_vectorization.py`.
- **Python packages** (minimum):
  - From `requirements.txt`:
    - `langchain>=1.2.10`
    - `langgraph>=1.0.9`
    - `python-dotenv>=1.0.0`
  - Used in code (add these to your environment if not already installed):
    - `google-genai` (new `google.genai` Gemini client)
    - `chromadb`
    - `langsmith`

> **Tip**: Keep your virtual environment isolated for this project.

---

### Installation

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd TelelinkAiProject/TelelinkAiProject
   ```

2. **Create and activate a virtual environment**

   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\activate

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt

   # Plus the runtime deps used in code
   pip install google-genai chromadb langsmith
   ```

---

### Configuration (.env)

Create a `.env` file in the project root (`TelelinkAiProject/TelelinkAiProject`) with at least:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

Notes:

- `core/database/embedder.py` and `exec/main_must_agent.py` both expect `GOOGLE_API_KEY` to be set.
- `exec/main_must_agent.py` wraps the Gemini client with **LangSmith**; if you want tracing, also configure LangSmith/LangChain environment variables (e.g. `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2`, etc.) according to the LangSmith documentation.

NOTE:
If .env file is not provided with the comopleted task, I will be online to send it.

---

### Preparing the property vector store (Chroma)

The Must agent uses a persistent **ChromaDB** collection of property documents.

- Property `.txt` files live under:
  - `documents/properties/`
- Chroma persistence path and collection name are defined in:
  - `core/database/vectorstore/prop_vectorization.py`
  - Key constants:
    - `CHROMA_LOCATION` – default is a Windows path under `persist_gemini/properties`.
    - `CHROMA_COLLECTION_NAME` – defaults to `"properties"`.

#### 1. Adjust paths if necessary

Open `core/database/vectorstore/prop_vectorization.py` and check:

- `CHROMA_LOCATION` – update this if you are not on Windows or if you want a different location.
- The default `dir_path` in `main()` points to `documents/properties` – update only if your input directory is different.

#### 2. Run the vectorization script

With your virtualenv activated and `.env` configured:

```bash
python -m core.database.vectorstore.prop_vectorization
```

This will:

- Ensure the Chroma client and `properties` collection exist.
- Read all `.txt` files in `documents/properties`.
- Embed each file using Gemini.
- Upsert the embeddings + metadata into the Chroma collection at `CHROMA_LOCATION`.

You only need to re‑run this when you **add or change** property documents.

---

### Running the TeleHelper (Must) agent

The main interactive entrypoint is `exec/main_must_agent.py`.

From the project root (with venv activated and vector store prepared):

```bash
python -m exec.main_must_agent
```

What this script does:

- Loads environment variables from `.env`.
- Creates a Gemini client via `google.genai.Client`.
- Wraps it with `langsmith.wrappers.wrap_gemini` (for optional tracing).
- Instantiates a `PropertyRetriever` that talks to the Chroma collection defined by `CHROMA_LOCATION` / `CHROMA_COLLECTION_NAME`.
- Creates a `MustAgent` with:
  - Model (default `"gemini-2.5-flash"` in `main_must_agent.py`).
  - Conversation state (`core/state/state.py`).
  - RAG enabled (`use_rag=True`).
- Starts a simple REPL:
  - Prompts with `User >`.
  - Sends your question to the agent.
  - Prints the answer as `Agent >`.

Exit by submitting an **empty line**.

---

### Auction system (experimental)

The project also includes an early stub of an auction system:

- `agents/auction_system/auction_system_def.py`
- `agents/auction_system/orchestrator_agent.py`
- `agents/auction_system/buyer_agent.py`
- `agents/auction_system/agent_configs/`
  - Example configs: `conf_orch.py`, `conf_buy1.py`, `conf_buy2.py`
- `exec/main_auction_system.py` – placeholder entry script.

This system is intended to:

- Orchestrate auctions for properties.
- Coordinate multiple buyer agents with different budgets and strategies.
- Use the same property data / vector store as context.

At the moment, `main_auction_system.py` is a **skeleton** and not a fully wired runnable entrypoint. Treat this subsystem as **work in progress**.

---

### Development notes

- Tests are planned under `exec/tests/` but are currently just placeholders.
- The code is structured for incremental extension:
  - You can add new agent types under `agents/`.
  - You can plug in additional collections or domains by:
    - Creating new Chroma collections via `ChromaOperator`.
    - Writing retrievers similar to `PropertyRetriever`.
    - Adding new prompt templates in `core/prompts/prompts.py`.

NOTICE:
  The agent is placed in a LangSmith wrapper. 
  This allows us to follow the execution of the agent step by step.
  It is really usefull when using LangGraph.
  In the 'Must' agent, it does not log much, because LangSmith is designed to work with LangGraph arcitecture.
  For the purpose of running the agent, only the .env would be required.
  An account is not currently mandatory. 
  If you descide to change the account with one of your own, just change the variables for LangSmith in .env file.
  Most important would be 'LANGSMITH_API_KEY'

  The .env file stays at the project root. (The most outer layer of the program)
  If you missplace it, the project would not work.

REQUIREMENTS:
  The requirements.txt file should be containing all the needed dependencies.
  If something is missing, here is what has been used:
  langchain>=1.2.10
  langgraph>=1.0.9
  python-dotenv>=1.0.0
  google genai sdk packet
  langsmith==0.7.6

ARCHITECTURE:
MUST REQUIREMENTS
  The project takes properties form the documents/properties dir.
  An Embedder is created that makes the embedding for the documents.
  Chunking is not used, because the documents are rather small.
  If in further cases chunking is needed, a class would be easily integrated. 
  The Chunker would separate the documents semantically, with some buffer allowed and metadata for the document appended to the file. This is a must, so the agent can descide for what property the info is.
  Configs would need to get adjusted then.
  Chroma is used for persistance vectorization.
  A STATE class is created, so the agent can have memmory of the user's previous questions.
  A prompt is created so the agent can be personalized and answer adequately.
  Everything is passed in a gemini agent, that answers te user querys.
  For the 'Must' agent, each user query triggers a fetch from the vectorstore.
  In later stages of the project, LangGraph would be implemented.
  The RAG will be made as a tool and the agent will call it when needed.
  This is a constraint for the cirrent approach.

SHOULD REQUIREMENTS
  For the auction agents, prompts were created.
  The foundation classes were made.
  
  LangGraph needs to be implemented and used. 
  Nodes and edges need to get created.
  Appropriete tools needs to get created to the agents.
  
  
  Everything was created in a way that would allow us to reuse it.
  This way the auction system can be created easy and would allow scalability.


WRITE-UP:
• Key decisions and trade-offs
  I chose Google Gemini (via `google-genai`) as the primary LLM because it offers strong reasoning and native embedding support.
  I used a simple RAG pipeline with ChromaDB and no chunking for property documents to keep the implementation straightforward and transparent, at the cost of less flexibility if documents grow larger. I left a Chunker class that can get implemented.
  I introduced a custom `State` abstraction and prompt layer instead of a heavier framework to keep control and readability high, trading off some of the orchestration features that LangGraph would later provide. This descision was made only for the 'Must' agent.
  I wired LangSmith only as an optional wrapper around the Gemini client so tracing is available for debugging, but not strictly required to run the Must agent, which simplifies onboarding at the cost of less standardized observability.
  I focused on a CLI entrypoint (`exec/main_must_agent.py`) instead of a full web UI to keep the core agent behavior clear and testable, accepting a less polished user experience for non-technical users.
  I laid the auction system out as a set of reusable agents and configs before fully integrating LangGraph, intentionally deferring complexity so the foundations are extensible but leaving the auction flow incomplete in the current version.


• What you would improve with more time
  I would complete the auction system.
  I wpuld make adjustments to the prompts.
  Tools would be usefull to have, based on the direction and the size of the project.
  CI/CD would be usefull.
  Uploading it to cloud can be usefull as well.
  Creating a GUI for thesting purposes and creating front-end would be nice as well.
  Optimization of the promot and information, so I can cut the costs is a nice idea as well.
  A posgres database would be helpfull to have, so we know how many vectors there were imported.
