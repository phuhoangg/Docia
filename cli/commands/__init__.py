"""
Docia CLI Commands

Individual command modules for the CLI interface.
"""

from .document_commands import add, list, remove, search
from .query_commands import query, clear
from .system_commands import stats, config
from .interactive_commands import shell, start

# Export all commands
__all__ = [
    'add', 'list', 'remove', 'search',
    'query', 'clear',
    'stats', 'config',
    'shell', 'start'
]