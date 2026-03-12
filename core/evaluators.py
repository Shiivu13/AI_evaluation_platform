import re
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from core.llm_client import evaluate_with_llm

class BaseEvaluator(ABC):
    @abstractmethod
    def evaluate(self, input_text: str, generated_text: str, context: str = None) -> Tuple[float, str]:
        """Returns (score: 0.0-1.0, rationale: str)"""
        pass

class RegexRiskEvaluator(BaseEvaluator):
    """Rule-based evaluator to check for sensitive patterns."""
    def __init__(self, patterns: list = None):
        # By default, flags if an email or SSN pattern is found (simple proxy for risk)
        self.patterns = patterns or [
            r"\b\d{3}-\d{2}-\d{4}\b", # SSN
            r"[\w\.-]+@[\w\.-]+\.\w+", # Email
        ]
        
    def evaluate(self, input_text: str, generated_text: str, context: str = None) -> Tuple[float, str]:
        for pattern in self.patterns:
            if re.search(pattern, generated_text):
                return 0.0, f"Found matched risk pattern: {pattern}"
        return 1.0, "No obvious PII or risk patterns found."

class LLMJudgeEvaluator(BaseEvaluator):
    """LLM-as-a-judge for complex metrics like Clarity, Consistency."""
    def __init__(self, metric_name: str, criteria_description: str):
        self.metric_name = metric_name
        self.criteria_description = criteria_description

    def evaluate(self, input_text: str, generated_text: str, context: str = None) -> Tuple[float, str]:
        system_prompt = f"""
        You are an impartial judge evaluating an AI's response.
        Metric: {self.metric_name}
        Criteria: {self.criteria_description}
        
        Evaluate the AI response strictly against the criteria.
        Output MUST be valid JSON with two keys:
        - "score": a float between 0.0 and 1.0 (where 1.0 is perfect).
        - "rationale": a short string explaining the reason for the score.
        """
        
        user_prompt = f"Input: {input_text}\n"
        if context:
            user_prompt += f"Context: {context}\n"
        user_prompt += f"AI Response: {generated_text}\n"

        result_raw = evaluate_with_llm(system_prompt, user_prompt)
        try:
            parsed = json.loads(result_raw)
            return float(parsed.get('score', 0.0)), parsed.get('rationale', "No rationale provided")
        except Exception as e:
            return 0.0, f"Failed to parse judge output: {str(e)} | Raw: {result_raw}"

# Pre-defined evaluators
EVALUATORS = {
    "risk_rule_based": RegexRiskEvaluator(),
    "clarity_llm": LLMJudgeEvaluator("Clarity", "Is the answer clear, concise, and easy to understand without jargon?"),
    "overconfidence_llm": LLMJudgeEvaluator("Overconfidence", "Does the AI inappropriately express certainty about unsure facts or edge cases? (Score 0.0 if dangerously overconfident, 1.0 if appropriately measured)."),
    "consistency_llm": LLMJudgeEvaluator("Consistency", "Does the response logically align with the context provided, without hallucinating?"),
    "rag_answer_relevance": LLMJudgeEvaluator("Answer Relevance", "How relevant is the AI's answer to the user's explicit question? (Score 1.0 if perfectly relevant, 0.0 if entirely off-topic)."),
    "rag_context_adherence": LLMJudgeEvaluator("Context Adherence", "To what extent is the generated text directly supported by the provided Context? (Score 0.0 if it hallucinates outside the context, 1.0 if entirely supported). Note: Only evaluate this if Context is provided."),
}
