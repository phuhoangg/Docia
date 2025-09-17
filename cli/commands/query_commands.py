"""
Query Commands

Commands for querying documents and managing conversations.
"""

import click
import os
from pathlib import Path
from typing import List

from docia.models.document import QueryMode
from docia.models.agent import ConversationMessage


@click.command()
@click.argument('query')
@click.option('--document', '-d', multiple=True, help='Specific document IDs to search')
@click.option('--mode', type=click.Choice(['auto', 'fast', 'comprehensive']), default='auto', help='Query mode')
@click.option('--max-pages', type=int, help='Maximum pages to analyze')
@click.option('--conversation', '-c', is_flag=True, help='Enable conversation mode')
@click.pass_context
def query(ctx, query, document, mode, max_pages, conversation):
    """Query documents with intelligent analysis"""
    docia_instance = ctx.obj['docia']
    cli_instance = ctx.obj['cli']

    try:
        # Check if query is a folder path
        if os.path.isdir(query.strip()):
            folder_path = Path(query.strip())
            click.echo(f"[DIR] Processing folder: {folder_path}")
            
            # Add all supported files in the folder
            supported_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            added_documents = []
            
            for file_path in folder_path.iterdir():
                if file_path.suffix.lower() in supported_extensions:
                    try:
                        doc = docia_instance.add_document(str(file_path))
                        added_documents.append(doc)
                        click.echo(f"  [OK] Added: {file_path.name}")
                    except Exception as e:
                        click.echo(f"  [ERR] Failed to add {file_path.name}: {e}")
            
            if added_documents:
                click.echo(f"[INFO] Added {len(added_documents)} documents from folder")
                query = f"Analyze all documents in the folder {folder_path.name}"
            else:
                click.echo("[WARN] No supported documents found in folder")
                return

        click.echo(f"[SEARCH] Querying: {query}")
        click.echo()

        # Convert mode string to enum
        query_mode = QueryMode(mode)

        # Execute query with progress tracking
        result = docia_instance.query_sync(
            question=query,
            mode=query_mode,
            document_ids=list(document) if document else None,
            max_pages=max_pages,
            conversation_history=cli_instance.conversation_history if conversation else None,
            task_update_callback=cli_instance._progress_callback if click.echo else None
        )

        # Display results
        click.echo("RESULTS: Analysis Results:")
        click.echo("=" * 50)
        click.echo(result.answer)
        click.echo()

        # Display metadata
        click.echo("INFO: Query Information:")
        click.echo(f"   Processing time: {result.processing_time:.2f} seconds")
        click.echo(f"   Pages analyzed: {result.page_count}")
        click.echo(f"   Tasks completed: {result.metadata.get('tasks_completed', 0)}")
        click.echo(f"   Total iterations: {result.metadata.get('agent_iterations', 0)}")

        if result.total_cost > 0:
            click.echo(f"   Cost: ${result.total_cost:.4f}")

        # Update conversation history if in conversation mode
        if conversation:
            cli_instance.conversation_history.append(
                ConversationMessage(role="user", content=query)
            )
            cli_instance.conversation_history.append(
                ConversationMessage(role="assistant", content=result.answer)
            )
            click.echo(f"CHAT: Conversation history: {len(cli_instance.conversation_history)} messages")

    except Exception as e:
        click.echo(f"ERROR: Query failed: {e}", err=True)
        import sys
        sys.exit(1)


@click.command()
@click.pass_context
def clear(ctx):
    """Clear conversation history"""
    cli_instance = ctx.obj['cli']
    cli_instance.conversation_history.clear()
    click.echo("CHAT: Conversation history cleared")