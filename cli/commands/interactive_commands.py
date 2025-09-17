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
        self.show_tasks = True  # Always show tasks
        self.running = True
        self.mode = "add"  # Default is add mode
        self.logo = r"""
    ╔════════════════════════════════════════════════╗
    ║  ██████╗  ██████╗  ██████╗██╗ █████╗           ║
    ║  ██╔══██╗██╔═══██╗██╔════╝██║██╔══██╗          ║
    ║  ██║  ██║██║   ██║██║     ██║███████║          ║
    ║  ██║  ██║██║   ██║██║     ██║██╔══██║          ║
    ║  ██████╔╝╚██████╔╝╚██████╗██║██║  ██║          ║
    ║  ╚═════╝  ╚═════╝  ╚═════╝╚═╝╚═╝  ╚═╝          ║
    ╠════════════════════════════════════════════════╣
    ║     VisionLM-Powered Documents Intelligence    ║    
    ╚════════════════════════════════════════════════╝
"""

    def display_welcome(self):
        """Display welcome message with enhanced logo"""
        click.echo(self.logo)
        click.echo()
        click.echo("Welcome to Docia Interactive Shell")
        click.echo("=" * 60)
        click.echo("To get started, add documents to analyze:")
        click.echo("  Type the path to a PDF or image file")
        click.echo("  Or drag and drop files onto this window")
        click.echo()
        click.echo("After adding documents, you can ask questions directly.")
        click.echo("Type '/' for available commands.")
        click.echo()

    def display_prompt(self):
        """Display the interactive prompt with enhanced styling"""
        return "Docia > "

    def display_help(self):
        """Display help information"""
        click.echo("Available commands:")
        click.echo("  /                 - Show this command menu")
        click.echo("  /add <file>       - Add a document")
        click.echo("  /list             - List all documents")
        click.echo("  /query <question> - Ask a question about your documents")
        click.echo("  /clear            - Clear conversation history")
        click.echo("  /exit             - Exit the interactive shell")
        click.echo()

    def display_tasks(self, tasks: List[Task]):
        """Display current tasks from planner"""
        if not tasks:
            return

        click.echo("Current Tasks:")
        click.echo("-" * 30)
        for i, task in enumerate(tasks, 1):
            status_icon = self._get_task_status_icon(task.status)
            click.echo(f"{i:2d}. {status_icon} {task.name}")
            click.echo(f"     Type: {task.information_type}")
        click.echo()

    def display_help(self):
        """Display help information"""
        click.echo("Available commands:")
        click.echo("  /                 - Show this command menu")
        click.echo("  /add <file>       - Add a document")
        click.echo("  /list             - List all documents")
        click.echo("  /query <question> - Ask a question about your documents")
        click.echo("  /clear            - Clear conversation history")
        click.echo("  /exit             - Exit the interactive shell")
        click.echo()

    def display_command_menu(self):
        """Display quick command menu"""
        click.echo("Commands:")
        click.echo("  /add              - Switch to add document mode")
        click.echo("  /query            - Switch to query mode")
        click.echo("  /list             - List all documents")
        click.echo("  /clear            - Clear conversation history")
        click.echo("  /exit             - Exit shell")
        click.echo()
        click.echo(f"Current mode: {self.mode.upper()}")
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

    def progress_callback(self, event_type: str, data):
        """Progress callback for real-time updates"""
        if event_type == 'plan_created':
            self.current_plan = data
            self.current_tasks = data.tasks
            if self.show_tasks:
                click.echo("Plan created:")
                self.display_tasks(data.tasks)

        elif event_type == 'task_started':
            task = data.get('task')
            if task and self.show_tasks:
                click.echo(f"Starting: {task.name}")

        elif event_type == 'task_completed':
            task = data.get('task')
            result = data.get('result')
            if task and self.show_tasks:
                pages_analyzed = len(result.selected_pages) if result else 0
                click.echo(f"Completed: {task.name} ({pages_analyzed} pages)")

        elif event_type == 'pages_selected':
            pages = data.get('page_numbers', [])
            if self.show_tasks:
                click.echo(f"Pages selected: {pages}")

    async def process_query(self, query_text: str):
        """Process a query interactively"""
        try:
            # Check if query is a folder path
            if os.path.isdir(query_text.strip()):
                folder_path = Path(query_text.strip())
                click.echo(f"Processing folder: {folder_path}")
                
                # Add all supported files in the folder
                supported_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
                added_documents = []
                
                for file_path in folder_path.iterdir():
                    if file_path.suffix.lower() in supported_extensions:
                        try:
                            doc = self.docia.add_document(str(file_path))
                            added_documents.append(doc)
                            click.echo(f"  Added: {file_path.name}")
                        except Exception as e:
                            click.echo(f"  Failed to add {file_path.name}: {e}")
                
                if added_documents:
                    click.echo(f"Added {len(added_documents)} documents from folder")
                    query_text = f"Analyze all documents in the folder {folder_path.name}"
                else:
                    click.echo("No supported documents found in folder")
                    return
            
            click.echo(f"Querying: {query_text}")
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
            click.echo("" + "="*30)
            click.echo("RESULTS:")
            click.echo("="*30)
            click.echo(result.answer)
            click.echo()

            # Display metadata
            click.echo("Information:")
            click.echo(f"   Time: {result.processing_time:.2f}s")
            click.echo(f"   Pages: {result.page_count}")
            click.echo(f"   Tasks: {result.metadata.get('tasks_completed', 0)}")

            # Update conversation history
            self.conversation_history.append(
                ConversationMessage(role="user", content=query_text)
            )
            self.conversation_history.append(
                ConversationMessage(role="assistant", content=result.answer)
            )

            click.echo(f"Messages: {len(self.conversation_history)} messages")

        except Exception as e:
            click.echo(f"Error: Query failed: {e}", err=True)

    def run(self):
        """Run the interactive shell"""
        self.display_welcome()
        self._run_basic_ui()

    def _run_basic_ui(self):
        """Run with basic UI using click.prompt"""
        # Display initial instructions
        click.echo("ADD MODE: Please add documents to get started.")
        click.echo("Enter file path or drag and drop files here.")
        click.echo()
        
        while self.running:
            try:
                # Display tasks if available
                if self.show_tasks and self.current_tasks:
                    self.display_tasks(self.current_tasks)
                
                # Get user input
                prompt_text = f"[{self.mode.upper()}] Docia > " if self.mode else "Docia > "
                user_input = click.prompt(prompt_text, default="", show_default=False)

                # Handle empty input
                if not user_input.strip():
                    continue

                # Handle commands with "/"
                if user_input.startswith("/"):
                    self._handle_slash_command(user_input)
                    continue

                # Handle exit command
                if user_input.lower() in ['exit', 'quit']:
                    self.running = False
                    click.echo("\nGoodbye!")
                    break

                # Process according to current mode
                if self.mode == "add":
                    # In add mode, process as file path
                    self._handle_add_command([user_input.strip()])
                    # Switch to query mode after successfully adding file
                    self.mode = "query"
                    click.echo("\nSwitched to QUERY MODE. You can now ask questions about your documents.")
                    click.echo("Example: 'What is this document about?'")
                    click.echo()
                else:
                    # In query mode, process as question
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

    def _handle_slash_command(self, user_input):
        """Handle commands that start with '/'"""
        command = user_input[1:].strip()  # Remove the leading '/'
        
        if not command:
            # Display command menu when only '/' is entered
            self.display_command_menu()
            return

        # Parse command and arguments
        parts = command.split()
        cmd = parts[0].lower() if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        # Handle specific commands
        if cmd in ['exit', 'quit']:
            self.running = False
            click.echo("\nGoodbye!")
        elif cmd == 'clear':
            self.conversation_history.clear()
            click.echo("Conversation history cleared")
        elif cmd == 'list':
            self._list_documents()
        elif cmd == 'add':
            self.mode = "add"
            click.echo("Switched to ADD MODE. Enter file paths to add documents.")
        elif cmd == 'query':
            self.mode = "query"
            click.echo("Switched to QUERY MODE. Enter your questions.")
        else:
            click.echo(f"Unknown command: /{cmd}. Type / for available commands.")

    def _handle_add_command(self, args):
        """Handle the add command"""
        # Simple implementation - in a full implementation, this would parse arguments properly
        file_path = args[0] if args else None
        if not file_path:
            click.echo("Usage: /add <file_path>")
            return
            
        try:
            if not os.path.exists(file_path):
                click.echo(f"Error: File '{file_path}' not found")
                return
                
            click.echo(f"Adding document: {file_path}")
            document = self.docia.add_document_sync(file_path=file_path)
            click.echo(f"Document added successfully!")
            click.echo(f"   Name: {document.name}")
            click.echo(f"   ID: {document.id}")
            click.echo(f"   Pages: {len(document.pages)}")
        except Exception as e:
            click.echo(f"Failed to add document: {e}")

    async def _async_query(self, query_text, document_ids, mode, max_pages, conversation):
        """Async helper for processing queries"""
        try:
            click.echo(f"Querying: {query_text}")
            click.echo()

            # Convert mode string to enum
            query_mode = QueryMode(mode)

            # Execute query with progress tracking
            result = await self.docia.query(
                question=query_text,
                mode=query_mode,
                document_ids=document_ids if document_ids else None,
                max_pages=max_pages,
                conversation_history=self.conversation_history if conversation else None,
                task_update_callback=self.progress_callback
            )

            # Display results
            click.echo("Results:")
            click.echo("=" * 30)
            click.echo(result.answer)
            click.echo()

            # Display metadata
            click.echo("Information:")
            click.echo(f"   Time: {result.processing_time:.2f}s")
            click.echo(f"   Pages: {result.page_count}")
            click.echo(f"   Tasks: {result.metadata.get('tasks_completed', 0)}")

            # Update conversation history if in conversation mode
            if conversation:
                self.conversation_history.append(
                    ConversationMessage(role="user", content=query_text)
                )
                self.conversation_history.append(
                    ConversationMessage(role="assistant", content=result.answer)
                )
                click.echo(f"Messages: {len(self.conversation_history)}")

        except Exception as e:
            click.echo(f"Query failed: {e}")

    def _list_documents(self):
        """List all documents"""
        try:
            documents = self.docia.list_documents_sync()
            if not documents:
                click.echo("No documents found")
                return

            click.echo(f"Documents ({len(documents)}):")
            click.echo("=" * 30)
            for doc in documents:
                pages_info = f"{doc.get('page_count', 0)} pages"
                status = "Ready" if doc.get('status') == "completed" else "Processing"
                click.echo(f"{doc.get('name')} ({doc.get('id')}) - {pages_info} [{status}]")
        except Exception as e:
            click.echo(f"Error listing documents: {e}")

    def _show_stats(self):
        """Show system statistics"""
        try:
            stats = self.docia.get_stats()
            click.echo("System Statistics:")
            click.echo("=" * 30)
            click.echo(f"Documents: {stats.get('total_documents', 0)}")
            click.echo(f"Queries: {stats.get('total_queries', 0)}")
            click.echo(f"Time: {stats.get('avg_processing_time', 0):.2f}s")
        except Exception as e:
            click.echo(f"Error getting stats: {e}")


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