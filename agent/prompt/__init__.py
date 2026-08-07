"""
Agent Prompt Module - 系统提示词构建模块
"""

from .builder import PromptBuilder, build_agent_system_prompt
from .soul import (
    SOUL_CORE_FILENAME,
    SOUL_FILENAME,
    build_soul_section,
    is_soul_path,
    load_soul_core_text,
    load_soul_text,
    use_full_soul,
)
from .workspace import ensure_workspace, load_context_files

__all__ = [
    'PromptBuilder',
    'build_agent_system_prompt',
    'ensure_workspace',
    'load_context_files',
    'SOUL_FILENAME',
    'SOUL_CORE_FILENAME',
    'build_soul_section',
    'is_soul_path',
    'load_soul_text',
    'load_soul_core_text',
    'use_full_soul',
]
