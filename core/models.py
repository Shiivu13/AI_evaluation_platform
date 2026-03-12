from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class TestCase(BaseModel):
    id: Optional[int] = None
    input_data: str
    expected_output: Optional[str] = None
    context: Optional[str] = None  # Background info if needed

class Variant(BaseModel):
    id: Optional[int] = None
    experiment_id: int
    name: str
    prompt_template: str
    model_name: str
    temperature: float = 0.7
    created_at: datetime = Field(default_factory=datetime.now)

class Experiment(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class EvaluationResult(BaseModel):
    id: Optional[int] = None
    run_id: int
    test_case_id: int
    metric_name: str
    score: float
    rationale: Optional[str] = None
    evaluator_type: str # 'rule_based' or 'llm_as_a_judge'

class EvaluationRun(BaseModel):
    id: Optional[int] = None
    variant_id: int
    status: str = "pending" # pending, running, completed, failed
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
