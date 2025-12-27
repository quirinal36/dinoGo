#!/usr/bin/env python3
"""
Compass Automation Manager
Service component management using Atlassian Compass GraphQL API
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from base64 import b64encode


class CompassAutomationManager:
    """Manages Compass components and metrics using GraphQL API"""

    def __init__(self):
        self._init_compass_client()

    def _init_compass_client(self):
        """Initialize Compass client with credentials"""
        self.site = os.getenv("ATLASSIAN_SITE", "letscoding.atlassian.net")
        self.email = os.getenv("ATLASSIAN_USER_EMAIL")
        self.token = os.getenv("ATLASSIAN_API_TOKEN")

        if not self.site.startswith("http"):
            self.base_url = f"https://{self.site}"
        else:
            self.base_url = self.site

        # GraphQL endpoint
        self.graphql_url = f"{self.base_url}/gateway/api/graphql"

        # REST API endpoint
        self.rest_url = f"{self.base_url}/gateway/api/compass"

        # Create auth header
        auth_string = f"{self.email}:{self.token}"
        auth_b64 = b64encode(auth_string.encode('ascii')).decode('ascii')
        self.headers = {
            'Authorization': f'Basic {auth_b64}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        self.cloud_id = None

    def _graphql_request(self, query: str, variables: Dict = None) -> Dict:
        """Execute GraphQL query"""
        payload = {
            "query": query,
            "variables": variables or {}
        }

        try:
            response = requests.post(
                self.graphql_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ GraphQL Error {response.status_code}: {response.text}")
                return {}

        except Exception as e:
            print(f"❌ Request error: {e}")
            return {}

    # ==================== Cloud ID Management ====================

    def get_cloud_id(self) -> Optional[str]:
        """Get Atlassian cloud ID for the site"""
        if self.cloud_id:
            return self.cloud_id

        query = """
        query getCloudId($hostName: String!) {
          tenantContexts(hostNames: [$hostName]) {
            cloudId
          }
        }
        """

        variables = {"hostName": self.site}

        result = self._graphql_request(query, variables)

        if result and 'data' in result:
            contexts = result['data'].get('tenantContexts', [])
            if contexts:
                self.cloud_id = contexts[0].get('cloudId')
                print(f"✅ Cloud ID: {self.cloud_id}")
                return self.cloud_id

        print(f"❌ Failed to retrieve Cloud ID")
        return None

    # ==================== Component Management ====================

    def create_component(self, name: str, component_type: str = "SERVICE",
                        description: str = None) -> Optional[str]:
        """
        Create a new Compass component

        Args:
            name: Component name
            component_type: One of: SERVICE, LIBRARY, APPLICATION, CAPABILITY,
                          CLOUD_RESOURCE, DATA_PIPELINE, MACHINE_LEARNING_MODEL,
                          UI_ELEMENT, WEBSITE, OTHER
            description: Optional description

        Returns:
            Component ID if successful
        """
        print(f"\n📦 Creating Component: {name}")

        # Ensure cloud ID is retrieved
        cloud_id = self.get_cloud_id()
        if not cloud_id:
            return None

        mutation = """
        mutation createComponent($cloudId: ID!, $componentDetails: CreateCompassComponentInput!) {
          compass {
            createComponent(cloudId: $cloudId, input: $componentDetails) {
              success
              errors {
                message
                extensions {
                  errorType
                }
              }
              componentDetails {
                id
                name
                typeId
                description
              }
            }
          }
        }
        """

        component_input = {
            "name": name,
            "typeId": component_type
        }

        if description:
            component_input["description"] = description

        variables = {
            "cloudId": cloud_id,
            "componentDetails": component_input
        }

        result = self._graphql_request(mutation, variables)

        if result and 'data' in result:
            create_result = result['data']['compass']['createComponent']

            if create_result['success']:
                component = create_result['componentDetails']
                comp_id = component['id']

                print(f"  ✅ Created: {component['name']}")
                print(f"     ID: {comp_id}")
                print(f"     Type: {component['typeId']}")

                return comp_id
            else:
                errors = create_result.get('errors', [])
                for error in errors:
                    print(f"  ❌ Error: {error['message']}")
                return None

        print(f"  ❌ Failed to create component")
        return None

    def get_components(self) -> List[Dict]:
        """Get all components"""
        cloud_id = self.get_cloud_id()
        if not cloud_id:
            return []

        query = """
        query getComponents($cloudId: ID!) {
          compass {
            searchComponents(cloudId: $cloudId, first: 100) {
              nodes {
                id
                name
                typeId
                description
                links {
                  url
                  type
                }
              }
            }
          }
        }
        """

        variables = {"cloudId": cloud_id}

        result = self._graphql_request(query, variables)

        if result and 'data' in result:
            nodes = result['data']['compass']['searchComponents']['nodes']
            return nodes

        return []

    def list_components(self):
        """List all components"""
        print("\n📦 Compass Components")
        print("="*60)

        components = self.get_components()

        if not components:
            print("No components found.")
            return

        for comp in components:
            print(f"\n🔧 {comp['name']}")
            print(f"   ID: {comp['id']}")
            print(f"   Type: {comp['typeId']}")
            if comp.get('description'):
                print(f"   Description: {comp['description'][:100]}")

    # ==================== Metrics Management ====================

    def send_metric(self, component_id: str, metric_name: str,
                   value: float, timestamp: str = None) -> bool:
        """
        Send metric value to component

        Args:
            component_id: Component ID
            metric_name: Metric name
            value: Metric value
            timestamp: ISO 8601 timestamp (default: now)

        Returns:
            Success boolean
        """
        if not timestamp:
            timestamp = datetime.utcnow().isoformat() + 'Z'

        url = f"{self.rest_url}/v1/metrics"

        payload = {
            "metricSourceId": component_id,
            "value": value,
            "timestamp": timestamp
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code in [200, 201, 204]:
                print(f"✅ Metric sent: {metric_name} = {value}")
                return True
            else:
                print(f"❌ Failed to send metric: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error sending metric: {e}")
            return False

    # ==================== Events Management ====================

    def send_deployment_event(self, component_id: str, environment: str,
                             state: str = "SUCCESSFUL") -> bool:
        """
        Send deployment event

        Args:
            component_id: Component ID
            environment: Environment (e.g., "production", "staging")
            state: SUCCESSFUL, FAILED, IN_PROGRESS, CANCELLED

        Returns:
            Success boolean
        """
        url = f"{self.rest_url}/v1/events"

        event = {
            "cloudId": self.get_cloud_id(),
            "event": {
                "deployment": {
                    "state": state,
                    "environment": {
                        "type": environment
                    },
                    "sequenceNumber": int(datetime.utcnow().timestamp()),
                    "updateSequenceNumber": int(datetime.utcnow().timestamp())
                }
            }
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=event,
                timeout=10
            )

            if response.status_code in [200, 201, 204]:
                print(f"✅ Deployment event sent: {environment} - {state}")
                return True
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    # ==================== Project Integration ====================

    def create_project_components_from_jira(self, project_key: str = "DIN"):
        """Create Compass components from Jira project structure"""
        print(f"\n🚀 Creating Compass Components from Jira Project: {project_key}")
        print("="*60)

        # Import Jira manager
        try:
            from jira_automation_manager import JiraAutomationManager
            jira = JiraAutomationManager(project_key)
        except:
            print("❌ Cannot import Jira manager")
            return

        # Get all epics
        jql = f'project = {project_key} AND issuetype = "에픽"'
        epics = jira.search_issues(jql, max_results=50)

        print(f"\nFound {len(epics)} Epic(s)")
        print(f"Creating corresponding Compass components...\n")

        created_components = []

        for epic in epics:
            epic_key = epic['key']
            epic_summary = epic['fields']['summary']
            epic_description = epic['fields'].get('description', '')

            # Create component for Epic
            component_name = f"{epic_key}: {epic_summary}"
            component_id = self.create_component(
                name=component_name,
                component_type="SERVICE",
                description=epic_description[:500]  # Limit description length
            )

            if component_id:
                created_components.append({
                    "epic_key": epic_key,
                    "component_id": component_id,
                    "name": component_name
                })

        print(f"\n✅ Created {len(created_components)} components")

        return created_components


def main():
    """Demo usage"""
    manager = CompassAutomationManager()

    print("🚀 Compass Automation Manager")
    print("="*60)

    # Get Cloud ID
    cloud_id = manager.get_cloud_id()

    if not cloud_id:
        print("\n❌ Failed to initialize Compass")
        print("   Check your credentials and Compass access")
        return

    # List existing components
    manager.list_components()


if __name__ == "__main__":
    main()
