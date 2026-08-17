# AI Headline Variation Agent

An AI-powered headline optimization agent that generates, evaluates, and iteratively improves headline variations using an **LLM-driven perception → reasoning → reflection loop**.

The system combines **OpenRouter**, **ChromaDB**, deterministic Python tools, structured prompts, and production guardrails to create reliable and repeatable headline generation.

## 🚀 Features

* Generate multiple variations of a given headline
* Analyze headline quality using an LLM
* Calculate exact character counts using deterministic Python functions
* Detect power words
* Evaluate SEO keyword fit
* Iteratively improve generated headlines through reflection
* Store previous reflection feedback in ChromaDB
* Semantically retrieve relevant past critiques
* Enforce structured JSON responses from the LLM
* Retry failed API requests using exponential backoff
* Track token usage and enforce token budgets
* Detect stuck or repetitive agent loops
* Generate structured execution logs
* Interactive Streamlit interface

## 🏗️ Architecture

```text
                         User
                           │
                           ▼
                    Streamlit UI
                           │
                           ▼
                    Agent Controller
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         Perception     Reasoning    Reflection
              │            │            │
              └────────────┼────────────┘
                           ▼
                      LLM Client
                           │
                           ▼
                      OpenRouter
                           │
                           ▼
                      LLM Model
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          tools.py    ChromaDB       Guardrails
              │            │            │
              ▼            ▼            ▼
       Deterministic    Agent       Retry / JSON
        evaluation      Memory       / Tokens
                           │
                           ▼
                      logger.py
                           │
                           ▼
                  agent_execution.log
```

## 🔄 Agent Workflow

The system follows an iterative agent loop.

### 1. Perception

The agent analyzes the input headline and identifies:

* Topic
* Intent
* Target audience
* Keywords
* Potential weaknesses

### 2. Reasoning

The agent decides how the headline can be improved based on:

* Clarity
* Engagement
* SEO relevance
* Power words
* Character length
* Target audience

### 3. Tool Execution

Deterministic Python tools are used for operations where exact results are required.

Examples:

```text
Character Count
Power Word Detection
SEO Keyword Fit
```

This avoids relying on the LLM for calculations that can be performed deterministically.

### 4. Generation

The LLM generates improved headline variations using the analysis and tool results.

### 5. Reflection

The generated headlines are evaluated against the requirements.

The reflection stage identifies weaknesses and provides feedback for the next iteration.

### 6. Memory

Reflection feedback is stored in **ChromaDB**.

Relevant previous critiques can later be retrieved using semantic similarity.

```text
Current headline
      ↓
Retrieve similar past critiques
      ↓
Combine with current analysis
      ↓
Improve generation
```

### 7. Iteration

The agent repeats the process until:

* The headline reaches the required quality
* The maximum number of iterations is reached
* The system detects a stuck loop
* The token budget is exhausted

## 📁 Project Structure

```text
headline-agent/
│
├── app.py
├── agent.py
├── memory_manager.py
├── tools.py
├── prompts.py
├── logger.py
├── guardrails.py
├── requirements.txt
├── .env
├── .gitignore
│
├── data/
│   └── chroma/
│
└── logs/
    └── agent_execution.log
```

## 📌 File Responsibilities

### `app.py`

Provides the Streamlit user interface.

It accepts the user's headline and displays generated variations, scores, feedback, and execution information.

### `agent.py`

Contains the main agent loop.

It coordinates:

```text
Perception
→ Reasoning
→ Tool execution
→ Generation
→ Reflection
→ Memory
→ Iteration
```

### `memory_manager.py`

Interfaces with ChromaDB.

Responsibilities:

* Store reflection feedback
* Generate/retrieve semantic memories
* Search for relevant previous critiques
* Provide historical feedback to future iterations

### `tools.py`

Contains deterministic Python functions.

Examples:

```python
character_count()
detect_power_words()
evaluate_keyword_fit()
```

These functions provide reliable evaluation results to the agent.

### `prompts.py`

Contains structured prompt templates for:

* Perception
* Reasoning
* Generation
* Reflection

Prompts enforce strict JSON response formats to make LLM outputs easier to parse and validate.

### `logger.py`

Produces structured JSON logs.

The logs can contain:

* Iteration number
* Input
* Output
* Latency in milliseconds
* Tool calls
* Errors
* Execution status

Example:

```json
{
  "iteration": 2,
  "latency_ms": 1240,
  "input": "AI is changing the world",
  "output": "10 AI Trends You Can't Ignore",
  "error": null
}
```

### `guardrails.py`

Provides production reliability mechanisms such as:

* API retries
* Exponential backoff
* JSON sanitization
* Token budget tracking
* Stuck-loop detection
* Maximum iteration limits

## 🧠 LLM Integration

The project uses **OpenRouter** as the LLM gateway.

The LLM client communicates with OpenRouter through an API and allows the application to use supported language models.

Basic flow:

```text
Python
  ↓
LLM Client
  ↓
OpenRouter API
  ↓
Selected LLM
  ↓
Structured Response
```

The API key should be stored in an environment variable.

```env
OPENROUTER_API_KEY=your_api_key_here
```

Never commit the API key to Git.

## 🗄️ ChromaDB

ChromaDB acts as the agent's semantic memory.

Reflection feedback can be stored as embeddings and later retrieved based on semantic similarity.

Example:

```text
Stored feedback:
"Headline is too generic. Use stronger and more specific wording."

Future input:
"AI is changing business"

Semantic search
       ↓
Relevant previous critique
       ↓
Agent uses feedback
```

This allows the agent to improve using knowledge from previous iterations.

## 🛠️ Deterministic Tools

The project intentionally separates **LLM reasoning** from **exact computation**.

For example, the LLM may suggest:

```text
"This headline is probably under 60 characters."
```

Instead of trusting that estimate, the Python tool calculates the exact value:

```python
len(headline)
```

This makes the evaluation more reliable.

## 🛡️ Production Guardrails

### API Retry

Temporary API failures are handled using exponential backoff.

```text
Attempt 1 → failure
      ↓
wait
      ↓
Attempt 2 → failure
      ↓
wait longer
      ↓
Attempt 3
```

### JSON Sanitization

LLM responses are validated and cleaned before being processed by the application.

### Token Budget

The system tracks token consumption and prevents the agent from exceeding the configured budget.

### Stuck Loop Detection

The system detects repeated actions or identical outputs.

Example:

```text
Iteration 1 → Headline A
Iteration 2 → Headline A
Iteration 3 → Headline A
Iteration 4 → Headline A
```

If the agent becomes repetitive, execution is stopped.

## 💻 Installation

Clone the repository:

```bash
git clone <repository-url>
cd headline-agent
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_api_key_here
```

## ▶️ Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in the browser.

## 🧪 Example

### Input

```text
AI is changing the world
```

### Possible generated variations

```text
1. 10 AI Trends That Are Changing the World
2. How AI Is Transforming the World in 2026
3. The AI Revolution: What Changes Next?
4. 7 Powerful Ways AI Is Reshaping Our Future
```

The system can then evaluate the generated headlines using:

```text
✓ Character count
✓ Power words
✓ SEO keyword fit
✓ Relevance
✓ Engagement
```

The reflection stage can determine whether another iteration is necessary.

## 📊 Example Agent Loop

```text
Input
  ↓
Perception
  ↓
Reasoning
  ↓
Generate Headlines
  ↓
Run Python Evaluation Tools
  ↓
Reflection
  ↓
Store Feedback in ChromaDB
  ↓
Retrieve Relevant Past Feedback
  ↓
Improve
  ↓
Quality Check
  │
  ├── Pass → Final Output
  │
  └── Fail → Next Iteration
```

## 🔐 Security

* Store API keys in environment variables
* Never commit `.env`
* Validate LLM responses before processing
* Limit maximum iterations
* Enforce token budgets
* Log errors without exposing sensitive credentials

Recommended `.gitignore`:

```text
.env
venv/
__pycache__/
data/chroma/
logs/
```

## 📦 Main Technologies

| Technology   | Purpose                          |
| ------------ | -------------------------------- |
| Python       | Core application and agent logic |
| Streamlit    | Web interface                    |
| OpenRouter   | LLM API gateway                  |
| LLM Client   | Communication with the LLM API   |
| ChromaDB     | Semantic agent memory            |
| JSON         | Structured LLM communication     |
| Python Tools | Deterministic evaluation         |
| Logging      | Execution monitoring             |

## 🎯 Goal

The goal of this project is to demonstrate how an LLM can be transformed from a simple **prompt → response** application into an **iterative, tool-using, memory-enabled AI agent**.

The system combines:

```text
LLM Reasoning
+
Deterministic Tools
+
Semantic Memory
+
Reflection
+
Production Guardrails
+
Observability
```

to produce more reliable and continuously improving headline variations.
