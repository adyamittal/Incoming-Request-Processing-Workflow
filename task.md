# Incoming Request Processing Workflow

## Objective
Design and develop an AI-powered prototype that automatically receives, classifies, and processes incoming requests — such as customer queries, complaints, or service requests — and executes a defined remediation workflow for each classification type[cite: 6]. The solution should demonstrate multi-step branching logic, where each request type triggers a distinct sequence of actions rather than a single generic response[cite: 6].

## Context
You are working with an operations team that receives a continuous stream of incoming requests from customers or clients via email, web forms, or a shared inbox[cite: 6]. Each request varies in type and urgency — a billing dispute requires a very different response path from a general enquiry or an escalation from a dissatisfied customer[cite: 6]. Currently, a team member manually reads each request, determines what it is asking for, and decides what to do next[cite: 6]. This process is slow, inconsistent, and heavily dependent on individual judgment[cite: 6].

The client wants a proof-of-concept that shows how AI can not only classify each incoming request, but also execute the correct multi-step remediation workflow for that classification — including generating an appropriate response, routing to the right team, setting a follow-up action, and logging the outcome[cite: 6]. The system should handle at least three distinct request types, each with its own branching logic and remediation strategy[cite: 6].

Your goal is to design and demonstrate a working prototype that handles this end-to-end within 5 days[cite: 6].

---

## Requirements and Deliverables

| Deliverable | Description |
| :--- | :--- |
| **Core Functionality** | Build a prototype that: (1) accepts an incoming request via form, file upload, or simulated inbox; (2) uses AI to classify the request by type and urgency; (3) branches into a type-specific remediation workflow; and (4) executes at least two downstream steps per branch — such as generating a tailored response, routing to a team, setting a follow-up flag, or escalating the case[cite: 6]. |
| **Classification & Remediation Design** | The prototype must handle a minimum of three distinct request types, each with its own defined remediation strategy[cite: 6]. Examples of request types and their workflows are provided below — candidates may adapt these or define their own, provided the branching logic is clearly justified[cite: 6]. |
| **Optional Enhancement** | Candidates may explore batch processing of multiple requests, a processing log or audit trail showing classification decisions and actions taken, a summary dashboard showing request volumes by type and status, or an escalation override mechanism for edge cases the AI is uncertain about[cite: 6]. |
| **Output Format** | For each request processed, the prototype should produce: a classification label and urgency level; a branch-specific action summary showing which remediation steps were triggered; and any generated outputs such as a draft response, a routing notification, or a follow-up task[cite: 6]. Outputs should be clearly legible for an operations team[cite: 6]. |
| **Documentation** | A one-page README describing the workflow design, the classification logic, the remediation strategy for each request type, tools used, and one end-to-end example per branch type[cite: 6]. |

---

## Example Classification Types and Remediation Strategies
The following are illustrative examples. Candidates are encouraged to adapt these to a context of their choosing — such as a healthcare provider, a financial services firm, a telecom operator, or a general BPO environment[cite: 6].

| Request Type | Urgency | Remediation Steps | Expected Output |
| :--- | :--- | :--- | :--- |
| **Complaint** | High | 1. Acknowledge receipt<br>2. Escalate to senior handler<br>3. Log case with priority flag<br>4. Set 2-hour follow-up reminder | Escalation notification + draft acknowledgement + case log entry[cite: 6] |
| **General Enquiry** | Low | 1. Classify sub-topic<br>2. Generate AI response from knowledge base<br>3. Send response<br>4. Log as resolved | Auto-generated response + resolved status log[cite: 6] |
| **Service Request** | Medium | 1. Extract required details<br>2. Route to relevant department<br>3. Generate confirmation to requester<br>4. Set SLA timer | Routing notification + confirmation message + SLA flag[cite: 6] |
| **Escalation / Urgent** | Critical | 1. Immediately flag for human review<br>2. Draft urgent acknowledgement<br>3. Notify supervisor<br>4. Pause auto-resolution | Supervisor alert + draft acknowledgement + human-in-the-loop flag[cite: 6] |

Candidates are free to define their own request types and remediation strategies provided they cover a minimum of three distinct branches, each with at least two downstream steps[cite: 6].

Candidates are free to use any publicly available dataset or generate a suitable dataset using AI tools. No proprietary or client data is required[cite: 6].

---

## Suggested Tools and Platforms

### Pro-Code Track
*   Python with an LLM API (OpenAI, Claude, or similar) for classification and response generation[cite: 6]
*   Streamlit or Gradio for UI; n8n Cloud or Retool Workflow for multi-step orchestration[cite: 6]
*   Optional: a simple SQLite or Google Sheet as a case log / audit trail[cite: 6]

### No-Code Track
*   n8n or Zapier with conditional branching nodes and an AI classification step[cite: 6]
*   Optional: Google Forms or Typeform as the request intake source; Slack or Gmail for notifications and responses[cite: 6]

Feel free to use the tools you enjoy working with. We do not cover subscription or license costs — please explore free trials or open-source options[cite: 6].

---

## Submission Format
Each candidate must submit three components within 5 days of receiving the brief[cite: 6].

### 1. Working Demo
*   Demonstrate the prototype end-to-end: incoming request → classification → branch-specific remediation → outputs[cite: 6]
*   Accepted formats: shared workflow link, hosted application, or screen recording (maximum 3 minutes)[cite: 6]
*   The demo must show at least three different request types being processed, each triggering a distinct remediation branch[cite: 6]

### 2. Five-Slide Summary Deck (Fixed Structure)

| Slide | Title | Description |
| :--- | :--- | :--- |
| **1** | PROBLEM UNDERSTANDING AND OBJECTIVE | Summarize your understanding of the brief and the problem statement[cite: 6]. |
| **2** | SOLUTION ARCHITECTURE AND DESIGN FLOW | Present your workflow or system design. Include a diagram showing the classification logic and each remediation branch[cite: 6]. |
| **3** | IMPLEMENTATION HIGHLIGHTS | Highlight technical decisions, branching logic, and AI reasoning. Include screenshots or concise code snippets[cite: 6]. |
| **4** | CHALLENGES AND LEARNINGS | Discuss key technical or design challenges, trade-offs made, and key takeaways from the build[cite: 6]. |
| **5** | DEMO SUMMARY AND NEXT STEPS | Present your final solution, include demo or repository links, and describe potential enhancements if given more time[cite: 6]. |

Format: PowerPoint or PDF (five slides maximum)[cite: 6].

### 3. Supporting Assets
*   README file with setup instructions, workflow design notes, and remediation strategy definitions[cite: 6]
*   Sample input requests (one per branch type) and corresponding output screenshots or logs[cite: 6]
*   Optional: shared workflow export (JSON) or GitHub repository[cite: 6]

---

## Evaluation Rubric

| Evaluation Focus | Weight |
| :--- | :--- |
| Classification accuracy and branching logic quality; appropriateness and completeness of each remediation strategy | 40%[cite: 6] |
| End-to-end reliability across all branches; clarity and usefulness of outputs for an operations team | 30%[cite: 6] |
| Communication clarity and presentation structure | 15%[cite: 6] |
| Creativity in remediation design, edge case handling, and reflection shown in documentation | 15%[cite: 6] |

---

## Deadline and Submission
*   **Time Limit:** 5 days from the time this brief is issued[cite: 6]
*   **Submission Package:** demo link or short video recording, five-slide summary deck (PDF or PPT), README or supporting documentation[cite: 6]
*   Submissions should be delivered to the specified email address before midnight of the 5th day[cite: 6]