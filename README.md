# Incoming Request Processing Workflow

AI-powered prototype for classifying incoming requests and executing a branch-specific remediation workflow.

This repo now contains a complete Python demo for the brief in [task.md](task.md): input a request, classify it, branch into the right remediation path, produce a useful output for operations, and log the result for audit purposes.

## What it does

The app accepts an incoming request, classifies it into one of four branches, and then runs the matching remediation path:

- Complaint
- General Enquiry
- Service Request
- Escalation

Each branch produces a branch summary, a draft response or acknowledgement, routing or follow-up details, and a case-log entry that can be stored in SQLite through the built-in logger.

## What Was Done

- Replaced the original Anthropic-based setup with Groq-only model initialization in [workflow.py](workflow.py).
- Split model responsibilities by role so the workflow is easier to tune: classification, routine response generation, structured evaluation, and refinement.
- Reworked the workflow into a clear request-processing graph with one intake node, one classifier, and four branch-specific remediation paths.
- Updated the Streamlit app in [app.py](app.py) to call the Python workflow directly.
- Refreshed the sample requests in [sample_req.py](sample_req.py) so each branch can be demonstrated quickly.
- Added SQLite audit logging through [logger.py](logger.py).
- Rewrote this README to document setup, workflow design, model choice, and implementation trade-offs.

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r req.txt

# 3. Configure environment variables
# Create a .env file and add:
# GROQ_API_KEY=your_key_here

# 4. Run the demo
streamlit run app.py
```

## Deploying on Streamlit Community Cloud

Streamlit Cloud reads [requirements.txt](requirements.txt), so this repo includes that file alongside the local [req.txt](req.txt) copy.

1. Push the repo to GitHub.
2. Create a new Streamlit Community Cloud app from the repository.
3. Set the main file path to `app.py`.
4. Add `GROQ_API_KEY` in the Streamlit Cloud secrets panel.
5. Deploy and open the app URL Streamlit gives you.

If you are running locally, `.env` still works through `app.py`. On Streamlit Cloud, `app.py` reads `GROQ_API_KEY` from secrets and passes it into the workflow.

## Workflow Design

```text
Incoming request
    |
    v
Classify request with Groq LLM
    |
    v
Branch by request_type
    |
    +--> Complaint --------> Acknowledge -> Escalate -> Log
    |
    +--> General Enquiry --> Answer -> Resolve -> Log
    |
    +--> Service Request --> Route -> Confirm -> Log
    |
    +--> Escalation -------> Flag human -> Draft urgent ack -> Notify supervisor -> Log
```

## Design Choices

### Why a branching graph instead of one generic prompt

A single prompt would be simpler, but it would not satisfy the brief as well. The assignment asks for distinct remediation strategies, different downstream actions, and outputs that are easy for an operations team to read. A graph makes those outcomes explicit.

### Why conditional branching instead of parallel workflows

This problem is naturally single-path per request. Each incoming request should be classified once, then routed into one remediation path. Running the complaint, enquiry, service, and escalation flows in parallel would waste tokens, produce irrelevant outputs, and make the audit trail harder to read. Conditional branching keeps the decision point visible and ensures only the correct path executes.

### Why not an iterable or loop-based workflow

An iterable design makes sense when you must process many homogeneous items in sequence, such as a batch of emails or a list of rows. Here, each request is handled independently and should terminate once its branch finishes. Loops would only add complexity without improving the demo outcome.

### Why some branches are sequential

Within a branch, the steps need a dependency order: for example, a complaint should be acknowledged before it is escalated and logged, and a service request should be routed before the confirmation is drafted. That is why each branch is sequential after the initial conditional route.

### Why use multiple Groq models

Different tasks benefit from different model strengths. The classifier needs consistent structured output, routine response generation needs speed, and escalation wording benefits from a stronger reasoning model. Keeping those roles separate makes the system easier to adjust later.

### Why the audit log is in SQLite

SQLite is enough for the prototype because it provides simple persistence without introducing extra infrastructure. It also makes the demo easy to run locally and still gives a visible audit trail for the operations flow.

## Classification Logic

The workflow classifies each request into:

| Field | Values |
|---|---|
| `request_type` | complaint / general_enquiry / service_request / escalation |
| `urgency` | low / medium / high / critical |
| `sub_topic` | short topic summary such as fee dispute, rate question, transfer request, or legal threat |
| `client_sentiment` | neutral / frustrated / angry / distressed |

## Groq Model Roles

The workflow uses three Groq model roles so the implementation can be tuned easily:

- `classifier` for structured triage
- `generator` for routine customer-facing drafts
- `evaluator` for structured evaluation and stronger classification judgments
- `optimizer` for escalation wording and refinement-style prompts

The model names are centralized in [workflow.py](workflow.py), so you can swap them without rewriting the graph.

## Implementation Notes

- The main entrypoint for programmatic use is `process_request(raw_request)` in [workflow.py](workflow.py).
- The Streamlit UI calls the same Python function, so the demo and the code path are aligned.
- The logger writes to `data/request_log.db`, which is ignored in version control so local demo runs do not dirty the repo.
- The branch outputs are designed to be operations-friendly: classification label, urgency, routing target, follow-up action, draft response, and case log entry.

## Remediation Strategy

### Complaint
- Draft an acknowledgement
- Escalate to a senior handler
- Set a follow-up window
- Log the case with priority metadata

### General Enquiry
- Draft a direct answer
- Mark the request as resolved
- Log the outcome

### Service Request
- Route the request to the relevant operational team
- Draft a confirmation message
- Start the SLA timer and log the routing decision

### Escalation
- Flag the case for human review
- Draft a safe urgent acknowledgement
- Notify the supervisor path
- Log as pending human review

## Demo Inputs

Use the sample requests in [sample_req.py](sample_req.py) to demonstrate one example per branch.

## Tools Used

- LangGraph for branching orchestration
- LangChain Groq for LLM calls
- Pydantic for structured classification output
- Streamlit for the demo UI
- SQLite for the audit trail

## Files of Interest

- [workflow.py](workflow.py) - core graph, schema, prompts, and routing
- [app.py](app.py) - Streamlit demo UI
- [sample_req.py](sample_req.py) - example inputs for each branch
- [logger.py](logger.py) - SQLite audit log helper
- [req.txt](req.txt) - dependencies

## Example Outputs

For each processed request, the app displays:

- classification label and urgency
- branch-specific remediation steps
- draft response or acknowledgement
- routing or follow-up details
- a case-log entry suitable for audit purposes

## How to Test It

### Fast demo run

```bash
python demo.py
```

This runs all sample requests and prints the full branch output.

### Interactive UI

```bash
streamlit run app.py
```

Use the sample buttons or paste your own request.

### Programmatic test

```python
from workflow import process_request

result = process_request("Please transfer £50k to my investment account")
print(result)
```

## Commit Hygiene

Before you push, make sure your commit includes the source files only. The repo now ignores local environment files, Python caches, SQLite logs, and Streamlit state so your commits stay clean.
