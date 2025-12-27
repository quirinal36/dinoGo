#!/usr/bin/env python3
"""
Confluence CLI Tool
Command-line interface for Confluence automation
"""

import sys
import argparse
from confluence_automation_manager import ConfluenceAutomationManager
from jira_confluence_integration import JiraConfluenceIntegration


def cmd_spaces(manager, args):
    """List all spaces"""
    manager.list_spaces()


def cmd_pages(manager, args):
    """List pages in space"""
    space = args.space if args.space else manager.space_key
    manager.list_pages_in_space(space)


def cmd_dashboard(manager, args):
    """Show space dashboard"""
    space = args.space if args.space else manager.space_key
    manager.print_space_dashboard(space)


def cmd_create(manager, args):
    """Create new page"""
    title = args.title
    content = args.content if args.content else "<p>Page created via CLI</p>"
    space = args.space if args.space else manager.space_key

    page_id = manager.create_page(title, content, space)

    if page_id:
        print(f"\n✅ Page created successfully!")
        print(f"   URL: {manager.base_url}/wiki/spaces/{space}/pages/{page_id}")


def cmd_update(manager, args):
    """Update existing page"""
    page_id = args.page_id
    title = args.title
    content = args.content

    manager.update_page(page_id, title, content)


def cmd_search(manager, args):
    """Search pages"""
    query = args.query
    space = args.space if args.space else None

    print(f"\n🔍 Searching: {query}\n")
    results = manager.search_pages(query, space, limit=args.limit)

    if not results:
        print("No results found.")
        return

    print(f"Found {len(results)} result(s):\n")
    for result in results:
        content = result.get('content', {})
        title = content.get('title', 'N/A')
        page_id = content.get('id', 'N/A')
        space_key = content.get('space', {}).get('key', 'N/A')

        print(f"📄 {title}")
        print(f"   ID: {page_id} | Space: {space_key}\n")


def cmd_export(manager, args):
    """Export page to PDF"""
    page_id = args.page_id
    output = args.output if args.output else f"exports/page_{page_id}.pdf"

    manager.export_page_to_pdf(page_id, output)


def cmd_report(manager, args):
    """Export space report"""
    space = args.space if args.space else manager.space_key
    output = args.output if args.output else None

    manager.export_report_json(space, output)


def cmd_sync(manager, args):
    """Sync Jira data to Confluence"""
    integration = JiraConfluenceIntegration(
        project_key=args.project,
        space_key=args.space if args.space else manager.space_key
    )

    if args.type == 'overview':
        integration.generate_project_overview_page()
    elif args.type == 'epic' and args.key:
        integration.generate_epic_documentation(args.key)
    elif args.type == 'story' and args.key:
        integration.generate_story_documentation(args.key)
    elif args.type == 'full':
        integration.generate_complete_project_documentation()
    else:
        print("❌ Invalid sync type or missing --key")


def main():
    parser = argparse.ArgumentParser(
        description='Confluence CLI - Confluence Automation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # List spaces
  %(prog)s spaces

  # List pages in space
  %(prog)s pages --space DIN

  # Show dashboard
  %(prog)s dashboard

  # Create page
  %(prog)s create --title "New Page" --content "<p>Hello World</p>"

  # Search pages
  %(prog)s search --query "title~'test'"

  # Export to PDF
  %(prog)s export PAGE_ID --output report.pdf

  # Sync Jira to Confluence
  %(prog)s sync --type overview --project DIN
  %(prog)s sync --type epic --key DIN-58 --project DIN
  %(prog)s sync --type full --project DIN
        '''
    )

    parser.add_argument('--space', default='DIN', help='Confluence space key (default: DIN)')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Spaces command
    subparsers.add_parser('spaces', help='List all accessible spaces')

    # Pages command
    pages_parser = subparsers.add_parser('pages', help='List pages in space')
    pages_parser.add_argument('--space', help='Space key')

    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Show space dashboard')
    dashboard_parser.add_argument('--space', help='Space key')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create new page')
    create_parser.add_argument('--title', required=True, help='Page title')
    create_parser.add_argument('--content', help='Page content (HTML)')
    create_parser.add_argument('--space', help='Space key')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update existing page')
    update_parser.add_argument('page_id', help='Page ID')
    update_parser.add_argument('--title', required=True, help='New title')
    update_parser.add_argument('--content', required=True, help='New content (HTML)')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search pages')
    search_parser.add_argument('--query', required=True, help='CQL query')
    search_parser.add_argument('--space', help='Limit to space')
    search_parser.add_argument('--limit', type=int, default=25, help='Max results')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export page to PDF')
    export_parser.add_argument('page_id', help='Page ID')
    export_parser.add_argument('--output', help='Output filename')

    # Report command
    report_parser = subparsers.add_parser('report', help='Export space report')
    report_parser.add_argument('--space', help='Space key')
    report_parser.add_argument('--output', help='Output filename')

    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync Jira to Confluence')
    sync_parser.add_argument('--type', required=True,
                           choices=['overview', 'epic', 'story', 'full'],
                           help='Sync type')
    sync_parser.add_argument('--key', help='Jira issue key (for epic/story)')
    sync_parser.add_argument('--project', default='DIN', help='Jira project key')
    sync_parser.add_argument('--space', help='Confluence space key')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize manager
    manager = ConfluenceAutomationManager(space_key=args.space)

    # Execute command
    commands = {
        'spaces': cmd_spaces,
        'pages': cmd_pages,
        'dashboard': cmd_dashboard,
        'create': cmd_create,
        'update': cmd_update,
        'search': cmd_search,
        'export': cmd_export,
        'report': cmd_report,
        'sync': cmd_sync
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        cmd_func(manager, args)
    else:
        print(f"❌ Unknown command: {args.command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
