"""
System Commands

Commands for system statistics and configuration management.
"""

import click
import json
from pathlib import Path


@click.command()
@click.pass_context
def stats(ctx):
    """Show Docia system statistics"""
    docia_instance = ctx.obj['docia']

    try:
        stats = docia_instance.get_stats()

        click.echo("STATS: Docia System Statistics")
        click.echo("=" * 40)
        click.echo(f"Version: {stats['docia_version']}")
        click.echo(f"Engine: {stats['intelligence_engine']}")
        click.echo()

        click.echo("CONFIG: Configuration:")
        config = stats['config']
        click.echo(f"   Provider: {config['provider']}")
        click.echo(f"   Storage: {config['storage_type']}")
        click.echo(f"   Max iterations: {config['max_agent_iterations']}")
        click.echo(f"   Max pages per task: {config['max_pages_per_task']}")
        click.echo()

        click.echo("STORAGE: Knowledge Storage:")
        storage = stats['knowledge_storage']
        click.echo(f"   Type: {storage.get('storage_type', 'Unknown')}")
        if 'document_count' in storage:
            click.echo(f"   Documents: {storage['document_count']}")
        click.echo()

        click.echo("INTELLIGENCE: Intelligence:")
        intelligence = stats['intelligence']
        click.echo(f"   Summarizer: {intelligence['summarizer'].get('status', 'Unknown')}")
        click.echo(f"   Agent: {intelligence['agent'].get('status', 'Unknown')}")
        click.echo()

        click.echo("FORMATS: Supported Formats:")
        formats = stats['supported_formats']
        click.echo(f"   {', '.join(formats)}")

    except Exception as e:
        click.echo(f"ERROR: Failed to get stats: {e}", err=True)
        import sys
        sys.exit(1)


@click.group()
def config():
    """Configuration management commands"""
    pass


@config.command()
@click.pass_context
def show(ctx):
    """Show current configuration"""
    try:
        from ..main import cli_instance
        if cli_instance.config_file.exists():
            with open(cli_instance.config_file, 'r') as f:
                config_data = json.load(f)

            click.echo("CONFIG: Current Configuration:")
            click.echo(json.dumps(config_data, indent=2))
        else:
            click.echo("CONFIG: No configuration file found")
            click.echo("Using environment variables and defaults")
    except Exception as e:
        click.echo(f"ERROR: Failed to show configuration: {e}", err=True)


@config.command()
@click.option('--provider', type=click.Choice(['openai', 'openrouter']))
@click.option('--storage-path')
@click.option('--max-iterations', type=int)
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']))
@click.pass_context
def set(ctx, provider, storage_path, max_iterations, log_level):
    """Set configuration values"""
    try:
        from ..main import cli_instance
        # Load existing config or create new
        if cli_instance.config_file.exists():
            with open(cli_instance.config_file, 'r') as f:
                config_data = json.load(f)
        else:
            config_data = {}

        # Update values
        if provider:
            config_data['provider'] = provider
        if storage_path:
            config_data['local_storage_path'] = storage_path
        if max_iterations:
            config_data['max_agent_iterations'] = max_iterations
        if log_level:
            config_data['log_level'] = log_level

        # Save config
        cli_instance.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cli_instance.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)

        click.echo("SUCCESS: Configuration saved successfully!")
        click.echo(f"   Location: {cli_instance.config_file}")

    except Exception as e:
        click.echo(f"ERROR: Failed to set configuration: {e}", err=True)