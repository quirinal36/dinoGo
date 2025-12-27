#!/usr/bin/env python3
"""
Interactive Jira CLI Tool
Command-line interface for Jira automation and management
"""

import sys
import argparse
from jira_automation_manager import JiraAutomationManager


def cmd_health(manager, args):
    """Display project health dashboard"""
    manager.print_project_health()


def cmd_search(manager, args):
    """Search issues with JQL"""
    if not args.jql:
        print("❌ Error: --jql required")
        return

    print(f"\n🔍 Searching: {args.jql}\n")
    issues = manager.search_issues(args.jql, max_results=args.limit)

    if not issues:
        print("No issues found.")
        return

    print(f"Found {len(issues)} issue(s):\n")
    for issue in issues:
        key = issue['key']
        summary = issue['fields']['summary']
        status = issue['fields']['status']['name']
        priority = issue['fields']['priority']['name']

        print(f"📋 {key}: {summary}")
        print(f"   Status: {status} | Priority: {priority}\n")


def cmd_epic(manager, args):
    """Get Epic details with stories"""
    epic_key = args.epic_key

    print(f"\n📦 Epic: {epic_key}")
    print("="*60)

    # Get epic details
    try:
        epic = manager.jira.issue(epic_key)
        print(f"Summary: {epic['fields']['summary']}")
        print(f"Status: {epic['fields']['status']['name']}")
        print(f"Priority: {epic['fields']['priority']['name']}\n")
    except:
        print(f"❌ Could not find Epic {epic_key}")
        return

    # Get stories
    stories = manager.get_epic_stories(epic_key)

    if not stories:
        print("No stories found under this Epic.")
        return

    print(f"📚 Stories ({len(stories)}):\n")
    for story in stories:
        key = story['key']
        summary = story['fields']['summary']
        status = story['fields']['status']['name']

        print(f"  {key}: {summary}")
        print(f"    Status: {status}\n")


def cmd_story(manager, args):
    """Get Story details with subtasks"""
    story_key = args.story_key

    print(f"\n📖 Story: {story_key}")
    print("="*60)

    # Get story details
    try:
        story = manager.jira.issue(story_key)
        print(f"Summary: {story['fields']['summary']}")
        print(f"Status: {story['fields']['status']['name']}")
        print(f"Priority: {story['fields']['priority']['name']}\n")
    except:
        print(f"❌ Could not find Story {story_key}")
        return

    # Get subtasks
    subtasks = manager.get_story_subtasks(story_key)

    if not subtasks:
        print("No subtasks found under this Story.")
        return

    print(f"✅ Subtasks ({len(subtasks)}):\n")
    for task in subtasks:
        key = task['key']
        summary = task['fields']['summary']
        status = task['fields']['status']['name']

        print(f"  {key}: {summary}")
        print(f"    Status: {status}\n")


def cmd_transition(manager, args):
    """Transition issue to new status"""
    issue_key = args.issue_key
    transition = args.transition

    print(f"\n🔄 Transitioning {issue_key} to '{transition}'...")

    success = manager.transition_issue(issue_key, transition)

    if success:
        print(f"✅ Success!")
    else:
        print(f"❌ Failed to transition issue")


def cmd_comment(manager, args):
    """Add comment to issue"""
    issue_key = args.issue_key
    comment = args.comment

    print(f"\n💬 Adding comment to {issue_key}...")

    success = manager.add_comment(issue_key, comment)

    if success:
        print(f"✅ Comment added!")


def cmd_blocked(manager, args):
    """Show blocked issues"""
    print("\n🚧 Blocked Issues")
    print("="*60)

    blocked = manager.find_blocked_issues()

    if not blocked:
        print("✅ No blocked issues found!")
        return

    for issue in blocked:
        key = issue['key']
        summary = issue['fields']['summary']
        status = issue['fields']['status']['name']

        print(f"\n📋 {key}: {summary}")
        print(f"   Status: {status}")


def cmd_overdue(manager, args):
    """Show overdue issues"""
    print("\n⏰ Overdue Issues")
    print("="*60)

    overdue = manager.find_overdue_issues()

    if not overdue:
        print("✅ No overdue issues!")
        return

    for issue in overdue:
        key = issue['key']
        summary = issue['fields']['summary']
        due_date = issue['fields'].get('duedate', 'N/A')

        print(f"\n📋 {key}: {summary}")
        print(f"   Due: {due_date}")


def cmd_unassigned(manager, args):
    """Show unassigned issues"""
    print("\n👤 Unassigned Issues")
    print("="*60)

    unassigned = manager.find_unassigned_issues()

    if not unassigned:
        print("✅ All issues assigned!")
        return

    for issue in unassigned:
        key = issue['key']
        summary = issue['fields']['summary']
        priority = issue['fields']['priority']['name']

        print(f"\n📋 {key}: {summary}")
        print(f"   Priority: {priority}")


def cmd_report(manager, args):
    """Export JSON report"""
    filename = args.output if args.output else None

    manager.export_report_json(filename)


def main():
    parser = argparse.ArgumentParser(
        description='Jira CLI - Interactive Jira Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Project health dashboard
  %(prog)s health

  # Search with JQL
  %(prog)s search --jql "status = 'In Progress'"

  # View Epic with stories
  %(prog)s epic DIN-58

  # View Story with subtasks
  %(prog)s story DIN-61

  # Transition issue
  %(prog)s transition DIN-72 "In Progress"

  # Add comment
  %(prog)s comment DIN-72 "Working on this now"

  # Show blocked issues
  %(prog)s blocked

  # Show overdue issues
  %(prog)s overdue

  # Show unassigned issues
  %(prog)s unassigned

  # Export report
  %(prog)s report --output custom_report.json
        '''
    )

    parser.add_argument('--project', default='DIN', help='Jira project key (default: DIN)')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Health command
    subparsers.add_parser('health', help='Show project health dashboard')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search issues with JQL')
    search_parser.add_argument('--jql', required=True, help='JQL query string')
    search_parser.add_argument('--limit', type=int, default=50, help='Max results (default: 50)')

    # Epic command
    epic_parser = subparsers.add_parser('epic', help='View Epic with stories')
    epic_parser.add_argument('epic_key', help='Epic key (e.g., DIN-58)')

    # Story command
    story_parser = subparsers.add_parser('story', help='View Story with subtasks')
    story_parser.add_argument('story_key', help='Story key (e.g., DIN-61)')

    # Transition command
    transition_parser = subparsers.add_parser('transition', help='Transition issue status')
    transition_parser.add_argument('issue_key', help='Issue key')
    transition_parser.add_argument('transition', help='Target status (e.g., "In Progress")')

    # Comment command
    comment_parser = subparsers.add_parser('comment', help='Add comment to issue')
    comment_parser.add_argument('issue_key', help='Issue key')
    comment_parser.add_argument('comment', help='Comment text')

    # Blocked command
    subparsers.add_parser('blocked', help='Show blocked issues')

    # Overdue command
    subparsers.add_parser('overdue', help='Show overdue issues')

    # Unassigned command
    subparsers.add_parser('unassigned', help='Show unassigned issues')

    # Report command
    report_parser = subparsers.add_parser('report', help='Export JSON report')
    report_parser.add_argument('--output', help='Output filename (optional)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize manager
    manager = JiraAutomationManager(project_key=args.project)

    # Execute command
    commands = {
        'health': cmd_health,
        'search': cmd_search,
        'epic': cmd_epic,
        'story': cmd_story,
        'transition': cmd_transition,
        'comment': cmd_comment,
        'blocked': cmd_blocked,
        'overdue': cmd_overdue,
        'unassigned': cmd_unassigned,
        'report': cmd_report
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        cmd_func(manager, args)
    else:
        print(f"❌ Unknown command: {args.command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
