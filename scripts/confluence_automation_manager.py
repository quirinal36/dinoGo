#!/usr/bin/env python3
"""
Confluence Automation Manager
Comprehensive automation system for Confluence document management using Atlassian API
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from atlassian import Confluence


class ConfluenceAutomationManager:
    """Manages automated Confluence workflows and operations"""

    def __init__(self, space_key: str = "DIN"):
        self.space_key = space_key
        self._init_confluence_client()

    def _init_confluence_client(self):
        """Initialize Confluence client with credentials"""
        confluence_url = os.getenv("ATLASSIAN_SITE", "https://letscoding.atlassian.net")
        confluence_email = os.getenv("ATLASSIAN_USER_EMAIL")
        confluence_token = os.getenv("ATLASSIAN_API_TOKEN")

        if not confluence_url.startswith("http"):
            confluence_url = f"https://{confluence_url}"

        self.confluence = Confluence(
            url=confluence_url,
            username=confluence_email,
            password=confluence_token,
            cloud=True
        )
        self.base_url = confluence_url

    # ==================== Space Management ====================

    def get_all_spaces(self, limit: int = 100) -> List[Dict]:
        """Get all accessible spaces"""
        try:
            result = self.confluence.get_all_spaces(start=0, limit=limit, expand='description.plain,homepage')
            return result.get('results', [])
        except Exception as e:
            print(f"❌ Error getting spaces: {e}")
            return []

    def get_space_info(self, space_key: str = None) -> Optional[Dict]:
        """Get detailed space information"""
        if not space_key:
            space_key = self.space_key

        try:
            space = self.confluence.get_space(space_key, expand='description.plain,homepage')
            return space
        except Exception as e:
            print(f"❌ Error getting space info: {e}")
            return None

    def list_spaces(self):
        """List all accessible spaces"""
        print("\n📚 Available Confluence Spaces")
        print("="*60)

        spaces = self.get_all_spaces()

        if not spaces:
            print("No spaces found or access denied.")
            return

        for space in spaces:
            key = space.get('key', 'N/A')
            name = space.get('name', 'N/A')
            space_type = space.get('type', 'N/A')

            print(f"\n🗂️  {key}: {name}")
            print(f"   Type: {space_type}")

    # ==================== Page Management ====================

    def get_all_pages(self, space_key: str = None, limit: int = 100) -> List[Dict]:
        """Get all pages from a space"""
        if not space_key:
            space_key = self.space_key

        try:
            pages = self.confluence.get_all_pages_from_space(
                space=space_key,
                start=0,
                limit=limit,
                content_type='page'
            )
            return pages
        except Exception as e:
            print(f"❌ Error getting pages: {e}")
            return []

    def page_exists(self, title: str, space_key: str = None) -> bool:
        """Check if a page exists"""
        if not space_key:
            space_key = self.space_key

        return self.confluence.page_exists(space=space_key, title=title)

    def get_page_by_title(self, title: str, space_key: str = None) -> Optional[Dict]:
        """Get page by title"""
        if not space_key:
            space_key = self.space_key

        try:
            page = self.confluence.get_page_by_title(space=space_key, title=title)
            if page:
                return page
            return None
        except Exception as e:
            print(f"❌ Error getting page: {e}")
            return None

    def get_page_by_id(self, page_id: str, expand: str = 'body.storage,version') -> Optional[Dict]:
        """Get page by ID"""
        try:
            return self.confluence.get_page_by_id(page_id=page_id, expand=expand)
        except Exception as e:
            print(f"❌ Error getting page by ID: {e}")
            return None

    # ==================== Page Creation & Updates ====================

    def create_page(self, title: str, body: str, space_key: str = None,
                   parent_id: str = None) -> Optional[str]:
        """
        Create a new Confluence page

        Args:
            title: Page title
            body: Page content in storage format (HTML)
            space_key: Target space (default: self.space_key)
            parent_id: Optional parent page ID for hierarchy

        Returns:
            Created page ID or None
        """
        if not space_key:
            space_key = self.space_key

        try:
            result = self.confluence.create_page(
                space=space_key,
                title=title,
                body=body,
                parent_id=parent_id,
                type='page',
                representation='storage'
            )

            page_id = result.get('id')
            print(f"✅ Created page: {title} (ID: {page_id})")
            print(f"   URL: {self.base_url}/wiki/spaces/{space_key}/pages/{page_id}")

            return page_id

        except Exception as e:
            print(f"❌ Error creating page: {e}")
            return None

    def update_page(self, page_id: str, title: str, body: str,
                   minor_edit: bool = False) -> bool:
        """Update existing page"""
        try:
            self.confluence.update_page(
                page_id=page_id,
                title=title,
                body=body,
                minor_edit=minor_edit
            )

            print(f"✅ Updated page: {title} (ID: {page_id})")
            return True

        except Exception as e:
            print(f"❌ Error updating page: {e}")
            return False

    def update_or_create_page(self, title: str, body: str, space_key: str = None,
                             parent_id: str = None) -> Optional[str]:
        """Create page if it doesn't exist, otherwise update it"""
        if not space_key:
            space_key = self.space_key

        try:
            # Check if page exists
            existing_page = self.get_page_by_title(title, space_key)

            if existing_page:
                # Update existing page
                page_id = existing_page['id']
                self.update_page(page_id, title, body)
                return page_id
            else:
                # Create new page
                return self.create_page(title, body, space_key, parent_id)

        except Exception as e:
            print(f"❌ Error in update_or_create: {e}")
            return None

    def delete_page(self, page_id: str) -> bool:
        """Delete a page"""
        try:
            self.confluence.remove_page(page_id)
            print(f"✅ Deleted page ID: {page_id}")
            return True
        except Exception as e:
            print(f"❌ Error deleting page: {e}")
            return False

    # ==================== Search ====================

    def search_pages(self, query: str, space_key: str = None, limit: int = 25) -> List[Dict]:
        """
        Search pages using CQL (Confluence Query Language)

        Example queries:
        - "type=page AND space=DIN AND title~'test'"
        - "type=page AND label='documentation'"
        - "type=page AND created >= '2025-01-01'"
        """
        if space_key:
            cql = f"type=page AND space={space_key} AND {query}"
        else:
            cql = f"type=page AND {query}"

        try:
            results = self.confluence.cql(cql=cql, limit=limit)
            return results.get('results', [])
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

    def find_pages_by_label(self, label: str, limit: int = 50) -> List[Dict]:
        """Find all pages with specific label"""
        try:
            return self.confluence.get_all_pages_by_label(
                label=label,
                start=0,
                limit=limit
            )
        except Exception as e:
            print(f"❌ Error finding pages by label: {e}")
            return []

    # ==================== Labels ====================

    def add_label(self, page_id: str, label: str) -> bool:
        """Add label to page"""
        try:
            self.confluence.set_page_label(page_id, label)
            print(f"✅ Added label '{label}' to page {page_id}")
            return True
        except Exception as e:
            print(f"❌ Error adding label: {e}")
            return False

    def get_page_labels(self, page_id: str) -> List[str]:
        """Get all labels on a page"""
        try:
            result = self.confluence.get_page_labels(page_id)
            return [label['name'] for label in result.get('results', [])]
        except Exception as e:
            print(f"❌ Error getting labels: {e}")
            return []

    # ==================== Attachments ====================

    def attach_file(self, page_id: str, filepath: str) -> bool:
        """Attach file to page"""
        try:
            self.confluence.attach_file(
                filename=filepath,
                page_id=page_id
            )
            print(f"✅ Attached {filepath} to page {page_id}")
            return True
        except Exception as e:
            print(f"❌ Error attaching file: {e}")
            return False

    def get_attachments(self, page_id: str) -> List[Dict]:
        """Get all attachments from page"""
        try:
            result = self.confluence.get_attachments_from_content(page_id)
            return result.get('results', [])
        except Exception as e:
            print(f"❌ Error getting attachments: {e}")
            return []

    # ==================== Template Operations ====================

    def create_page_from_template(self, title: str, template_html: str,
                                  space_key: str = None, parent_id: str = None) -> Optional[str]:
        """Create page using HTML template"""
        return self.create_page(title, template_html, space_key, parent_id)

    # ==================== Utility ====================

    def export_page_to_pdf(self, page_id: str, output_path: str = None) -> bool:
        """Export page as PDF"""
        try:
            pdf_content = self.confluence.export_page(page_id)

            if not output_path:
                output_path = f"exports/page_{page_id}.pdf"

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(pdf_content)

            print(f"✅ Exported PDF to: {output_path}")
            return True

        except Exception as e:
            print(f"❌ Error exporting PDF: {e}")
            return False

    def list_pages_in_space(self, space_key: str = None):
        """List all pages in space"""
        if not space_key:
            space_key = self.space_key

        print(f"\n📄 Pages in Space: {space_key}")
        print("="*60)

        pages = self.get_all_pages(space_key)

        if not pages:
            print("No pages found in this space.")
            return

        for page in pages:
            page_id = page.get('id')
            title = page.get('title')
            page_type = page.get('type')

            print(f"\n📝 {title}")
            print(f"   ID: {page_id}")
            print(f"   Type: {page_type}")
            print(f"   URL: {self.base_url}/wiki/spaces/{space_key}/pages/{page_id}")

    # ==================== Reporting ====================

    def generate_space_report(self, space_key: str = None) -> Dict:
        """Generate comprehensive space report"""
        if not space_key:
            space_key = self.space_key

        print(f"\n📊 Generating Space Report for: {space_key}")

        report = {
            "space_key": space_key,
            "generated_at": datetime.now().isoformat(),
            "space_info": {},
            "pages": [],
            "summary": {}
        }

        # Get space info
        space_info = self.get_space_info(space_key)
        if space_info:
            report['space_info'] = {
                "name": space_info.get('name'),
                "type": space_info.get('type'),
                "key": space_info.get('key')
            }

        # Get all pages
        pages = self.get_all_pages(space_key, limit=500)
        report['pages'] = [
            {
                "id": p.get('id'),
                "title": p.get('title'),
                "type": p.get('type')
            }
            for p in pages
        ]

        # Summary
        report['summary'] = {
            "total_pages": len(pages),
            "page_types": {}
        }

        # Count by type
        for page in pages:
            page_type = page.get('type', 'unknown')
            report['summary']['page_types'][page_type] = \
                report['summary']['page_types'].get(page_type, 0) + 1

        return report

    def print_space_dashboard(self, space_key: str = None):
        """Print space dashboard"""
        if not space_key:
            space_key = self.space_key

        print("\n" + "="*60)
        print(f"📚 Confluence Space Dashboard: {space_key}")
        print("="*60)

        report = self.generate_space_report(space_key)

        if report['space_info']:
            print(f"\n📖 Space: {report['space_info']['name']}")
            print(f"   Type: {report['space_info']['type']}")

        print(f"\n📊 Summary:")
        print(f"  Total Pages: {report['summary']['total_pages']}")

        if report['summary']['page_types']:
            print(f"\n📄 By Type:")
            for page_type, count in report['summary']['page_types'].items():
                print(f"  {page_type}: {count}")

    def export_report_json(self, space_key: str = None, filename: str = None):
        """Export space report to JSON"""
        if not space_key:
            space_key = self.space_key

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/confluence_report_{space_key}_{timestamp}.json"

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        report = self.generate_space_report(space_key)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Report exported to: {filename}")


def main():
    """Demo usage"""
    manager = ConfluenceAutomationManager(space_key="DIN")

    print("🚀 Confluence Automation Manager")
    print("="*60)

    # List available spaces
    manager.list_spaces()

    # Display space dashboard (if space exists)
    try:
        manager.print_space_dashboard()
    except:
        print("\n⚠️  Space 'DIN' may not exist yet in Confluence")


if __name__ == "__main__":
    main()
