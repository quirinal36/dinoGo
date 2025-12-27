#!/usr/bin/env python3
"""
Jira-Confluence Integration
Automated documentation generation from Jira projects to Confluence
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from jira_automation_manager import JiraAutomationManager
from confluence_automation_manager import ConfluenceAutomationManager


class JiraConfluenceIntegration:
    """Integrates Jira and Confluence for automated documentation"""

    def __init__(self, project_key: str = "DIN", space_key: str = "DIN"):
        self.project_key = project_key
        self.space_key = space_key

        self.jira = JiraAutomationManager(project_key=project_key)
        self.confluence = ConfluenceAutomationManager(space_key=space_key)

    # ==================== Documentation Generators ====================

    def generate_project_overview_page(self) -> Optional[str]:
        """Generate project overview page in Confluence"""
        print("\n📝 Generating Project Overview Page...")

        # Get Jira data
        report = self.jira.generate_sprint_report()

        # Build HTML content
        title = f"{self.project_key} - Project Overview"

        html_body = f"""
<h1>{self.project_key} Project Overview</h1>

<p><em>Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</em></p>

<h2>📊 Project Summary</h2>
<table>
  <tbody>
    <tr>
      <th>Total Active Issues</th>
      <td>{report['summary']['total_active']}</td>
    </tr>
    <tr>
      <th>Blocked Issues</th>
      <td>{report['summary']['blocked_count']}</td>
    </tr>
    <tr>
      <th>Overdue Issues</th>
      <td>{report['summary']['overdue_count']}</td>
    </tr>
  </tbody>
</table>

<h2>📈 Issues by Status</h2>
<table>
  <tbody>
"""

        for status, count in report['issues_by_status'].items():
            html_body += f"""
    <tr>
      <th>{status}</th>
      <td>{count}</td>
    </tr>
"""

        html_body += """
  </tbody>
</table>

<h2>🎯 Issues by Priority</h2>
<table>
  <tbody>
"""

        for priority, count in sorted(report['issues_by_priority'].items()):
            html_body += f"""
    <tr>
      <th>{priority}</th>
      <td>{count}</td>
    </tr>
"""

        html_body += """
  </tbody>
</table>
"""

        # Add blocked issues if any
        if report['blocked']:
            html_body += """
<h2>🚧 Blocked Issues</h2>
<ul>
"""
            for issue_key in report['blocked']:
                jira_url = self.jira.base_url
                html_body += f"""  <li><a href="{jira_url}/browse/{issue_key}">{issue_key}</a></li>\n"""

            html_body += "</ul>\n"

        # Add overdue issues if any
        if report['overdue']:
            html_body += """
<h2>⏰ Overdue Issues</h2>
<ul>
"""
            for issue_key in report['overdue']:
                jira_url = self.jira.base_url
                html_body += f"""  <li><a href="{jira_url}/browse/{issue_key}">{issue_key}</a></li>\n"""

            html_body += "</ul>\n"

        # Create or update Confluence page
        page_id = self.confluence.update_or_create_page(
            title=title,
            body=html_body,
            space_key=self.space_key
        )

        return page_id

    def generate_epic_documentation(self, epic_key: str) -> Optional[str]:
        """Generate comprehensive Epic documentation page"""
        print(f"\n📝 Generating Epic Documentation: {epic_key}...")

        try:
            # Get Epic details
            epic = self.jira.jira.issue(epic_key)
            epic_summary = epic['fields']['summary']
            epic_description = epic['fields'].get('description', 'No description')
            epic_status = epic['fields']['status']['name']
            epic_priority = epic['fields']['priority']['name']

            # Get stories under Epic
            stories = self.jira.get_epic_stories(epic_key)

            # Build HTML content
            title = f"{epic_key}: {epic_summary}"

            html_body = f"""
<h1>{epic_key}: {epic_summary}</h1>

<p><em>Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</em></p>

<h2>📦 Epic Information</h2>
<table>
  <tbody>
    <tr>
      <th>Epic Key</th>
      <td><a href="{self.jira.base_url}/browse/{epic_key}">{epic_key}</a></td>
    </tr>
    <tr>
      <th>Status</th>
      <td>{epic_status}</td>
    </tr>
    <tr>
      <th>Priority</th>
      <td>{epic_priority}</td>
    </tr>
  </tbody>
</table>

<h2>📄 Description</h2>
<p>{epic_description}</p>

<h2>📚 Stories ({len(stories)})</h2>
"""

            if stories:
                html_body += "<table>\n  <thead>\n    <tr>\n"
                html_body += "      <th>Key</th>\n"
                html_body += "      <th>Summary</th>\n"
                html_body += "      <th>Status</th>\n"
                html_body += "      <th>Story Points</th>\n"
                html_body += "    </tr>\n  </thead>\n  <tbody>\n"

                for story in stories:
                    story_key = story['key']
                    story_summary = story['fields']['summary']
                    story_status = story['fields']['status']['name']
                    story_points = story['fields'].get('customfield_10016', 'N/A')

                    html_body += f"""    <tr>
      <td><a href="{self.jira.base_url}/browse/{story_key}">{story_key}</a></td>
      <td>{story_summary}</td>
      <td>{story_status}</td>
      <td>{story_points}</td>
    </tr>
"""

                html_body += "  </tbody>\n</table>\n"
            else:
                html_body += "<p><em>No stories found under this Epic.</em></p>\n"

            # Create Confluence page
            page_id = self.confluence.update_or_create_page(
                title=title,
                body=html_body,
                space_key=self.space_key
            )

            return page_id

        except Exception as e:
            print(f"❌ Error generating Epic documentation: {e}")
            return None

    def generate_story_documentation(self, story_key: str) -> Optional[str]:
        """Generate Story documentation with subtasks"""
        print(f"\n📝 Generating Story Documentation: {story_key}...")

        try:
            # Get Story details
            story = self.jira.jira.issue(story_key)
            story_summary = story['fields']['summary']
            story_description = story['fields'].get('description', 'No description')
            story_status = story['fields']['status']['name']
            story_priority = story['fields']['priority']['name']
            story_points = story['fields'].get('customfield_10016', 'N/A')

            # Get subtasks
            subtasks = self.jira.get_story_subtasks(story_key)

            # Build HTML
            title = f"{story_key}: {story_summary}"

            html_body = f"""
<h1>{story_key}: {story_summary}</h1>

<p><em>Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</em></p>

<h2>📖 Story Information</h2>
<table>
  <tbody>
    <tr>
      <th>Story Key</th>
      <td><a href="{self.jira.base_url}/browse/{story_key}">{story_key}</a></td>
    </tr>
    <tr>
      <th>Status</th>
      <td>{story_status}</td>
    </tr>
    <tr>
      <th>Priority</th>
      <td>{story_priority}</td>
    </tr>
    <tr>
      <th>Story Points</th>
      <td>{story_points}</td>
    </tr>
  </tbody>
</table>

<h2>📄 Description</h2>
<p>{story_description}</p>

<h2>✅ Subtasks ({len(subtasks)})</h2>
"""

            if subtasks:
                html_body += "<table>\n  <thead>\n    <tr>\n"
                html_body += "      <th>Key</th>\n"
                html_body += "      <th>Summary</th>\n"
                html_body += "      <th>Status</th>\n"
                html_body += "      <th>Estimate</th>\n"
                html_body += "    </tr>\n  </thead>\n  <tbody>\n"

                for task in subtasks:
                    task_key = task['key']
                    task_summary = task['fields']['summary']
                    task_status = task['fields']['status']['name']
                    estimate = task['fields'].get('timetracking', {}).get('originalEstimate', 'N/A')

                    html_body += f"""    <tr>
      <td><a href="{self.jira.base_url}/browse/{task_key}">{task_key}</a></td>
      <td>{task_summary}</td>
      <td>{task_status}</td>
      <td>{estimate}</td>
    </tr>
"""

                html_body += "  </tbody>\n</table>\n"
            else:
                html_body += "<p><em>No subtasks found.</em></p>\n"

            # Create page
            page_id = self.confluence.update_or_create_page(
                title=title,
                body=html_body,
                space_key=self.space_key
            )

            return page_id

        except Exception as e:
            print(f"❌ Error generating Story documentation: {e}")
            return None

    def generate_complete_project_documentation(self) -> Dict[str, str]:
        """Generate complete project documentation structure"""
        print("\n🚀 Generating Complete Project Documentation...")
        print("="*60)

        created_pages = {
            "overview": None,
            "epics": {},
            "stories": {}
        }

        # 1. Create project overview
        overview_id = self.generate_project_overview_page()
        created_pages["overview"] = overview_id

        # 2. Get all epics
        jql = f'project = {self.project_key} AND issuetype = "에픽"'
        epics = self.jira.search_issues(jql, max_results=50)

        print(f"\nFound {len(epics)} Epic(s)")

        # 3. Generate Epic pages
        for epic in epics:
            epic_key = epic['key']
            epic_page_id = self.generate_epic_documentation(epic_key)
            created_pages["epics"][epic_key] = epic_page_id

        # 4. Get all stories
        jql = f'project = {self.project_key} AND issuetype = "스토리"'
        stories = self.jira.search_issues(jql, max_results=100)

        print(f"\nFound {len(stories)} Story(ies)")

        # 5. Generate Story pages (limit to first 5 for demo)
        for story in stories[:5]:
            story_key = story['key']
            story_page_id = self.generate_story_documentation(story_key)
            created_pages["stories"][story_key] = story_page_id

        print("\n" + "="*60)
        print("✅ Documentation Generation Complete!")
        print("="*60)
        print(f"\nCreated Pages:")
        print(f"  - Overview: {created_pages['overview']}")
        print(f"  - Epics: {len(created_pages['epics'])}")
        print(f"  - Stories: {len(created_pages['stories'])}")

        return created_pages

    # ==================== Sprint Documentation ====================

    def generate_sprint_report_page(self) -> Optional[str]:
        """Generate current sprint report page"""
        print("\n📝 Generating Sprint Report Page...")

        report = self.jira.generate_sprint_report()

        title = f"{self.project_key} - Sprint Report - {datetime.now().strftime('%Y-%m-%d')}"

        html_body = f"""
<h1>Sprint Report - {datetime.now().strftime('%Y-%m-%d')}</h1>

<p><em>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</em></p>

<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p>This report is automatically generated from Jira data.</p>
  </ac:rich-text-body>
</ac:structured-macro>

<h2>📊 Sprint Summary</h2>
<table>
  <tbody>
    <tr>
      <th>Total Active Issues</th>
      <td>{report['summary']['total_active']}</td>
    </tr>
    <tr>
      <th>Blocked</th>
      <td style="color: {'red' if report['summary']['blocked_count'] > 0 else 'green'}">
        {report['summary']['blocked_count']}
      </td>
    </tr>
    <tr>
      <th>Overdue</th>
      <td style="color: {'red' if report['summary']['overdue_count'] > 0 else 'green'}">
        {report['summary']['overdue_count']}
      </td>
    </tr>
  </tbody>
</table>

<h2>Progress by Status</h2>
<table>
  <thead>
    <tr>
      <th>Status</th>
      <th>Count</th>
    </tr>
  </thead>
  <tbody>
"""

        for status, count in report['issues_by_status'].items():
            html_body += f"    <tr><th>{status}</th><td>{count}</td></tr>\n"

        html_body += "  </tbody>\n</table>\n"

        # Create page
        page_id = self.confluence.update_or_create_page(
            title=title,
            body=html_body,
            space_key=self.space_key
        )

        return page_id


def main():
    """Demo usage"""
    integration = JiraConfluenceIntegration(project_key="DIN", space_key="DIN")

    print("🚀 Jira-Confluence Integration")
    print("="*60)

    # Generate project overview
    integration.generate_project_overview_page()

    print("\n✅ Documentation generated in Confluence!")


if __name__ == "__main__":
    main()
