"""Tools package — core always loaded; heavy tools registered only via ToolManager.

Heavy tools (browser, vision, web_search, MCP) are NOT in CORE_TOOL_EXPORTS so
``import agent.tools`` / ``ToolManager`` discovery does not pull Playwright.
"""

from agent.tools.base_tool import BaseTool
from agent.tools.tool_manager import ToolManager

# ---- Core tools (always available; small import graph) ----
from agent.tools.read.read import Read
from agent.tools.write.write import Write
from agent.tools.edit.edit import Edit
from agent.tools.bash.bash import Bash
from agent.tools.ls.ls import Ls
from agent.tools.send.send import Send
from agent.tools.search_files.search_files import SearchFiles
from agent.tools.memory.memory_search import MemorySearchTool
from agent.tools.memory.memory_get import MemoryGetTool
from agent.tools.evolution_undo.evolution_undo import EvolutionUndoTool
from agent.tools.subagent.subagent import SubagentTool

# Soft-optional core product tools
EnvConfig = None
SchedulerTool = None
WebFetch = None

try:
    from agent.tools.env_config.env_config import EnvConfig  # noqa: F401
except Exception:
    pass

try:
    from agent.tools.scheduler.scheduler_tool import SchedulerTool  # noqa: F401
except Exception:
    pass

try:
    from agent.tools.web_fetch.web_fetch import WebFetch  # noqa: F401
except Exception:
    pass


# ---- Lazy / heavy tools (import path, class name) ----
# NOT listed in CORE_TOOL_EXPORTS — ToolManager loads them separately.
LAZY_TOOL_SPECS = {
    "WebSearch": ("agent.tools.web_search.web_search", "WebSearch"),
    "Vision": ("agent.tools.vision.vision", "Vision"),
    "BrowserTool": ("agent.tools.browser.browser_tool", "BrowserTool"),
    "McpTool": ("agent.tools.mcp.mcp_tool", "McpTool"),
}

_lazy_cache = {}


def load_lazy_tool_class(class_name: str):
    """Import a heavy tool class once. Returns None if unavailable."""
    if class_name in _lazy_cache:
        return _lazy_cache[class_name]
    spec = LAZY_TOOL_SPECS.get(class_name)
    if not spec:
        _lazy_cache[class_name] = None
        return None
    module_path, attr = spec
    try:
        import importlib
        mod = importlib.import_module(module_path)
        cls = getattr(mod, attr, None)
        _lazy_cache[class_name] = cls
        return cls
    except Exception as e:
        from common.log import logger
        logger.debug(f"[Tools] Lazy tool {class_name} not loaded: {e}")
        _lazy_cache[class_name] = None
        return None


# Names ToolManager may discover via getattr on this package (core only).
# Lazy names intentionally excluded so hasattr/getattr cannot eager-import them.
CORE_TOOL_EXPORTS = [
    "Read",
    "Write",
    "Edit",
    "Bash",
    "Ls",
    "Send",
    "SearchFiles",
    "MemorySearchTool",
    "MemoryGetTool",
    "EvolutionUndoTool",
    "SubagentTool",
    "EnvConfig",
    "SchedulerTool",
    "WebFetch",
]

# Public package API (includes lazy names for documentation only — they are
# not auto-discovered; access via load_lazy_tool_class).
__all__ = [
    "BaseTool",
    "ToolManager",
    *CORE_TOOL_EXPORTS,
    "LAZY_TOOL_SPECS",
    "CORE_TOOL_EXPORTS",
    "load_lazy_tool_class",
]
