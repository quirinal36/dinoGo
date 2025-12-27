#!/usr/bin/env python3
"""
Jira Automation Manager
Comprehensive automation system for Jira project management using Atlassian API
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from base64 import b64encode
from atlassian import Jira


class JiraAutomationManager:
    """Manages automated Jira workflows and operations"""

    def __init__(self, project_key: str = "DIN"):
        self.project_key = project_key
        self._init_jira_client()

    def _init_jira_client(self):
        """Initialize Jira client with credentials"""
        jira_url = os.getenv("ATLASSIAN_SITE", "https://letscoding.atlassian.net")
        jira_email = os.getenv("ATLASSIAN_USER_EMAIL")
        jira_token = os.getenv("ATLASSIAN_API_TOKEN")

        if not jira_url.startswith("http"):
            jira_url = f"https://{jira_url}"

        self.jira = Jira(
            url=jira_url,
            username=jira_email,
            password=jira_token,
            cloud=True
        )
        self.base_url = jira_url

        # Setup auth for direct API calls
        auth_string = f"{jira_email}:{jira_token}"
        self.auth_header = b64encode(auth_string.encode('ascii')).decode('ascii')
        self.headers = {
            'Authorization': f'Basic {self.auth_header}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    # ==================== Search & Query ====================

    def search_issues(self, jql: str, max_results: int = 50) -> List[Dict]:
        """
        Search Jira issues using JQL

        Example JQL:
        - "project = DIN AND status = 'In Progress'"
        - "assignee = currentUser() AND status != Done"
        - "created >= -7d ORDER BY created DESC"
        """
        try:
            # Use new JQL API endpoint (v3) with direct requests
            url = f"{self.base_url}/rest/api/3/search/jql"
            params = {
                "jql": jql,
                "maxResults": max_results,
                "fields": "*all"
            }
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json().get('issues', [])
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

    def get_epic_stories(self, epic_key: str) -> List[Dict]:
        """Get all stories under an Epic"""
        jql = f'parent = "{epic_key}" AND issuetype = "스토리"'
        return self.search_issues(jql)

    def get_story_subtasks(self, story_key: str) -> List[Dict]:
        """Get all subtasks under a Story"""
        jql = f'parent = "{story_key}" AND issuetype = "하위 작업"'
        return self.search_issues(jql)

    def find_blocked_issues(self) -> List[Dict]:
        """Find issues with 'Blocked' status or flag"""
        jql = f'project = {self.project_key} AND (status = Blocked OR flagged = Impediment)'
        return self.search_issues(jql)

    def find_overdue_issues(self) -> List[Dict]:
        """Find issues past due date"""
        jql = f'project = {self.project_key} AND duedate < now() AND status != Done'
        return self.search_issues(jql)

    def find_unassigned_issues(self) -> List[Dict]:
        """Find unassigned issues"""
        jql = f'project = {self.project_key} AND assignee is EMPTY AND status != Done'
        return self.search_issues(jql)

    # ==================== Issue Management ====================

    def transition_issue(self, issue_key: str, transition_name: str) -> bool:
        """
        Transition issue to new status

        Common transitions:
        - "To Do" / "In Progress" / "Done"
        - "Open" / "In Review" / "Closed"
        """
        try:
            # Get available transitions
            transitions = self.jira.get_issue_transitions(issue_key)

            # Find matching transition
            transition_id = None
            for trans in transitions['transitions']:
                if trans['name'].lower() == transition_name.lower():
                    transition_id = trans['id']
                    break

            if not transition_id:
                print(f"⚠️  Transition '{transition_name}' not found for {issue_key}")
                return False

            # Execute transition
            self.jira.set_issue_status(issue_key, transition_id)
            print(f"✅ {issue_key} → {transition_name}")
            return True

        except Exception as e:
            print(f"❌ Transition error: {e}")
            return False

    def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> bool:
        """
        Update issue fields

        Example fields:
        - {"summary": "New title"}
        - {"description": "Updated description"}
        - {"priority": {"name": "High"}}
        - {"assignee": {"accountId": "123456"}}
        """
        try:
            self.jira.update_issue_field(issue_key, fields)
            print(f"✅ Updated {issue_key}")
            return True
        except Exception as e:
            print(f"❌ Update error: {e}")
            return False

    def add_comment(self, issue_key: str, comment: str) -> bool:
        """Add comment to issue"""
        try:
            self.jira.issue_add_comment(issue_key, comment)
            print(f"✅ Comment added to {issue_key}")
            return True
        except Exception as e:
            print(f"❌ Comment error: {e}")
            return False

    def assign_issue(self, issue_key: str, account_id: str) -> bool:
        """Assign issue to user"""
        return self.update_issue(issue_key, {"assignee": {"accountId": account_id}})

    # ==================== Bulk Operations ====================

    def bulk_transition(self, issue_keys: List[str], transition_name: str):
        """Bulk transition multiple issues"""
        print(f"\n🔄 Bulk transitioning {len(issue_keys)} issues to '{transition_name}'")

        success = 0
        for key in issue_keys:
            if self.transition_issue(key, transition_name):
                success += 1

        print(f"\n✅ Successfully transitioned {success}/{len(issue_keys)} issues")

    def bulk_update_priority(self, jql: str, priority: str):
        """Update priority for all issues matching JQL"""
        issues = self.search_issues(jql)
        print(f"\n🔄 Updating priority to '{priority}' for {len(issues)} issues")

        for issue in issues:
            issue_key = issue['key']
            self.update_issue(issue_key, {"priority": {"name": priority}})

    # ==================== Automated Workflows ====================

    def auto_close_completed_subtasks(self):
        """Automatically close subtasks when all work is done"""
        print("\n🤖 Auto-closing completed subtasks...")

        # Find subtasks in review/testing that might be ready to close
        jql = f'project = {self.project_key} AND issuetype = "하위 작업" AND status = "In Review"'
        issues = self.search_issues(jql)

        for issue in issues:
            issue_key = issue['key']
            # Add logic here to check if ready to close
            # For now, just report
            print(f"  📋 {issue_key}: {issue['fields']['summary']}")

    def auto_flag_overdue_issues(self):
        """Automatically flag overdue issues"""
        print("\n🚩 Flagging overdue issues...")

        overdue = self.find_overdue_issues()

        for issue in overdue:
            issue_key = issue['key']
            comment = f"⚠️ This issue is overdue. Due date was: {issue['fields'].get('duedate', 'Not set')}"
            self.add_comment(issue_key, comment)
            print(f"  🚩 {issue_key} flagged as overdue")

    def auto_assign_unassigned(self, default_assignee_id: str):
        """Auto-assign unassigned high-priority issues"""
        print("\n👤 Auto-assigning unassigned issues...")

        jql = f'project = {self.project_key} AND assignee is EMPTY AND priority = High AND status != Done'
        issues = self.search_issues(jql)

        for issue in issues:
            issue_key = issue['key']
            self.assign_issue(issue_key, default_assignee_id)

    # ==================== Reporting ====================

    def generate_sprint_report(self) -> Dict:
        """Generate current sprint progress report"""
        print("\n📊 Generating Sprint Report...")

        report = {
            "project": self.project_key,
            "generated_at": datetime.now().isoformat(),
            "summary": {},
            "epics": [],
            "issues_by_status": {},
            "issues_by_priority": {},
            "blocked": [],
            "overdue": []
        }

        # Get all active issues
        jql = f'project = {self.project_key} AND status != Done'
        all_issues = self.search_issues(jql, max_results=200)

        # Count by status
        for issue in all_issues:
            status = issue['fields']['status']['name']
            report['issues_by_status'][status] = report['issues_by_status'].get(status, 0) + 1

            priority = issue['fields']['priority']['name']
            report['issues_by_priority'][priority] = report['issues_by_priority'].get(priority, 0) + 1

        # Find blocked and overdue
        report['blocked'] = [issue['key'] for issue in self.find_blocked_issues()]
        report['overdue'] = [issue['key'] for issue in self.find_overdue_issues()]

        report['summary'] = {
            "total_active": len(all_issues),
            "blocked_count": len(report['blocked']),
            "overdue_count": len(report['overdue'])
        }

        return report

    def print_project_health(self):
        """Print project health dashboard"""
        print("\n" + "="*60)
        print(f"📊 {self.project_key} Project Health Dashboard")
        print("="*60)

        report = self.generate_sprint_report()

        print(f"\n📈 Summary:")
        print(f"  Total Active Issues: {report['summary']['total_active']}")
        print(f"  Blocked Issues: {report['summary']['blocked_count']}")
        print(f"  Overdue Issues: {report['summary']['overdue_count']}")

        print(f"\n📊 By Status:")
        for status, count in sorted(report['issues_by_status'].items()):
            print(f"  {status}: {count}")

        print(f"\n🎯 By Priority:")
        for priority, count in sorted(report['issues_by_priority'].items()):
            print(f"  {priority}: {count}")

        if report['blocked']:
            print(f"\n🚧 Blocked Issues:")
            for key in report['blocked']:
                print(f"  - {key}")

        if report['overdue']:
            print(f"\n⏰ Overdue Issues:")
            for key in report['overdue']:
                print(f"  - {key}")

    def export_report_json(self, filename: str = None):
        """Export report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/jira_report_{self.project_key}_{timestamp}.json"

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        report = self.generate_sprint_report()

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Report exported to: {filename}")


def main():
    """Demo usage"""
    manager = JiraAutomationManager(project_key="DIN")

    print("🚀 Jira Automation Manager")
    print("="*60)

    # Display project health
    manager.print_project_health()

    # Export report
    manager.export_report_json()


if __name__ == "__main__":
    main()
