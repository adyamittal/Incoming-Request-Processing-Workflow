"""Incoming request processing workflow for the brief in task.md."""

from __future__ import annotations

import operator
import os
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

GROQ_MODELS = {
    "classifier": "llama-3.1-8b-instant",
    "generator": "llama-3.1-8b-instant",
    "evaluator": "llama-3.3-70b-versatile",
    "optimizer": "openai/gpt-oss-20b",
}


def _groq(model_name: str) -> ChatGroq:
    return ChatGroq(model=model_name, temperature=0, api_key=os.environ["GROQ_API_KEY"])


classifier_llm = _groq(GROQ_MODELS["classifier"])
generator_llm = _groq(GROQ_MODELS["generator"])
evaluator_llm = _groq(GROQ_MODELS["evaluator"])
optimizer_llm = _groq(GROQ_MODELS["optimizer"])


class ClassificationSchema(BaseModel):
    request_type: Literal["complaint", "general_enquiry", "service_request", "escalation"] = Field(
        description="Primary request branch"
    )
    urgency: Literal["low", "medium", "high", "critical"] = Field(description="Urgency level")
    sub_topic: str = Field(description="Short operational topic summary")
    client_sentiment: Literal["neutral", "frustrated", "angry", "distressed"] = Field(description="Detected sentiment")
    reasoning: str = Field(description="One sentence explanation")
    branch_summary: str = Field(description="Operations-friendly branch summary")


class RequestState(TypedDict, total=False):
    raw_request: str
    request_type: Literal["complaint", "general_enquiry", "service_request", "escalation"]
    urgency: Literal["low", "medium", "high", "critical"]
    sub_topic: str
    client_sentiment: Literal["neutral", "frustrated", "angry", "distressed"]
    classification_reasoning: str
    branch_summary: str
    draft_response: str
    routing_target: str
    follow_up_action: str
    remediation_summary: str
    case_log_entry: str
    status: str
    steps_taken: Annotated[list[str], operator.add]


def _case_log(state: RequestState) -> str:
    return (
        f"TYPE={state.get('request_type', '')} | SUB_TOPIC={state.get('sub_topic', '')} | "
        f"URGENCY={state.get('urgency', '')} | SENTIMENT={state.get('client_sentiment', '')} | "
        f"ROUTED_TO={state.get('routing_target', '')} | FOLLOW_UP={state.get('follow_up_action', '')} | "
        f"STATUS={state.get('status', 'processed')}"
    )


def classify_request(state: RequestState):
    structured = classifier_llm.with_structured_output(ClassificationSchema)
    prompt = (
        "You are triaging incoming customer requests.\n\n"
        "Classify the request using these branches:\n"
        "- complaint: dissatisfaction, billing dispute, poor service, error, or feedback\n"
        "- general_enquiry: questions about accounts, products, policies, or how-to guidance\n"
        "- service_request: requests that require an action such as a transfer, update, reset, or document handling\n"
        "- escalation: legal language, regulatory threats, reputational risk, or immediate human review\n\n"
        "Return a concise result with a sub-topic, one-sentence reasoning, and a branch_summary that an operations team can use.\n\n"
        f"Request:\n{state['raw_request']}\n"
    )
    result = structured.invoke(prompt)
    return {
        "request_type": result.request_type,
        "urgency": result.urgency,
        "sub_topic": result.sub_topic,
        "client_sentiment": result.client_sentiment,
        "classification_reasoning": result.reasoning,
        "branch_summary": result.branch_summary,
        "steps_taken": [f"[CLASSIFY] {result.request_type} | {result.urgency} | {result.sub_topic}"],
    }


def route_request(state: RequestState) -> Literal["complaint_branch", "enquiry_branch", "service_branch", "escalation_branch"]:
    return {
        "complaint": "complaint_branch",
        "general_enquiry": "enquiry_branch",
        "service_request": "service_branch",
        "escalation": "escalation_branch",
    }[state["request_type"]]


def complaint_acknowledge(state: RequestState):
    draft = generator_llm.invoke([
        SystemMessage(content="You write concise, empathetic support acknowledgements."),
        HumanMessage(content=(
            "Draft a 3-4 sentence acknowledgement.\n\n"
            f"Topic: {state['sub_topic']}\n"
            f"Sentiment: {state['client_sentiment']}\n"
            f"Urgency: {state['urgency']}\n\n"
            "Requirements:\n"
            "- acknowledge the concern\n"
            "- say the case is being reviewed\n"
            "- do not admit fault or promise a final outcome\n\n"
            f"Request:\n{state['raw_request']}\n"
        )),
    ]).content
    return {
        "draft_response": draft,
        "routing_target": "Senior Support Lead" if state["urgency"] in ("low", "medium") else "Senior Support Lead + Compliance",
        "follow_up_action": "Review and respond within 1 business day" if state["urgency"] in ("low", "medium") else "Priority review within 2 hours",
        "status": "in_review",
        "steps_taken": ["[COMPLAINT] Step 1: Drafted acknowledgement"],
    }


def complaint_escalate(state: RequestState):
    return {
        "routing_target": "Head of Customer Operations + Compliance",
        "follow_up_action": "Escalate to senior handler and assign priority follow-up",
        "remediation_summary": "Complaint acknowledged and escalated for review.",
        "status": "escalated",
        "steps_taken": ["[COMPLAINT] Step 2: Routed to senior handler"],
    }


def complaint_log(state: RequestState):
    return {"case_log_entry": _case_log(state), "steps_taken": ["[COMPLAINT] Step 3: Logged with priority flag"]}


def enquiry_generate_response(state: RequestState):
    draft = generator_llm.invoke([
        SystemMessage(content="You write clear, concise customer support answers."),
        HumanMessage(content=(
            "Answer this enquiry in 4-6 sentences.\n\n"
            f"Topic: {state['sub_topic']}\n"
            f"Request:\n{state['raw_request']}\n\n"
            "If account-specific details are required, direct the user to their relationship manager.\n"
        )),
    ]).content
    return {
        "draft_response": draft,
        "routing_target": "Self-service / Customer Support",
        "follow_up_action": "No follow-up required unless additional account details are needed",
        "status": "resolved",
        "steps_taken": ["[ENQUIRY] Step 1: Generated response"],
    }


def enquiry_log_resolved(state: RequestState):
    return {
        "remediation_summary": "Enquiry answered and marked resolved.",
        "case_log_entry": _case_log(state),
        "steps_taken": ["[ENQUIRY] Step 2: Logged as resolved"],
    }


def service_extract_and_route(state: RequestState):
    text = f"{state['sub_topic']} {state['raw_request']}".lower()
    routing_map = {
        "transfer": "Payments Operations",
        "transaction": "Payments Operations",
        "mandate": "Account Administration",
        "update": "Account Administration",
        "onboarding": "Client Onboarding",
        "document": "KYC / Document Processing",
        "reset": "Account Support",
    }
    routing_target = "Operations Team"
    for keyword, team in routing_map.items():
        if keyword in text:
            routing_target = team
            break
    return {
        "routing_target": routing_target,
        "follow_up_action": "Set SLA timer for 1 business day",
        "status": "queued",
        "steps_taken": [f"[SERVICE] Step 1: Routed to {routing_target}"],
    }


def service_confirm_and_log(state: RequestState):
    draft = generator_llm.invoke([
        SystemMessage(content="You write brief operational confirmations."),
        HumanMessage(content=(
            "Draft a 2-3 sentence confirmation.\n\n"
            f"Topic: {state['sub_topic']}\n"
            f"Routing target: {state['routing_target']}\n"
            f"Request:\n{state['raw_request']}\n\n"
            "Mention that the request has been routed and is being processed within the standard SLA.\n"
        )),
    ]).content
    return {
        "draft_response": draft,
        "remediation_summary": f"Request routed to {state['routing_target']} and SLA started.",
        "case_log_entry": _case_log(state),
        "steps_taken": ["[SERVICE] Step 2: Confirmation drafted and SLA set"],
    }


def escalation_flag_human(state: RequestState):
    return {
        "routing_target": "Supervisor + Compliance + Legal Review",
        "follow_up_action": "Pause automation and request human review immediately",
        "status": "human_review_required",
        "steps_taken": ["[ESCALATION] Step 1: Human review required"],
    }


def escalation_draft_urgent_ack(state: RequestState):
    draft = optimizer_llm.invoke([
        SystemMessage(content="You write safe escalation acknowledgements."),
        HumanMessage(content=(
            "Draft a cautious urgent acknowledgement.\n\n"
            f"Topic: {state['sub_topic']}\n"
            f"Sentiment: {state['client_sentiment']}\n"
            f"Request:\n{state['raw_request']}\n\n"
            "Requirements:\n"
            "- 2 to 3 sentences\n"
            "- no admissions\n"
            "- no promises beyond acknowledging receipt and urgency\n"
        )),
    ]).content
    return {"draft_response": draft, "steps_taken": ["[ESCALATION] Step 2: Urgent acknowledgement drafted"]}


def escalation_notify_supervisor(state: RequestState):
    return {
        "remediation_summary": "Escalation flagged for immediate review and supervisor notification.",
        "case_log_entry": _case_log(state),
        "steps_taken": ["[ESCALATION] Step 3: Supervisor notified"],
    }


def build_graph():
    graph = StateGraph(RequestState)
    graph.add_node("classify", classify_request)
    graph.add_node("complaint_acknowledge", complaint_acknowledge)
    graph.add_node("complaint_escalate", complaint_escalate)
    graph.add_node("complaint_log", complaint_log)
    graph.add_node("enquiry_generate_response", enquiry_generate_response)
    graph.add_node("enquiry_log_resolved", enquiry_log_resolved)
    graph.add_node("service_extract_and_route", service_extract_and_route)
    graph.add_node("service_confirm_and_log", service_confirm_and_log)
    graph.add_node("escalation_flag_human", escalation_flag_human)
    graph.add_node("escalation_draft_urgent_ack", escalation_draft_urgent_ack)
    graph.add_node("escalation_notify_supervisor", escalation_notify_supervisor)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        route_request,
        {
            "complaint_branch": "complaint_acknowledge",
            "enquiry_branch": "enquiry_generate_response",
            "service_branch": "service_extract_and_route",
            "escalation_branch": "escalation_flag_human",
        },
    )

    graph.add_edge("complaint_acknowledge", "complaint_escalate")
    graph.add_edge("complaint_escalate", "complaint_log")
    graph.add_edge("complaint_log", END)

    graph.add_edge("enquiry_generate_response", "enquiry_log_resolved")
    graph.add_edge("enquiry_log_resolved", END)

    graph.add_edge("service_extract_and_route", "service_confirm_and_log")
    graph.add_edge("service_confirm_and_log", END)

    graph.add_edge("escalation_flag_human", "escalation_draft_urgent_ack")
    graph.add_edge("escalation_draft_urgent_ack", "escalation_notify_supervisor")
    graph.add_edge("escalation_notify_supervisor", END)
    return graph.compile()


workflow = build_graph()


def process_request(raw_request: str):
    return workflow.invoke({"raw_request": raw_request, "steps_taken": []})