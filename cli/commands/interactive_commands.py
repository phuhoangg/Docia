"""
Interactive Shell Commands

Commands for interactive shell interface.
"""

import click
import asyncio
import sys
from typing import List, Optional
from datetime import datetime
import os
from pathlib import Path

from docia.models.document import QueryMode
from docia.models.agent import ConversationMessage
from docia.models.planner import Task, TaskStatus, Plan


class InteractiveShell:
    """Interactive shell for Docia with enhanced UI"""

    def __init__(self, docia_instance, cli_instance):
        self.docia = docia_instance
        self.cli = cli_instance
        self.conversation_history: List[ConversationMessage] = []
        self.current_plan: Optional[Plan] = None
        self.current_tasks: List[Task] = []
        self.show_tasks = False
        self.running = True
        self.logo = r"""
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                              │
│    ██████╗  ██████╗  ██████╗██╗ █████╗                             VisionLM-powered           │
│    ██╔══██╗██╔═══██╗██╔════╝██║██╔══██╗                            Documents Intelligence     │
│    ██║  ██║██║   ██║██║     ██║███████║                            Solution                   │
│    ██║  ██║██║   ██║██║     ██║██╔══██║                                                       │
│    ██████╔╝╚██████╔╝╚██████╗██║██║  ██║                            Intelligent Document       │
│    ╚═════╝  ╚═════╝  ╚═════╝╚═╝╚═╝  ╚═╝                            Analysis & Insights        │
│                                                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
        """

    def display_welcome(self):
        """Display welcome message with enhanced logo"""
        click.echo(self.logo)
        click.echo()
        click.echo("Welcome to Docia Interactive Shell")
        click.echo("=" * 60)
        click.echo("Type 'help' for available commands or start querying your documents.")
        click.echo()

    def display_prompt(self):
        """Display the interactive prompt with enhanced styling"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] Docia > "

    def display_help(self):
        """Display help information"""
        click.echo("Available commands:")
        click.echo("  help              - Show this help message")
        click.echo("  clear             - Clear conversation history")
        click.echo("  stats             - Show system statistics")
        print("  list              - List all documents")
        click.echo("  tasks             - Toggle task display mode")
        click.echo("  exit / quit       - Exit the interactive shell")
        click.echo()
        click.echo("Or simply type your query to analyze documents:")
        click.echo('  "What are the key findings in the report?"')
        click.echo('  "Extract all financial data from Q3"')
        click.echo()
        click.echo("To analyze PDF documents:")
        click.echo("  1. Use the 'add' command to add documents to Docia's knowledge base:")
        click.echo("     add /path/to/your/document.pdf")
        click.echo("  2. Or drag and drop files or folders:")
        click.echo("     On Windows: Drag files/folders onto this window and press Enter")
        click.echo("     On other systems: Copy file path and paste into the input field")
        click.echo()

    def display_tasks(self, tasks: List[Task]):
        """Display current tasks from planner"""
        if not tasks:
            return

        click.echo("+- Current Plan Tasks ---------------------------------------------+")
        for i, task in enumerate(tasks, 1):
            status_icon = self._get_task_status_icon(task.status)
            click.echo(f"| {i:2d}. {status_icon} {task.name}")
            click.echo(f"|     Type: {task.information_type}")
            if task.description:
                click.echo(f"|     Description: {task.description}")
            if task.dependencies:
                click.echo(f"|     Dependencies: {', '.join(task.dependencies)}")
        click.echo("-------------------------------------------------------------------")
        click.echo()

    def _get_task_status_icon(self, status: TaskStatus) -> str:
        """Get status icon for task"""
        icons = {
            TaskStatus.PENDING: "[ ]",
            TaskStatus.IN_PROGRESS: "[*]",
            TaskStatus.COMPLETED: "[x]",
            TaskStatus.FAILED: "[!]",
            TaskStatus.SKIPPED: "[s]"
        }
        return icons.get(status, "[?]")

    def progress_callback(self, event_type: str, data):
        """Progress callback for real-time updates"""
        if event_type == 'plan_created':
            self.current_plan = data
            self.current_tasks = data.tasks
            if self.show_tasks:
                click.echo("\n[PLAN] PLAN CREATED:")
                self.display_tasks(data.tasks)

        elif event_type == 'task_started':
            task = data.get('task')
            if task and self.show_tasks:
                click.echo(f"\n[RUN] STARTING: {task.name}")

        elif event_type == 'task_completed':
            task = data.get('task')
            result = data.get('result')
            if task and self.show_tasks:
                pages_analyzed = len(result.selected_pages) if result else 0
                click.echo(f"\n[DONE] COMPLETED: {task.name} ({pages_analyzed} pages)")

        elif event_type == 'pages_selected':
            pages = data.get('page_numbers', [])
            if self.show_tasks:
                click.echo(f"\n[PAGES] PAGES SELECTED: {pages}")

    async def process_query(self, query_text: str):
        """Process a query interactively"""
        try:
            # Check if query is a folder path
            if os.path.isdir(query_text.strip()):
                folder_path = Path(query_text.strip())
                click.echo(f"\n[DIR] Processing folder: {folder_path}")
                
                # Add all supported files in the folder
                supported_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
                added_documents = []
                
                for file_path in folder_path.iterdir():
                    if file_path.suffix.lower() in supported_extensions:
                        try:
                            doc = self.docia.add_document(str(file_path))
                            added_documents.append(doc)
                            click.echo(f"  [OK] Added: {file_path.name}")
                        except Exception as e:
                            click.echo(f"  [ERR] Failed to add {file_path.name}: {e}")
                
                if added_documents:
                    click.echo(f"\n[INFO] Added {len(added_documents)} documents from folder")
                    query_text = f"Analyze all documents in the folder {folder_path.name}"
                else:
                    click.echo("\n[WARN] No supported documents found in folder")
                    return
            
            click.echo(f"\n[SEARCH] SEARCHING: {query_text}")
            click.echo()

            # Execute query with real-time updates
            result = await self.docia.query(
                question=query_text,
                mode=QueryMode.AUTO,
                document_ids=None,
                max_pages=None,
                conversation_history=self.conversation_history,
                task_update_callback=self.progress_callback
            )

            # Display results
            click.echo("\n" + "="*60)
            click.echo("ANALYSIS RESULTS:")
            click.echo("="*60)
            click.echo(result.answer)
            click.echo()

            # Display metadata
            click.echo("QUERY METADATA:")
            click.echo(f"   Time: {result.processing_time_seconds:.2f}s")
            click.echo(f"   Pages: {result.get_total_pages_analyzed()}")
            click.echo(f"   Tasks: {len(result.task_results)}")
            click.echo(f"   Iterations: {result.total_iterations}")

            if result.total_cost > 0:
                click.echo(f"   Cost: ${result.total_cost:.4f}")

            # Update conversation history
            self.conversation_history.append(
                ConversationMessage(role="user", content=query_text)
            )
            self.conversation_history.append(
                ConversationMessage(role="assistant", content=result.answer)
            )

            click.echo(f"\n[CHAT] Conversation: {len(self.conversation_history)} messages")

        except Exception as e:
            click.echo(f"\n❌ ERROR: Query failed: {e}", err=True)

    def run(self):
        """Run the interactive shell"""
        self.display_welcome()
        self._run_basic_ui()

    def _run_basic_ui(self):
        """Run with basic UI using click.prompt"""
        while self.running:
            try:
                # Get user input
                user_input = click.prompt(self.display_prompt(), default="", show_default=False)

                # Handle empty input
                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.lower() in ['exit', 'quit']:
                    self.running = False
                    click.echo("\nGoodbye!")
                    break

                elif user_input.lower() == 'help':
                    self.display_help()

                elif user_input.lower() == 'clear':
                    self.conversation_history.clear()
                    click.echo("💬 Conversation history cleared")

                elif user_input.lower() == 'stats':
                    self._show_stats()

                elif user_input.lower() == 'list':
                    self._list_documents()

                elif user_input.lower() == 'tasks':
                    self.show_tasks = not self.show_tasks
                    status = "enabled" if self.show_tasks else "disabled"
                    click.echo(f"📋 Task display {status}")
                    if self.show_tasks and self.current_tasks:
                        self.display_tasks(self.current_tasks)

                else:
                    # Process as query
                    asyncio.run(self.process_query(user_input))

            except click.exceptions.Abort:
                # Handle Ctrl+C or terminal issues gracefully
                click.echo("\n\nGoodbye!")
                break
            except KeyboardInterrupt:
                click.echo("\n\nGoodbye!")
                break
            except EOFError:
                click.echo("\nGoodbye!")
                break

    def _show_stats(self):
        """Show system statistics"""
        try:
            stats = self.docia.get_stats()
            click.echo("\nSYSTEM STATISTICS:")
            click.echo("=" * 40)
            click.echo(f"Documents: {stats.get('total_documents', 0)}")
            click.echo(f"Queries: {stats.get('total_queries', 0)}")
            click.echo(f"Cost: ${stats.get('total_cost', 0):.4f}")
            click.echo(f"Time: {stats.get('avg_processing_time', 0):.2f}s")
        except Exception as e:
            click.echo(f"[ERR] Error getting stats: {e}")

    def _list_documents(self):
        """List all documents"""
        try:
            documents = self.docia.list_documents_sync()
            if not documents:
                click.echo("No documents found")
                return

            click.echo(f"\nDOCUMENTS ({len(documents)}):")
            click.echo("=" * 50)
            for doc in documents:
                pages_info = f"{doc.get('page_count', 0)} pages"
                status_icon = "[OK]" if doc.get('status') == "completed" else "[RUN]"
                click.echo(f"{status_icon} {doc.get('name')} ({doc.get('id')}) - {pages_info}")
        except Exception as e:
            click.echo(f"[ERR] Error listing documents: {e}")


@click.command()
@click.pass_context
def shell(ctx):
    """Start interactive shell"""
    docia_instance = ctx.obj['docia']
    cli_instance = ctx.obj['cli']

    try:
        # Create and run interactive shell
        interactive_shell = InteractiveShell(docia_instance, cli_instance)
        interactive_shell.run()
    except Exception as e:
        click.echo(f"ERROR: Failed to start interactive shell: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@click.command()
@click.pass_context
def start(ctx):
    """Start Docia interactive mode (alias for shell)"""
    return shell(ctx)