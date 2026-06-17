"""Quick demo of the workflow on sample requests."""

import json
from workflow import process_request
from sample_req import SAMPLES

print("=" * 80)
print("INCOMING REQUEST PROCESSING WORKFLOW DEMO")
print("=" * 80)

for branch_type, request_text in SAMPLES.items():
    print(f"\n{'='*80}")
    print(f"BRANCH: {branch_type.upper()}")
    print(f"{'='*80}\n")
    
    print(f"INPUT REQUEST:\n{request_text}\n")
    print("-" * 80)
    
    result = process_request(request_text)
    
    print(f"\nCLASSIFICATION:")
    print(f"  Type:       {result.get('request_type')}")
    print(f"  Urgency:    {result.get('urgency')}")
    print(f"  Sub-topic:  {result.get('sub_topic')}")
    print(f"  Sentiment:  {result.get('client_sentiment')}")
    print(f"  Reasoning:  {result.get('classification_reasoning')}")
    
    print(f"\nREMEDIATION STEPS:")
    for i, step in enumerate(result.get("steps_taken", []), 1):
        print(f"  {i}. {step}")
    
    print(f"\nDRAFT RESPONSE:")
    print(f"  {result.get('draft_response', '—')}")
    
    print(f"\nROUTING & FOLLOW-UP:")
    print(f"  Routed to:     {result.get('routing_target', '—')}")
    print(f"  Follow-up:     {result.get('follow_up_action', '—')}")
    print(f"  Summary:       {result.get('remediation_summary', '—')}")
    
    print(f"\nCASE LOG ENTRY:")
    print(f"  {result.get('case_log_entry', '—')}")

print(f"\n{'='*80}")
print("DEMO COMPLETE")
print(f"{'='*80}\n")
