from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

from app.chatbot.llm import GeminiChatProvider, OpenAIChatProvider, RuleBasedChatProvider
from app.chatbot.memory import ConversationMemory, MemoryTurn
from app.chatbot.prompts import PromptBuilder
from app.chatbot.query_parser import ChatIntent, QueryParser
from app.services.analytics_service import AnalyticsService
from app.services.nlp_service import NLPService


@dataclass(slots=True)
class ChatbotReply:
    conversation_id: str
    content: str
    confidence: float
    intent: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    chart_data: dict[str, Any] | None = None
    follow_up_questions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class AskYourDefectsEngine:
    def __init__(
        self,
        analytics_service: AnalyticsService,
        nlp_service: NLPService,
        memory: ConversationMemory,
        chat_provider: OpenAIChatProvider | RuleBasedChatProvider | GeminiChatProvider | None = None,
    ) -> None:
        self.analytics_service = analytics_service
        self.nlp_service = nlp_service
        self.memory = memory
        self.query_parser = QueryParser()
        self.prompt_builder = PromptBuilder()
        if chat_provider is not None:
            self.chat_provider = chat_provider
        else:
            self.chat_provider = GeminiChatProvider() if GeminiChatProvider().enabled else RuleBasedChatProvider()

    async def build_reply(self, user_id: str, conversation_id: str | None, query: str, context_filters: dict[str, Any] | None = None) -> ChatbotReply:
        conversation_id = conversation_id or self.memory.new_conversation_id()
        intent = self.query_parser.parse(query)
        memory_turns = await self.memory.load(conversation_id)
        analytics = await self._analytics_snapshot(intent)
        semantic_context = await self._semantic_context(query, intent, context_filters)

        system_prompt = self.prompt_builder.build_system_prompt(intent, analytics, semantic_context)
        user_prompt = self.prompt_builder.build_user_prompt(query, intent)
        response = await self.chat_provider.generate(system_prompt, user_prompt)
        content = self._compose_content(intent, query, analytics, semantic_context, response)
        sources = self._build_sources(semantic_context, analytics, memory_turns)
        chart_data = self._build_chart_data(intent, analytics, semantic_context)

        reply = ChatbotReply(
            conversation_id=conversation_id,
            content=content,
            confidence=self._confidence(intent, semantic_context, analytics),
            intent=intent.name,
            sources=sources,
            chart_data=chart_data,
            follow_up_questions=self._follow_ups(intent, analytics),
            metadata={"intent": intent.name, "entities": intent.entities},
        )

        await self.memory.append(conversation_id, user_id, "user", query, context_filters=context_filters)
        await self.memory.append(
            conversation_id,
            user_id,
            "assistant",
            content,
            sources=sources,
            confidence=reply.confidence,
            context_filters=context_filters,
        )
        return reply

    async def stream_reply(self, user_id: str, conversation_id: str | None, query: str, context_filters: dict[str, Any] | None = None) -> AsyncIterator[str]:
        reply = await self.build_reply(user_id, conversation_id, query, context_filters)
        payload = {
            "event": "final",
            "conversation_id": reply.conversation_id,
            "content": reply.content,
            "sources": reply.sources,
            "chart_data": reply.chart_data,
            "intent": reply.intent,
            "confidence": reply.confidence,
            "follow_up_questions": reply.follow_up_questions,
            "done": True,
        }
        for token in reply.content.split():
            yield f"data: {json.dumps({'event': 'delta', 'conversation_id': reply.conversation_id, 'delta': token + ' '})}\n\n"
        yield f"data: {json.dumps(payload)}\n\n"

    async def history(self, conversation_id: str) -> list[MemoryTurn]:
        return await self.memory.load(conversation_id)

    async def suggestions(self, query: str) -> list[str]:
        intent = self.query_parser.parse(query)
        if intent.name == "backlog":
            return [
                "Which assignment group has the highest backlog?",
                "Show unresolved defects older than 7 days.",
                "Which queues are increasing fastest this week?",
            ]
        if intent.name == "sla_risk":
            return [
                "Show high-risk SLA tickets.",
                "What is the breach probability by assignment group?",
                "Which tickets need escalation now?",
            ]
        return [
            "Which assignment group has highest backlog?",
            "Show unresolved SCM defects older than 7 days.",
            "Why are finance defects increasing?",
        ]

    async def _semantic_context(self, query: str, intent: ChatIntent, context_filters: dict[str, Any] | None) -> list[dict[str, Any]]:
        if intent.name not in {"semantic_search", "backlog", "trend", "sla_risk", "kpi", "management_insight"}:
            return []
        return self.nlp_service.semantic_search(query, top_k=5)

    async def _analytics_snapshot(self, intent: ChatIntent) -> dict[str, Any]:
        backlog = await self.analytics_service.by_assignment_group()
        priority = await self.analytics_service.by_priority()
        status = await self.analytics_service.by_status()
        top_backlog = sorted(backlog.items(), key=lambda item: item[1], reverse=True)[:5]
        return {
            "backlog_by_assignment_group": top_backlog,
            "priority_breakdown": priority,
            "status_breakdown": status,
        }

    def _compose_content(self, intent: ChatIntent, query: str, analytics: dict[str, Any], semantic_context: list[dict[str, Any]], fallback: str) -> str:
        if intent.name == "backlog":
            top_group = analytics.get("backlog_by_assignment_group", [])[:1]
            group_text = f"The highest backlog is in **{top_group[0][0]}** with {top_group[0][1]} defects." if top_group else "Backlog data is not available."
            return (
                f"{group_text}\n\n"
                f"Recommended next step: re-balance work into the busiest queue and review aging items older than {intent.days or 7} days.\n\n"
                f"Related defects: {self._format_context(semantic_context)}"
            )
        if intent.name == "sla_risk":
            return (
                "### High-risk SLA tickets\n"
                f"I found {len(semantic_context)} relevant defect matches. Focus on Critical and High priority tickets with high aging and frequent reassignments.\n\n"
                f"{self._format_context(semantic_context)}"
            )
        if intent.name == "trend":
            return (
                "### Trend explanation\n"
                "The increase is usually driven by a combination of backlog accumulation, repeated reassignments, and work notes that indicate unresolved dependencies.\n\n"
                "Recommended action: isolate the fastest-growing assignment group, check recent releases, and compare new incidents against the last 7 days of semantic matches."
            )
        if intent.name == "management_insight":
            return (
                "### Management insight\n"
                "The current portfolio is dominated by a small number of assignment groups and the biggest risk is concentration of open work in the same queues.\n\n"
                "- Prioritize the top backlog groups first.\n- Review SLA exposure daily.\n- Reduce reassignments to improve cycle time."
            )
        return fallback or "I analyzed the request against defect analytics and semantic search context, but I need more detail to answer precisely."

    def _format_context(self, items: list[dict[str, Any]]) -> str:
        if not items:
            return "No directly related defects were found."
        lines = [f"- {item.get('ticket_number') or item.get('ticket_id')}: {item.get('title')} ({item.get('score', 0):.2f})" for item in items[:5]]
        return "\n".join(lines)

    def _build_sources(self, semantic_context: list[dict[str, Any]], analytics: dict[str, Any], memory_turns: list[MemoryTurn]) -> list[dict[str, Any]]:
        sources: list[dict[str, Any]] = []
        for item in semantic_context[:5]:
            sources.append({"type": "semantic_search", "ticket_id": item.get("ticket_id"), "ticket_number": item.get("ticket_number"), "title": item.get("title"), "score": item.get("score")})
        sources.append({"type": "analytics", "payload": analytics})
        if memory_turns:
            sources.append({"type": "memory", "turns": len(memory_turns)})
        return sources

    def _build_chart_data(self, intent: ChatIntent, analytics: dict[str, Any], semantic_context: list[dict[str, Any]]) -> dict[str, Any] | None:
        if intent.name in {"backlog", "kpi", "management_insight"}:
            return {"type": "bar", "title": "Backlog by assignment group", "data": [{"name": name, "value": value} for name, value in analytics.get("backlog_by_assignment_group", [])], "xKey": "name", "yKey": "value"}
        if intent.name == "sla_risk":
            return {"type": "bar", "title": "Semantic match risk", "data": [{"name": item.get("ticket_number") or item.get("ticket_id"), "value": round(float(item.get("score", 0)) * 100)} for item in semantic_context[:5]], "xKey": "name", "yKey": "value"}
        return None

    def _confidence(self, intent: ChatIntent, semantic_context: list[dict[str, Any]], analytics: dict[str, Any]) -> float:
        score = 0.55 + (0.08 if semantic_context else 0.0) + (0.1 if analytics else 0.0) + (intent.confidence * 0.2)
        return round(min(score, 0.97), 2)

    def _follow_ups(self, intent: ChatIntent, analytics: dict[str, Any]) -> list[str]:
        if intent.name == "backlog":
            return ["Show unresolved SCM defects older than 7 days.", "Which assignment group has highest backlog?", "Why are finance defects increasing?"]
        if intent.name == "trend":
            return ["Show high-risk SLA tickets.", "Which defects are being reassigned most often?", "What changed in the last 7 days?"]
        return ["Show high-risk SLA tickets.", "Which assignment group has highest backlog?", "Show unresolved defects older than 7 days."]
