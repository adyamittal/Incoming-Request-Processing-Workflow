"""Streamlit demo for the incoming request workflow."""

import json
import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

try:
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:
    pass

if "GROQ_API_KEY" not in os.environ:
    try:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

if not os.getenv("GROQ_API_KEY"):
    st.error(
        "Missing GROQ_API_KEY. Add it in Streamlit Cloud secrets for deployment, or set it in your local environment/.env file."
    )
    st.stop()

from logger import fetch_all_logs, fetch_summary, log_request
from sample_req import SAMPLES
from workflow import process_request


st.set_page_config(page_title="Request Processing - Ops Demo", layout="wide")

URGENCY_COLOR = {
    "low": "#2ecc71",
    "medium": "#f39c12",
    "high": "#e74c3c",
    "critical": "#8e44ad",
}

TYPE_ICON = {
    "complaint": "[COMPLAINT]",
    "general_enquiry": "[ENQUIRY]",
    "service_request": "[SERVICE]",
    "escalation": "[ESCALATION]",
}


st.title("Incoming Request Processor")
st.caption("Groq-powered triage and remediation workflow for the task brief")

tab_process, tab_log, tab_dashboard = st.tabs(["Process Request", "Audit Log", "Dashboard"])

with tab_process:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("Incoming Request")
        st.caption("Load a sample request:")
        sample_cols = st.columns(4)
        labels = {
            "complaint": "Complaint",
            "general_enquiry": "Enquiry",
            "service_request": "Service Request",
            "escalation": "Escalation",
        }
        for index, (key, label) in enumerate(labels.items()):
            if sample_cols[index].button(label, use_container_width=True):
                st.session_state["request_text"] = SAMPLES[key]

        request_text = st.text_area(
            "Paste or type the request below:",
            value=st.session_state.get("request_text", ""),
            height=220,
            placeholder="Type a client message or click a sample above...",
        )

        run = st.button("Process Request", type="primary", use_container_width=True)

    with right:
        st.subheader("Processing Output")

        if run and request_text.strip():
            with st.spinner("Running workflow..."):
                result = process_request(request_text)

            request_id = log_request({"raw_request": request_text, **result})
            urgency = result.get("urgency", "")
            request_type = result.get("request_type", "")
            color = URGENCY_COLOR.get(urgency, "#95a5a6")
            icon = TYPE_ICON.get(request_type, "[REQUEST]")

            st.markdown(
                f"""
<div style="border-left: 5px solid {color}; padding: 12px 16px; border-radius: 4px; background: #f8f9fa; margin-bottom: 12px;">
    <strong style="font-size:1.1em">{icon} {request_type.replace('_',' ').title()}</strong>
    &nbsp;&nbsp;<span style="background:{color}; color:white; border-radius:12px; padding:2px 10px; font-size:0.85em">{urgency.upper()}</span>
    <br><small style="color:#666">ID: {request_id} &nbsp;|&nbsp; Sub-topic: {result.get('sub_topic','-')} &nbsp;|&nbsp; Sentiment: {result.get('client_sentiment','-')}</small>
    <br><small style="color:#555; margin-top:4px; display:block"><em>{result.get('classification_reasoning','')}</em></small>
</div>
""",
                unsafe_allow_html=True,
            )

            st.markdown("**Remediation Steps Taken**")
            for step in result.get("steps_taken", []):
                st.markdown(f"- {step}")

            with st.expander("Draft Response / Acknowledgement", expanded=True):
                st.write(result.get("draft_response", "-"))

            with st.expander("Routing and Follow-up"):
                st.markdown(f"**Routed to:** {result.get('routing_target', '-')}")
                st.markdown(f"**Follow-up action:** {result.get('follow_up_action', '-')}")
                st.markdown(f"**Summary:** {result.get('remediation_summary', '-')}")

            with st.expander("Case Log Entry"):
                st.code(result.get("case_log_entry", "-"))

        elif run:
            st.warning("Please enter a request before processing.")
        else:
            st.info("Submit a request on the left to see the workflow output here.")

with tab_log:
    st.subheader("Audit Trail")
    logs = fetch_all_logs()
    if not logs:
        st.info("No requests processed yet.")
    else:
        for entry in logs:
            urgency = entry.get("urgency", "")
            request_type = entry.get("request_type", "")
            icon = TYPE_ICON.get(request_type, "[REQUEST]")
            with st.expander(f"{icon} [{entry['id']}] {entry['timestamp']} - {request_type.replace('_',' ').title()} | {urgency.upper()}"):
                cols = st.columns(2)
                with cols[0]:
                    st.markdown("**Raw Request**")
                    st.caption(entry["raw_request"][:300] + ("..." if len(entry["raw_request"]) > 300 else ""))
                    st.markdown(f"**Sub-topic:** {entry['sub_topic']}")
                    st.markdown(f"**Sentiment:** {entry['client_sentiment']}")
                    st.markdown(f"**Routing:** {entry['routing_target']}")
                with cols[1]:
                    st.markdown("**Steps Taken**")
                    steps = json.loads(entry.get("steps_taken") or "[]")
                    for step in steps:
                        st.markdown(f"- {step}")
                    st.markdown(f"**Follow-up:** {entry['follow_up_action']}")

with tab_dashboard:
    st.subheader("Request Volume Dashboard")
    summary = fetch_summary()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**By Request Type**")
        type_data = summary.get("by_type", {})
        if type_data:
            df_type = pd.DataFrame(list(type_data.items()), columns=["Type", "Count"]).sort_values("Count", ascending=False)
            st.bar_chart(df_type.set_index("Type"))
        else:
            st.info("No data yet.")
    with col2:
        st.markdown("**By Urgency Level**")
        urgency_data = summary.get("by_urgency", {})
        if urgency_data:
            df_urgency = pd.DataFrame(list(urgency_data.items()), columns=["Urgency", "Count"])
            order = ["critical", "high", "medium", "low"]
            df_urgency["Urgency"] = pd.Categorical(df_urgency["Urgency"], categories=order, ordered=True)
            df_urgency = df_urgency.sort_values("Urgency")
            st.bar_chart(df_urgency.set_index("Urgency"))
        else:
            st.info("No data yet.")