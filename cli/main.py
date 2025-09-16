#!/usr/bin/env python3
"""
Docia CLI - VisionLM Document Intelligence Tool

A command-line interface for Docia's intelligent document analysis capabilities.
"""

import asyncio
import json
import os
import sys
import click
from pathlib import Path
from typing import Optional, List
from datetime import datetime

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    env_paths = [
        Path.cwd() / ".env",  # Current directory
        Path(__file__).parent.parent / ".env",  # Project root
        Path(__file__).parent.parent / "docia" / ".env",  # Package directory
    ]

    for env_path in env_paths:
        if env_path.exists():
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
            except UnicodeDecodeError:
                # Fallback to different encoding if utf-8 fails
                with open(env_path, 'r', encoding='latin-1') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()

# Load environment variables at module import
load_env_file()

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from docia import Docia, DociaConfig, create_docia
from docia.models.document import Document, QueryMode
from docia.models.agent import ConversationMessage
from .commands import add, list, remove, search, query, clear, stats, config
from .commands.interactive_commands import shell, start


class DociaCLI:
    """Docia CLI Application"""

    def __init__(self):
        self.docia: Optional[Docia] = None
        self.config_file = Path.home() / ".docia" / "config.json"
        self.conversation_history: List[ConversationMessage] = []

    def initialize_docia(self, config_path: Optional[str] = None) -> Docia:
        """Initialize Docia with configuration"""
        try:
            if config_path and Path(config_path).exists():
                # Load from config file
                config = self._load_config_from_file(config_path)
            else:
                # Use environment variables or defaults
                config = DociaConfig.from_env()

            self.docia = Docia(config=config)
            return self.docia
        except Exception as e:
            click.echo(f"ERROR: Failed to initialize Docia: {e}", err=True)
            sys.exit(1)

    def _load_config_from_file(self, config_path: str) -> DociaConfig:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        return DociaConfig.from_dict(config_data)

    def _save_config_to_file(self, config: DociaConfig):
        """Save configuration to file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        config_dict = {
            'provider': config.provider,
            'model': config.model,
            'vision_model': config.vision_model,
            'storage_type': config.storage_type,
            'local_storage_path': config.local_storage_path,
            'max_agent_iterations': config.max_agent_iterations,
            'max_pages_per_task': config.max_pages_per_task,
            'max_tasks_per_plan': config.max_tasks_per_plan,
            'vision_detail': config.vision_detail,
            'jpeg_quality': config.jpeg_quality,
            'log_level': config.log_level
        }

        with open(self.config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)

    def _format_document_info(self, doc: Document) -> str:
        """Format document information for display"""
        pages_info = f"{len(doc.pages)} pages" if doc.pages else "0 pages"
        status_icon = "OK:" if doc.status.value == "completed" else "PROCESSING:"
        return f"{status_icon} {doc.name} ({doc.id}) - {pages_info}"

    def _progress_callback(self, event_type: str, data):
        """Callback for tracking task progress"""
        if event_type == 'plan_created':
            click.echo(f"PLAN: Created analysis plan with {len(data.tasks)} tasks")
            for i, task in enumerate(data.tasks, 1):
                click.echo(f"   {i}. {task.name} ({task.information_type})")

        elif event_type == 'task_started':
            click.echo(f"SEARCH: Starting: {data['task'].name}")

        elif event_type == 'pages_selected':
            pages = data['page_numbers']
            click.echo(f"PAGES: Selected pages: {pages}")

        elif event_type == 'task_completed':
            result = data['result']
            pages_analyzed = len(result.selected_pages)
            click.echo(f"SUCCESS: Completed: {data['task'].name} ({pages_analyzed} pages)")

        elif event_type == 'plan_updated':
            click.echo(f"UPDATED: Plan: {len(data.tasks)} tasks remaining")


# Create global CLI instance
cli_instance = DociaCLI()


@click.group(invoke_without_command=True)
@click.option('--config', '-c', help='Path to configuration file')
@click.option('--provider', type=click.Choice(['openai', 'openrouter']), help='AI provider')
@click.option('--api-key', help='API key for the selected provider')
@click.option('--storage-path', help='Local storage path for documents')
@click.pass_context
def docia(ctx, config, provider, api_key, storage_path):
    """Docia - VisionLM Document Intelligence CLI"""
    ctx.ensure_object(dict)

    # Initialize Docia
    try:
        if config:
            cli_instance.docia = cli_instance.initialize_docia(config)
        else:
            # Create config with provided options
            config_dict = {}
            if provider:
                config_dict['provider'] = provider
            if storage_path:
                config_dict['local_storage_path'] = storage_path

            # Load environment configuration first
            env_config = DociaConfig.from_env()

            # Override with provided options
            if config_dict:
                for key, value in config_dict.items():
                    setattr(env_config, key, value)

            cli_instance.docia = Docia(config=env_config, api_key=api_key)

        ctx.obj['docia'] = cli_instance.docia
        ctx.obj['cli'] = cli_instance

        # If no command is provided, start interactive shell
        if ctx.invoked_subcommand is None:
            from .commands.interactive_commands import InteractiveShell
            interactive_shell = InteractiveShell(cli_instance.docia, cli_instance)
            interactive_shell.run()
            return

    except Exception as e:
        click.echo(f"ERROR: Initialization failed: {e}", err=True)
        sys.exit(1)


# Register all commands
docia.add_command(add)
docia.add_command(list)
docia.add_command(remove)
docia.add_command(search)
docia.add_command(query)
docia.add_command(clear)
docia.add_command(stats)
docia.add_command(config)
docia.add_command(shell)
docia.add_command(start)


if __name__ == '__main__':
    docia()