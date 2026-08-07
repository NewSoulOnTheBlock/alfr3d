"""Tools package — core always loaded; heavy tools registered lazily.

Tier A lean: browser, vision, web_search, MCP are not imported until
ToolManager asks for them (or create_tool is called by name).
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

# Soft-optional but still "core product" — import with quiet fallback
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
# Registered by name only; ToolManager imports on first use.
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


# Module-level names for backward compatibility (may be None until first load)
def __getattr__(name: str):
    if name in LAZY_TOOL_SPECS:
        return load_lazy_tool_class(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Classes ToolManager should discover from this package (core only).
# Lazy tools are appended by ToolManager after optional import.
__all__ = [
    "BaseTool",
    "ToolManager",
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
    # Lazy names listed so getattr / documentation stay stable
    "WebSearch",
    "Vision",
    "BrowserTool",
    "McpTool",
    "LAZY_TOOL_SPECS",
    "load_lazy_tool_class",
]
