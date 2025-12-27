#!/usr/bin/env python3
"""
Compass CLI Tool
Command-line interface for Compass component management
"""

import sys
import argparse
from compass_automation_manager import CompassAutomationManager


def cmd_list(manager, args):
    """List all components"""
    manager.list_components()


def cmd_create(manager, args):
    """Create new component"""
    component_id = manager.create_component(
        name=args.name,
        component_type=args.type,
        description=args.description
    )

    if component_id:
        print(f"\n✅ Component created successfully!")
        print(f"   ID: {component_id}")


def cmd_sync(manager, args):
    """Sync Jira project to Compass"""
    components = manager.create_project_components_from_jira(args.project)

    if components:
        print(f"\n✅ Synced {len(components)} components from Jira")


def cmd_cloudid(manager, args):
    """Get Cloud ID"""
    cloud_id = manager.get_cloud_id()
    if cloud_id:
        print(f"\n✅ Cloud ID: {cloud_id}")


def main():
    parser = argparse.ArgumentParser(
        description='Compass CLI - Component Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Get Cloud ID
  %(prog)s cloudid

  # List components
  %(prog)s list

  # Create component
  %(prog)s create --name "API Gateway" --type SERVICE --description "Main API Gateway"

  # Sync from Jira
  %(prog)s sync --project DIN
        '''
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Cloud ID command
    subparsers.add_parser('cloudid', help='Get Atlassian Cloud ID')

    # List command
    subparsers.add_parser('list', help='List all components')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create new component')
    create_parser.add_argument('--name', required=True, help='Component name')
    create_parser.add_argument('--type', default='SERVICE',
                              choices=['SERVICE', 'LIBRARY', 'APPLICATION', 'CAPABILITY',
                                     'CLOUD_RESOURCE', 'DATA_PIPELINE', 'MACHINE_LEARNING_MODEL',
                                     'UI_ELEMENT', 'WEBSITE', 'OTHER'],
                              help='Component type')
    create_parser.add_argument('--description', help='Component description')

    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync Jira project to Compass')
    sync_parser.add_argument('--project', default='DIN', help='Jira project key')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize manager
    manager = CompassAutomationManager()

    # Execute command
    commands = {
        'cloudid': cmd_cloudid,
        'list': cmd_list,
        'create': cmd_create,
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
