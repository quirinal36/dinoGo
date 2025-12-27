#!/usr/bin/env python3
"""
Test Jira issue creation with different description formats
"""

import os
from atlassian import Jira

def main():
    # Initialize Jira client
    jira_url = os.getenv("ATLASSIAN_SITE", "https://letscoding.atlassian.net")
    jira_email = os.getenv("ATLASSIAN_USER_EMAIL")
    jira_token = os.getenv("ATLASSIAN_API_TOKEN")

    if not jira_url.startswith("http"):
        jira_url = f"https://{jira_url}"

    jira = Jira(
        url=jira_url,
        username=jira_email,
        password=jira_token,
        cloud=True
    )

    project_key = "DIN"

    print("Testing different description formats...\n")

    # Test 1: Simple string description
    print("=" * 60)
    print("Test 1: Plain text description")
    print("=" * 60)

    try:
        fields = {
            "project": {"key": project_key},
            "summary": "TEST Epic - Plain Text Description",
            "description": "This is a simple plain text description for testing.",
            "issuetype": {"name": "에픽"},
            "priority": {"name": "Medium"}
        }

        result = jira.create_issue(fields=fields)
        print(f"✅ Success! Created: {result.get('key')}")
        print(f"   URL: {jira_url}/browse/{result.get('key')}\n")

        # Clean up - delete the test issue
        jira.delete_issue(result.get('key'))
        print(f"🗑️  Test issue deleted\n")

    except Exception as e:
        print(f"❌ Failed: {e}\n")

    # Test 2: ADF (Atlassian Document Format)
    print("=" * 60)
    print("Test 2: ADF format description")
    print("=" * 60)

    try:
        fields = {
            "project": {"key": project_key},
            "summary": "TEST Epic - ADF Description",
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This is ADF formatted description for testing."
                            }
                        ]
                    }
                ]
            },
            "issuetype": {"name": "에픽"},
            "priority": {"name": "Medium"}
        }

        result = jira.create_issue(fields=fields)
        print(f"✅ Success! Created: {result.get('key')}")
        print(f"   URL: {jira_url}/browse/{result.get('key')}\n")

        # Clean up
        jira.delete_issue(result.get('key'))
        print(f"🗑️  Test issue deleted\n")

    except Exception as e:
        print(f"❌ Failed: {e}\n")


if __name__ == "__main__":
    main()
