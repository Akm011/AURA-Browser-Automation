from __future__ import annotations

from typing import TypedDict

from aura_models.config import AuraSettings, get_settings
from aura_models.planning import ExecutionPlan, ParsedIntent
from langgraph.graph import END, START, StateGraph

from aura_planner.execution_planner import ExecutionPlanner
from aura_planner.intent import IntentParser
from aura_planner.request_analyzer import OpenAIRequestAnalyzer


class PlannerState(TypedDict):
    request: str
    intent: ParsedIntent | None
    plan: ExecutionPlan | None
    error: str | None


class PlannerAgent:
    """LangGraph agent that converts natural language into an execution plan."""

    def __init__(
        self,
        intent_parser: IntentParser | None = None,
        execution_planner: ExecutionPlanner | None = None,
        request_analyzer: OpenAIRequestAnalyzer | None = None,
        settings: AuraSettings | None = None,
    ) -> None:
        self.intent_parser = intent_parser or IntentParser()
        settings = settings or get_settings()
        self.request_analyzer = request_analyzer or OpenAIRequestAnalyzer(
            settings=settings,
            fallback_parser=self.intent_parser,
        )
        self.execution_planner = execution_planner or ExecutionPlanner()
        self._graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(PlannerState)
        graph.add_node("parse_intent", self._parse_intent)
        graph.add_node("plan_execution", self._plan_execution)
        graph.add_edge(START, "parse_intent")
        graph.add_edge("parse_intent", "plan_execution")
        graph.add_edge("plan_execution", END)
        return graph.compile()

    def plan(self, request: str) -> ExecutionPlan:
        result = self._graph.invoke(
            {
                "request": request,
                "intent": None,
                "plan": None,
                "error": None,
            }
        )
        if result.get("error"):
            raise ValueError(result["error"])
        plan = result.get("plan")
        if plan is None:
            raise ValueError("Planner did not produce an execution plan")
        return plan

    def _parse_intent(self, state: PlannerState) -> PlannerState:
        try:
            intent = self.request_analyzer.analyze(state["request"])
            return {**state, "intent": intent, "error": None}
        except Exception as exc:
            return {**state, "intent": None, "error": str(exc)}

    def _plan_execution(self, state: PlannerState) -> PlannerState:
        intent = state.get("intent")
        if intent is None:
            return {**state, "plan": None, "error": state.get("error") or "Intent parsing failed"}

        try:
            plan = self.execution_planner.plan(intent)
            if not plan.steps:
                return {**state, "plan": None, "error": "No executable steps generated"}
            return {**state, "plan": plan, "error": None}
        except Exception as exc:
            return {**state, "plan": None, "error": str(exc)}
