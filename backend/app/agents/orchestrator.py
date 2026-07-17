import time
import logging
from typing import Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from app.agents.registry import AGENT_REGISTRY

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    request: str
    context: dict[str, Any] | None
    agents_to_run: list[str]
    results: dict[str, dict]
    errors: dict[str, str]
    execution_plan: list[dict[str, str]]
    memory_context: str
    reviewed: bool
    formatted_output: str


def _build_graph_for_agents(agent_keys: list[str]) -> StateGraph:
    workflow = StateGraph(AgentState)

    async def route_intent(state: AgentState) -> dict:
        req = state["request"].lower()
        agents = state["agents_to_run"]
        if not agents:
            if any(w in req for w in ["debug", "bug", "fix", "error", "issue"]):
                agents = ["debugger", "coder", "reviewer"]
            elif any(w in req for w in ["architect", "design", "structure", "architecture"]):
                agents = ["architect", "reviewer", "documenter"]
            elif any(w in req for w in ["test", "unit test", "integration test"]):
                agents = ["tester", "coder", "reviewer"]
            elif any(w in req for w in ["refactor", "optimize", "improve"]):
                agents = ["refactorer", "coder", "reviewer"]
            elif any(w in req for w in ["explain", "document", "documentation"]):
                agents = ["explainer", "documenter"]
            else:
                agents = ["coder", "reviewer"]
            agents = [a for a in agents if a in AGENT_REGISTRY]
        plan = [{"agent": a, "action": AGENT_REGISTRY[a]().description} for a in agents]
        return {"agents_to_run": agents, "execution_plan": plan}

    async def build_plan(state: AgentState) -> dict:
        logger.info(f"Planning execution for: {state['agents_to_run']}")
        return {}

    async def build_context(state: AgentState) -> dict:
        ctx = state.get("context") or {}
        ctx_str = "\n".join(f"{k}: {v}" for k, v in ctx.items()) if ctx else ""
        return {"memory_context": ctx_str}

    async def review_output(state: AgentState) -> dict:
        results = state.get("results", {})
        for key, result in results.items():
            if result.get("status") == "success" and not result.get("output"):
                results[key] = {**result, "status": "error", "output": None}
                errors = state.get("errors", {})
                errors[key] = "Empty output generated"
                return {"results": results, "errors": errors, "reviewed": True}
        return {"reviewed": True}

    async def format_response(state: AgentState) -> dict:
        results = state.get("results", {})
        parts = []
        for key, result in results.items():
            output = result.get("output", "")
            if output:
                parts.append(f"### {key}\n{output}")
        return {"formatted_output": "\n\n".join(parts) if parts else "No output generated"}

    workflow.add_node("intent_router", route_intent)
    workflow.add_node("planner", build_plan)
    workflow.add_node("context_builder", build_context)
    workflow.add_node("reviewer", review_output)
    workflow.add_node("response_formatter", format_response)

    workflow.add_edge(START, "intent_router")
    workflow.add_edge("intent_router", "planner")
    workflow.add_edge("planner", "context_builder")

    prev = "context_builder"
    for key in agent_keys:
        node_name = f"agent_{key}"
        def make_node(k: str):
            async def run_agent(state: AgentState) -> dict:
                agent_cls = AGENT_REGISTRY.get(k)
                if not agent_cls:
                    return {"errors": {**state.get("errors", {}), k: f"Unknown agent: {k}"}}
                agent = agent_cls()
                try:
                    start = time.monotonic()
                    result = await agent.execute(state["request"], state.get("context"))
                    elapsed = int((time.monotonic() - start) * 1000)
                    return {
                        "results": {
                            **state.get("results", {}),
                            k: {
                                "output": result.get("content", ""),
                                "tokens_used": result.get("tokens_used", 0),
                                "execution_time_ms": elapsed,
                                "status": "success",
                            },
                        }
                    }
                except Exception as e:
                    logger.error(f"Agent {k} failed: {e}")
                    return {"errors": {**state.get("errors", {}), k: str(e)}}
            return run_agent
        workflow.add_node(node_name, make_node(key))
        workflow.add_edge(prev, node_name)
        prev = node_name

    workflow.add_edge(prev, "reviewer")
    workflow.add_edge("reviewer", "response_formatter")
    workflow.add_edge("response_formatter", END)

    return workflow.compile()


class AgentOrchestrator:
    def __init__(self):
        self._graphs: dict[str, StateGraph] = {}

    def _get_graph(self, agent_keys: tuple[str, ...]) -> StateGraph:
        key = ",".join(sorted(agent_keys)) if agent_keys else "__default__"
        if key not in self._graphs:
            keys = list(agent_keys) if agent_keys else list(AGENT_REGISTRY.keys())
            self._graphs[key] = _build_graph_for_agents(keys)
        return self._graphs[key]

    async def execute_single(self, request: str, context: dict | None = None, agent_key: str = "coder") -> dict:
        agent_cls = AGENT_REGISTRY.get(agent_key)
        if not agent_cls:
            return {
                "agent_name": agent_key,
                "status": "error",
                "output": None,
                "error": f"Unknown agent: {agent_key}",
                "execution_time_ms": 0,
                "tokens_used": 0,
            }
        agent = agent_cls()
        start = time.monotonic()
        try:
            result = await agent.execute(request, context)
            elapsed = int((time.monotonic() - start) * 1000)
            return {
                "agent_name": agent_key,
                "status": "success",
                "output": result.get("content", ""),
                "error": None,
                "execution_time_ms": elapsed,
                "tokens_used": result.get("tokens_used", 0),
            }
        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            return {
                "agent_name": agent_key,
                "status": "error",
                "output": None,
                "error": str(e),
                "execution_time_ms": elapsed,
                "tokens_used": 0,
            }

    async def orchestrate(self, request: str, context: dict | None = None, agents: list[str] | None = None) -> dict:
        valid_keys = [k for k in (agents or []) if k in AGENT_REGISTRY]
        if not valid_keys:
            valid_keys = ["architect", "coder", "reviewer"]
            valid_keys = [k for k in valid_keys if k in AGENT_REGISTRY]
        if not valid_keys:
            return {
                "request": request,
                "agents_used": [],
                "execution_plan": [],
                "results": [],
                "merged_output": {"content": ""},
                "total_time_ms": 0,
            }

        start_total = time.monotonic()
        graph = self._get_graph(tuple(valid_keys))
        initial_state: AgentState = {
            "request": request,
            "context": context,
            "agents_to_run": valid_keys,
            "results": {},
            "errors": {},
            "execution_plan": [],
            "memory_context": "",
            "reviewed": False,
            "formatted_output": "",
        }

        final_state = await graph.ainvoke(initial_state)

        results_list = []
        for key in valid_keys:
            res = final_state.get("results", {}).get(key, {})
            err = final_state.get("errors", {}).get(key)
            results_list.append({
                "agent_name": key,
                "status": "error" if err else "success",
                "output": res.get("output"),
                "error": err,
                "execution_time_ms": res.get("execution_time_ms", 0),
                "tokens_used": res.get("tokens_used", 0) if not err else 0,
            })

        total_time = int((time.monotonic() - start_total) * 1000)
        for r in results_list:
            if r["execution_time_ms"] == 0:
                r["execution_time_ms"] = total_time // len(results_list) if results_list else 0

        merged = "\n\n".join([f"### {r['agent_name']}\n{r['output']}" for r in results_list if r.get("output")])
        execution_plan = [{"agent": k, "action": AGENT_REGISTRY[k]().description} for k in valid_keys if k in AGENT_REGISTRY]

        return {
            "request": request,
            "agents_used": valid_keys,
            "execution_plan": execution_plan,
            "results": results_list,
            "merged_output": {"content": merged},
            "total_time_ms": total_time,
        }


agent_orchestrator = AgentOrchestrator()
