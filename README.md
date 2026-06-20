# Incoming Request Processing Workflow

Submission-ready prototype for classifying incoming requests and executing branch-specific remediation workflows.

## 1. Project Overview

This project processes a request end-to-end:

1. Accept incoming request text.
2. Classify request type and urgency.
3. Route to a type-specific remediation branch.
4. Generate operational outputs and log results.

Supported request types:

- Complaint
- General Enquiry
- Service Request
- Escalation

## 2. Setup Instructions

### Local Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r req.txt
```

Create a `.env` file in the repo root:

```env
GROQ_API_KEY=your_key_here
```

Run the app:

```bash
streamlit run app.py
```

### Streamlit Community Cloud

1. Push the repository to GitHub.
2. Create a Streamlit Community Cloud app from this repo.
3. Set main file path to `app.py`.
4. Add `GROQ_API_KEY` in Streamlit secrets.
5. Deploy.

## 3. Workflow Design Notes

### Processing Flow

```text
Incoming request
  -> Classify (type, urgency, sentiment, sub-topic)
  -> Conditional branch by request_type
     -> complaint: acknowledge -> escalate -> priority log -> 2-hour follow-up
     -> general_enquiry: generate response -> log resolved
     -> service_request: extract and route -> confirm and log
     -> escalation: flag human review -> draft urgent ack -> notify supervisor -> pause auto-resolution
```

### Design Decisions

- Graph-based branching is used to enforce distinct remediation sequences.
- Each request follows one branch only.
- Branch steps are sequential where state from previous steps is required.
- SQLite logging provides an audit trail without external infrastructure.

### Classification Output Schema

The classifier returns:

- `request_type`: complaint, general_enquiry, service_request, escalation
- `urgency`: low, medium, high, critical
- `sub_topic`: concise operational topic
- `client_sentiment`: neutral, frustrated, angry, distressed
- `reasoning` and `branch_summary`

## 4. Remediation Strategy Definitions

### Complaint

1. Acknowledge receipt.
2. Escalate to senior handler.
3. Log case with priority flag.
4. Set 2-hour follow-up reminder.

### General Enquiry

1. Classify sub-topic.
2. Generate AI response.
3. Send/prepare response.
4. Log as resolved.

### Service Request

1. Extract required details.
2. Route to relevant department.
3. Generate confirmation to requester.
4. Set SLA timer and log.

### Escalation

1. Flag for immediate human review.
2. Draft urgent acknowledgement.
3. Notify supervisor.
4. Pause auto-resolution until review completes.

## 5. Repository Structure

- `workflow.py`: LangGraph workflow, prompts, routing, and remediation nodes
- `app.py`: Streamlit UI for processing and dashboard views
- `logger.py`: SQLite audit logging helpers
- `sample_req.py`: sample inputs for each request branch
- `demo.py`: command-line run across sample requests
- `req.txt` and `requirements.txt`: dependencies

## 6. How to Run and Validate

### Demo Run

```bash
python demo.py
```

### Syntax Check

```bash
python -m py_compile workflow.py app.py demo.py logger.py
```

## 7. Expected Output Per Request

Each processed request returns:

- classification label and urgency
- branch-specific steps taken
- draft response or acknowledgement
- routing and follow-up action
- case log entry for audit trail
