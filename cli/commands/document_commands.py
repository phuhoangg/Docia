"""
Document Management Commands

Commands for adding, listing, removing, and searching documents.
"""

import click
from pathlib import Path
from typing import Optional


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--name', help='Custom document name')
@click.option('--id', help='Custom document ID')
@click.pass_context
def add(ctx, file_path, name, id):
    """Add a document to Docia's knowledge base"""
    docia_instance = ctx.obj['docia']

    try:
        click.echo(f"DOC: Adding document: {file_path}")

        # Use sync method for CLI
        document = docia_instance.add_document_sync(
            file_path=file_path,
            document_name=name,
            document_id=id
        )

        click.echo(f"SUCCESS: Document added successfully!")
        click.echo(f"   Name: {document.name}")
        click.echo(f"   ID: {document.id}")
        click.echo(f"   Pages: {len(document.pages)}")
        click.echo(f"   Status: {document.status.value}")

    except Exception as e:
        click.echo(f"ERROR: Failed to add document: {e}", err=True)
        import sys
        sys.exit(1)


@click.command()
@click.pass_context
def list(ctx):
    """List all documents in the knowledge base"""
    docia_instance = ctx.obj['docia']

    try:
        documents = docia_instance.list_documents_sync()

        if not documents:
            click.echo("FOLDER: No documents found in knowledge base")
            return

        click.echo(f"FOLDER: Found {len(documents)} document(s):")
        click.echo()

        for doc_info in documents:
            click.echo(f"DOC: {doc_info['name']}")
            click.echo(f"   ID: {doc_info['id']}")
            click.echo(f"   Pages: {doc_info.get('page_count', 0)}")
            click.echo(f"   Added: {doc_info.get('created_at', 'Unknown')}")
            click.echo()

    except Exception as e:
        click.echo(f"ERROR: Failed to list documents: {e}", err=True)
        import sys
        sys.exit(1)


@click.command()
@click.argument('document_id')
@click.pass_context
def remove(ctx, document_id):
    """Remove a document from the knowledge base"""
    docia_instance = ctx.obj['docia']

    try:
        # First, get document info for confirmation
        document = docia_instance.get_document_sync(document_id)
        if not document:
            click.echo(f"ERROR: Document with ID '{document_id}' not found")
            return

        click.echo(f"DELETE: Removing document: {document.name}")

        # Confirm deletion
        if click.confirm("Are you sure you want to remove this document?"):
            success = docia_instance.delete_document_sync(document_id)
            if success:
                click.echo("SUCCESS: Document removed successfully!")
            else:
                click.echo("ERROR: Failed to remove document")

    except Exception as e:
        click.echo(f"ERROR: Failed to remove document: {e}", err=True)
        import sys
        sys.exit(1)


@click.command()
@click.argument('search_term')
@click.option('--limit', '-l', default=10, help='Maximum number of results')
@click.pass_context
def search(ctx, search_term, limit):
    """Search documents by name and content"""
    docia_instance = ctx.obj['docia']

    try:
        results = docia_instance.search_documents_sync(search_term, limit)

        if not results:
            click.echo(f"SEARCH: No documents found matching: {search_term}")
            return

        click.echo(f"SEARCH: Found {len(results)} document(s) matching '{search_term}':")
        click.echo()

        for result in results:
            click.echo(f"DOC: {result['name']}")
            click.echo(f"   ID: {result['id']}")
            if 'summary' in result and result['summary']:
                summary = result['summary'][:100] + "..." if len(result['summary']) > 100 else result['summary']
                click.echo(f"   Summary: {summary}")
            click.echo()

    except Exception as e:
        click.echo(f"ERROR: Search failed: {e}", err=True)
        import sys
        sys.exit(1)