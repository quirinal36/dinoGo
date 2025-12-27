#!/usr/bin/env python3
"""
Jira CSV Import Script
Imports Epics, Stories, and Sub-tasks to Jira using Atlassian API
"""

import csv
import json
import os
import sys
from typing import Dict, List, Optional
import time
from atlassian import Jira

class JiraImporter:
    def __init__(self, project_key: str = "DIN"):
        self.project_key = project_key
        self.epic_map: Dict[str, str] = {}  # Epic Summary -> Epic Key
        self.story_map: Dict[str, str] = {}  # Story Summary -> Story Key

        # Initialize Jira client from environment variables
        jira_url = os.getenv("ATLASSIAN_SITE", "https://letscoding.atlassian.net")
        jira_email = os.getenv("ATLASSIAN_USER_EMAIL")
        jira_token = os.getenv("ATLASSIAN_API_TOKEN")

        if not jira_url.startswith("http"):
            jira_url = f"https://{jira_url}"

        print(f"🔗 Connecting to Jira: {jira_url}")
        print(f"👤 User: {jira_email}")

        self.jira = Jira(
            url=jira_url,
            username=jira_email,
            password=jira_token,
            cloud=True
        )

    def create_epic(self, summary: str, description: str, priority: str) -> Optional[str]:
        """Create an Epic in Jira"""
        print(f"Creating Epic: {summary[:50]}...")

        try:
            # Jira Cloud uses Epic as a regular issue type
            # Korean Jira uses "에픽" instead of "Epic"
            # Use plain text description (ADF not supported in this project)
            fields = {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": description,  # Plain text format
                "issuetype": {"name": "에픽"},
                "priority": {"name": priority}
            }

            result = self.jira.create_issue(fields=fields)
            epic_key = result.get("key")

            print(f"  ✅ Created: {epic_key}")
            print(f"  - Priority: {priority}")
            print(f"  - Description: {len(description)} chars")

            return epic_key

        except Exception as e:
            print(f"  ❌ Error creating epic: {e}")
            return None

    def create_story(self, summary: str, description: str, priority: str,
                    story_points: Optional[int], epic_link: str) -> Optional[str]:
        """Create a Story in Jira and link to Epic"""
        print(f"Creating Story: {summary[:50]}...")

        epic_key = self.epic_map.get(epic_link)
        if not epic_key:
            print(f"  ⚠️  Warning: Epic '{epic_link}' not found")

        try:
            # Korean Jira uses "스토리" instead of "Story"
            # Use plain text description
            fields = {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": description,  # Plain text format
                "issuetype": {"name": "스토리"},
                "priority": {"name": priority}
            }

            # Link to Epic (parent relationship in Jira Cloud)
            if epic_key:
                fields["parent"] = {"key": epic_key}

            # Story Points - common field ID, may need adjustment
            if story_points:
                fields["customfield_10016"] = story_points

            result = self.jira.create_issue(fields=fields)
            story_key = result.get("key")

            print(f"  ✅ Created: {story_key}")
            print(f"  - Priority: {priority}")
            print(f"  - Story Points: {story_points}")
            print(f"  - Epic: {epic_key}")

            return story_key

        except Exception as e:
            print(f"  ❌ Error creating story: {e}")
            return None

    def create_subtask(self, summary: str, description: str, priority: str,
                      estimate: str, parent: str) -> Optional[str]:
        """Create a Sub-task in Jira and link to parent Story"""
        print(f"Creating Sub-task: {summary[:40]}...")

        parent_key = self.story_map.get(parent)
        if not parent_key:
            print(f"  ⚠️  Warning: Parent '{parent}' not found")
            return None

        try:
            # Korean Jira uses "하위 작업" instead of "Sub-task"
            # Use plain text description
            fields = {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": description,  # Plain text format
                "issuetype": {"name": "하위 작업"},
                "priority": {"name": priority},
                "parent": {"key": parent_key}
            }

            # Original estimate
            if estimate:
                fields["timetracking"] = {"originalEstimate": estimate}

            result = self.jira.create_issue(fields=fields)
            subtask_key = result.get("key")

            print(f"  ✅ Created: {subtask_key}")
            print(f"  - Parent: {parent_key}")
            print(f"  - Estimate: {estimate}")

            return subtask_key

        except Exception as e:
            print(f"  ❌ Error creating subtask: {e}")
            return None

    def import_epics(self, csv_path: str):
        """Import all Epics from CSV"""
        print("\n" + "="*60)
        print("PHASE 1: Importing Epics")
        print("="*60)

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                summary = row['Summary']
                description = row['Description']
                priority = row['Priority']

                epic_key = self.create_epic(summary, description, priority)

                if epic_key:
                    self.epic_map[summary] = epic_key
                    print()
                    time.sleep(1)  # Rate limiting

    def import_stories(self, csv_path: str):
        """Import all Stories from CSV"""
        print("\n" + "="*60)
        print("PHASE 2: Importing Stories")
        print("="*60)

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                summary = row['Summary']
                description = row['Description']
                priority = row['Priority']
                story_points = int(row['Story Points']) if row['Story Points'] else None
                epic_link = row['Epic Link']

                story_key = self.create_story(summary, description, priority,
                                             story_points, epic_link)

                if story_key:
                    self.story_map[summary] = story_key
                    print()
                    time.sleep(1)  # Rate limiting

    def import_subtasks(self, csv_path: str):
        """Import all Sub-tasks from CSV"""
        print("\n" + "="*60)
        print("PHASE 3: Importing Sub-tasks")
        print("="*60)

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                summary = row['Summary']
                description = row['Description']
                priority = row['Priority']
                estimate = row['Original Estimate']
                parent = row['Parent']

                subtask_key = self.create_subtask(summary, description, priority,
                                                  estimate, parent)

                if subtask_key:
                    print()
                    time.sleep(0.5)  # Rate limiting

    def run_import(self, epics_csv: str, stories_csv: str, tasks_csv: str):
        """Execute full import process"""
        print("🚀 Starting Jira Import Process")
        print(f"Project: {self.project_key}")
        print(f"Epics CSV: {epics_csv}")
        print(f"Stories CSV: {stories_csv}")
        print(f"Tasks CSV: {tasks_csv}")

        # Phase 1: Import Epics
        self.import_epics(epics_csv)

        # Phase 2: Import Stories
        self.import_stories(stories_csv)

        # Phase 3: Import Sub-tasks
        self.import_subtasks(tasks_csv)

        print("\n" + "="*60)
        print("✅ Import Complete!")
        print("="*60)
        print(f"Epics created: {len(self.epic_map)}")
        print(f"Stories created: {len(self.story_map)}")
        print("\nEpic Mapping:")
        for summary, key in self.epic_map.items():
            print(f"  {key}: {summary}")


def main():
    # File paths
    base_path = "/home/ubuntu/dinoGo/docs/agile"
    epics_csv = f"{base_path}/jira_import_epics.csv"
    stories_csv = f"{base_path}/jira_import_stories.csv"
    tasks_csv = f"{base_path}/jira_import_tasks.csv"

    # Verify files exist
    for path in [epics_csv, stories_csv, tasks_csv]:
        if not os.path.exists(path):
            print(f"❌ Error: File not found: {path}")
            sys.exit(1)

    # Run import
    importer = JiraImporter(project_key="DIN")
    importer.run_import(epics_csv, stories_csv, tasks_csv)


if __name__ == "__main__":
    main()
