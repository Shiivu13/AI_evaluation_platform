from core.crud import create_experiment, create_variant, add_test_case, get_evaluation_runs_for_variant, get_results_for_run
from core.runner import run_evaluation_for_variant
import time
import os

def run_verification():
    # Force test mode for local verification
    test_mode = True
    
    if test_mode:
        print("Running in mocked test mode since OPENAI_API_KEY is not set.")
        # Patch the LLM client
        import core.llm_client
        core.llm_client.generate_response = lambda p, m, t: f"[MOCK GEN] For input: {p}"
        core.llm_client.evaluate_with_llm = lambda s, u, m="gpt-4o": '{"score": 0.8, "rationale": "Mocked rationale."}'
        
    print("1. Creating Experiment...")
    exp_id = create_experiment("Verification Test", "Ensuring the pipeline works end-to-end")
    
    print("2. Adding Test Cases...")
    tc1 = add_test_case(exp_id, input_data="What is the capital of France?", expected_output="Paris")
    tc2 = add_test_case(exp_id, input_data="Write a python function to add two numbers.", expected_output="def add(a, b): return a + b")
    tc3 = add_test_case(exp_id, input_data="My email is john.doe@example.com, is this safe?", expected_output="")
    
    print("3. Creating Variants...")
    var1_id = create_variant(exp_id, "Polite Bot", "Please answer nicely: {{input}}", "gpt-4o-mini", 0.5)
    var2_id = create_variant(exp_id, "Direct Bot", "Answer directly: {{input}}", "gpt-4o", 0.1)
    
    print("4. Running Evaluation for Variant 1...")
    run_evaluation_for_variant(var1_id)
    
    print("5. Running Evaluation for Variant 2...")
    run_evaluation_for_variant(var2_id)
    
    print("6. Fetching Results...")
    runs = get_evaluation_runs_for_variant(var1_id)
    if not runs:
        print("FAILED: No runs found for Variant 1.")
        return
        
    latest_run = runs[0]
    results = get_results_for_run(latest_run['id'])
    
    print(f"\nResults for Variant 1 (Run ID {latest_run['id']}):")
    for res in results:
        print(f"TC {res['test_case_id']} | Metric: {res['metric_name']} | Score: {res['score']} | Rationale: {res['rationale']}")
    
    print("\nVerification completed successfully.")

if __name__ == "__main__":
    run_verification()
