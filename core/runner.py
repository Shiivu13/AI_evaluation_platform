from typing import List, Dict, Any
from core.db import get_cursor
from core.llm_client import generate_response
from core.evaluators import EVALUATORS
from core.models import EvaluationRun, EvaluationResult

def run_evaluation_for_variant(variant_id: int):
    """
    Executes the evaluation pipeline for a given variant against all test cases for its experiment.
    """
    with get_cursor() as cursor:
        # Get variant details
        cursor.execute("SELECT * FROM variants WHERE id = ?", (variant_id,))
        variant = cursor.fetchone()
        if not variant:
            print(f"Variant {variant_id} not found.")
            return

        # Create a new run record
        cursor.execute("INSERT INTO evaluation_runs (variant_id, status) VALUES (?, 'running')", (variant_id,))
        run_id = cursor.lastrowid
        
        # Get test cases for this experiment
        cursor.execute("SELECT * FROM test_cases WHERE experiment_id = ?", (variant['experiment_id'],))
        test_cases = cursor.fetchall()
        
        try:
            for tc in test_cases:
                input_data = tc['input_data']
                context = tc['context']
                
                # 1. Generate the response
                # Replace a placeholder like {{input}} in the template with actual data
                prompt = variant['prompt_template'].replace('{{input}}', input_data)
                if context:
                    prompt = prompt.replace('{{context}}', context)
                    
                generated_text = generate_response(
                    prompt=prompt, 
                    model=variant['model_name'], 
                    temperature=variant['temperature']
                )
                
                # 2. Evaluate the response
                for eval_name, evaluator in EVALUATORS.items():
                    score, rationale = evaluator.evaluate(input_text=input_data, generated_text=generated_text, context=context)
                    
                    # 3. Save result
                    cursor.execute('''
                        INSERT INTO evaluation_results 
                        (run_id, test_case_id, metric_name, score, rationale, evaluator_type)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (run_id, tc['id'], eval_name, score, rationale, type(evaluator).__name__))
            
            # Mark run complete
            cursor.execute("UPDATE evaluation_runs SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?", (run_id,))
            print(f"Run {run_id} completed successfully.")
            
        except Exception as e:
            # Mark run failed
            cursor.execute("UPDATE evaluation_runs SET status = 'failed', completed_at = CURRENT_TIMESTAMP WHERE id = ?", (run_id,))
            print(f"Run {run_id} failed: {e}")
