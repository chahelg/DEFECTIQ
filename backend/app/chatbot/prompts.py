"""Prompt engineering for Ask Your Defects."""

from __future__ import annotations

from typing import Any

from app.chatbot.query_parser import ChatIntent


class PromptBuilder:
    def build_system_prompt(self, intent: ChatIntent, analytics: dict[str, Any], context: list[dict[str, Any]]) -> str:
        sections = [
            "You are Ask Your Defects, an enterprise defect intelligence copilot for DefectIQ AI.",
            "Answer in concise executive language when the user asks for management insight, and in operational detail when they ask for defect triage.",
            "Use the provided analytics and semantic retrieval context. Never invent ticket numbers or metrics.",
            f"Detected intent: {intent.name}",
        ]
        if analytics:
            sections.append(f"Analytics snapshot: {analytics}")
        if context:
            sections.append(f"Relevant defect context: {context}")
        sections.append(
            "When answering trends or backlog questions, explicitly mention the driver, impact, and recommended next action."
        )
        return "\n\n".join(sections)

    def build_user_prompt(self, query: str, intent: ChatIntent) -> str:
        return (
            f"User question: {query}\n"
            f"Intent: {intent.name}\n"
            f"Parsed entities: {intent.entities}\n"
            "Provide a markdown response with bullet points when useful."
        )
