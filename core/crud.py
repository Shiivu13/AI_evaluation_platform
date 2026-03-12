from typing import List, Dict, Any
from core.db import get_cursor

def create_experiment(name: str, description: str = "") -> int:
    with get_cursor() as cursor:
        cursor.execute("INSERT INTO experiments (name, description) VALUES (?, ?)", (name, description))
        return cursor.lastrowid

def get_all_experiments() -> List[Dict[str, Any]]:
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM experiments ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

def create_variant(experiment_id: int, name: str, prompt_template: str, model_name: str, temperature: float = 0.7) -> int:
    with get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO variants (experiment_id, name, prompt_template, model_name, temperature) 
            VALUES (?, ?, ?, ?, ?)
        """, (experiment_id, name, prompt_template, model_name, temperature))
        return cursor.lastrowid

def get_variants_for_experiment(experiment_id: int) -> List[Dict[str, Any]]:
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM variants WHERE experiment_id = ? ORDER BY created_at DESC", (experiment_id,))
        return [dict(row) for row in cursor.fetchall()]

def add_test_case(experiment_id: int, input_data: str, expected_output: str = "", context: str = "") -> int:
    with get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO test_cases (experiment_id, input_data, expected_output, context) 
            VALUES (?, ?, ?, ?)
        """, (experiment_id, input_data, expected_output, context))
        return cursor.lastrowid

def get_test_cases_for_experiment(experiment_id: int) -> List[Dict[str, Any]]:
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM test_cases WHERE experiment_id = ?", (experiment_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_evaluation_runs_for_variant(variant_id: int) -> List[Dict[str, Any]]:
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM evaluation_runs WHERE variant_id = ? ORDER BY created_at DESC", (variant_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_results_for_run(run_id: int) -> List[Dict[str, Any]]:
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM evaluation_results WHERE run_id = ?", (run_id,))
        return [dict(row) for row in cursor.fetchall()]
