from app.agents.coder_agent import CoderAgent
from app.agents.debugger_agent import DebuggerAgent
from app.agents.architect_agent import ArchitectAgent
from app.agents.reviewer_agent import ReviewerAgent
from app.agents.documenter_agent import DocumenterAgent
from app.agents.tester_agent import TesterAgent
from app.agents.refactorer_agent import RefactorerAgent
from app.agents.explainer_agent import ExplainerAgent

AGENT_REGISTRY = {
    "coder": CoderAgent,
    "debugger": DebuggerAgent,
    "architect": ArchitectAgent,
    "reviewer": ReviewerAgent,
    "documenter": DocumenterAgent,
    "tester": TesterAgent,
    "refactorer": RefactorerAgent,
    "explainer": ExplainerAgent,
}
