"""CrewAI Agent and Crew offline wiring test (Item 4).
Uses our own agents.py factories and our classifier output parser
through the ai_crew path; fakes only the LLM call.
"""
import json
from unittest.mock import patch
import pytest

from crewai import LLM, Task
from crewai.llms.providers.openai.completion import OpenAICompletion

from app.backend.ai.agents import (
    create_classifier_agent,
    create_retrieval_agent,
    create_drafting_agent,
    create_escalation_agent,
    validate_classifier_output,
    ClassifierOutput,
)
from app.backend.ai.crew import PayrollAICrew
from app.backend.auth import USERS


def test_crewai_agent_and_crew_kickoff_offline():
    """Builds the real CrewAI Agent and Crew using agents.py factories
    and runs kickoff and parsing through the ai_crew path with a fake LLM
    at the LLM-call level (no network).
    """
    fake_json = json.dumps({
        "intent": "explain_salary",
        "scenario_num": 9,
        "entities": {"employee_name": "Neha Gupta", "month": "September 2026"},
        "confidence": 0.95,
        "is_prompt_injection": False,
        "clarification_needed": False
    })
    fake_completion_response = f"Final Answer: {fake_json}"

    # Verify agent factories from agents.py
    llm = LLM(model="gpt-4o-mini", api_key="fake-test-key")
    classifier_agent = create_classifier_agent(llm)
    assert classifier_agent.role == "HCM One Payroll Intent Classifier"
    assert classifier_agent.allow_delegation is False

    retrieval_agent = create_retrieval_agent(llm)
    assert retrieval_agent.role == "Deterministic Payroll Data Retriever"

    drafting_agent = create_drafting_agent(llm)
    assert drafting_agent.role == "HCM One Slot-Based Communications Drafter"

    escalation_agent = create_escalation_agent(llm)
    assert escalation_agent.role == "Governance and Human Action Router"

    # Wiring test through the ai_crew path faking only OpenAICompletion.call
    with patch.object(OpenAICompletion, "call", return_value=fake_completion_response):
        task = Task(
            description="Classify: Explain my September pay.",
            expected_output="JSON formatted classification",
            agent=classifier_agent,
        )
        ai_crew = PayrollAICrew(llm=llm)
        user = USERS.get("USER-E05")

        classifier_res = ai_crew._execute_classifier(
            task=task,
            message="Explain my September pay",
            role="Employee",
            user=user,
            context={"user_id": "USER-E05"}
        )

        assert isinstance(classifier_res, ClassifierOutput)
        assert classifier_res.intent == "explain_salary"
        assert classifier_res.scenario_num == 9
        assert classifier_res.entities.get("employee_name") == "Neha Gupta"
        assert classifier_res.entities.get("employee_id") == "E05"
        assert classifier_res.confidence == 0.95
        assert classifier_res.is_prompt_injection is False
        assert classifier_res.clarification_needed is False
