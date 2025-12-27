#!/usr/bin/env python3
"""
Check Jira project configuration
"""

import os
import json
from atlassian import Jira

def main():
    # Initialize Jira client
    jira_url = os.getenv("ATLASSIAN_SITE", "https://letscoding.atlassian.net")
    jira_email = os.getenv("ATLASSIAN_USER_EMAIL")
    jira_token = os.getenv("ATLASSIAN_API_TOKEN")

    if not jira_url.startswith("http"):
        jira_url = f"https://{jira_url}"

    print(f"🔗 Connecting to: {jira_url}")
    print(f"👤 User: {jira_email}\n")

    jira = Jira(
        url=jira_url,
        username=jira_email,
        password=jira_token,
        cloud=True
    )

    project_key = "DIN"

    print("=" * 60)
    print(f"Project: {project_key}")
    print("=" * 60)

    # Get project metadata
    try:
        project = jira.project(project_key)
        print(f"\n✅ Project found: {project.get('name')}")
        print(f"   Key: {project.get('key')}")
        print(f"   Type: {project.get('projectTypeKey')}")
    except Exception as e:
        print(f"❌ Error getting project: {e}")
        return

    # Get issue types
    print("\n" + "=" * 60)
    print("Available Issue Types:")
    print("=" * 60)

    try:
        # Get issue types directly using REST API
        response = jira.get(f"rest/api/3/project/{project_key}")

        issue_types = response.get('issueTypes', [])

        for issue_type in issue_types:
            print(f"\n📋 {issue_type['name']}")
            print(f"   ID: {issue_type['id']}")
            print(f"   Description: {issue_type.get('description', 'N/A')}")
            print(f"   Subtask: {issue_type.get('subtask', False)}")
            print(f"   Hierarchy Level: {issue_type.get('hierarchyLevel', 'N/A')}")

    except Exception as e:
        print(f"❌ Error getting issue types: {e}")

    # Get custom fields
    print("\n" + "=" * 60)
    print("Custom Fields (looking for Story Points):")
    print("=" * 60)

    try:
        fields = jira.get_all_fields()

        # Look for story points field
        for field in fields:
            if 'story' in field['name'].lower() or 'point' in field['name'].lower():
                print(f"\n🔖 {field['name']}")
                print(f"   ID: {field['id']}")
                print(f"   Type: {field.get('schema', {}).get('type', 'N/A')}")

    except Exception as e:
        print(f"❌ Error getting fields: {e}")


if __name__ == "__main__":
    main()
