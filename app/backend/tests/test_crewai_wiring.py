"""CrewAI Agent and Crew offline wiring test (Item 12).
Builds the real CrewAI Agent and Crew and runs kickoff with a fake LLM
at the LLM-call level (no network), testing the real parsing path.
"""
import os
import json
from unittest.mock import patch
import pytest

from crewai import Agent, Task, Crew
from crewai.llms.providers.openai.completion import OpenAICompletion


def test_crewai_agent_and_crew_kickoff_offline():
    """Builds the real CrewAI Agent and Crew and runs kickoff with a fake LLM
    at the LLM-call level (no network), testing the real parsing path.
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

    with patch.object(OpenAICompletion, "call", return_value=fake_completion_response):
        agent = Agent(
            role="Payroll Intent Classifier",
            goal="Classify incoming employee requests accurately",
            backstory="Expert payroll assistant responsible for intent classification",
            verbose=False,
            allow_delegation=False,
        )
        task = Task(
            description="Classify: Explain my September pay.",
            expected_output="JSON formatted classification",
            agent=agent,
        )
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=False,
        )

        result = crew.kickoff()
        result_str = str(result)
        assert result_str, "CrewAI kickoff returned empty result"
        assert "explain_salary" in result_str or fake_json in result_str
