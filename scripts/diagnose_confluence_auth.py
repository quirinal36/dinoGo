#!/usr/bin/env python3
"""
Confluence Authentication Diagnostic Tool
Tests various authentication methods and provides detailed debugging
"""

import os
import sys
import requests
from base64 import b64encode


def test_basic_auth():
    """Test basic authentication with API token"""
    print("\n" + "="*60)
    print("Test 1: Basic Authentication (API Token)")
    print("="*60)

    site = os.getenv("ATLASSIAN_SITE", "letscoding.atlassian.net")
    email = os.getenv("ATLASSIAN_USER_EMAIL")
    token = os.getenv("ATLASSIAN_API_TOKEN")

    if not site.startswith("http"):
        base_url = f"https://{site}"
    else:
        base_url = site

    print(f"\n📍 Testing URL: {base_url}")
    print(f"👤 Email: {email}")
    print(f"🔑 Token: {'*' * 20}...{token[-4:] if token else 'NOT SET'}")

    # Create Basic Auth header
    auth_string = f"{email}:{token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = b64encode(auth_bytes).decode('ascii')

    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Test Confluence API v2 endpoint
    api_url = f"{base_url}/wiki/api/v2/spaces"

    print(f"\n🔗 Testing endpoint: {api_url}")

    try:
        response = requests.get(api_url, headers=headers, timeout=10)

        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📝 Response Headers:")
        for key, value in response.headers.items():
            if key.lower() in ['content-type', 'x-ausername', 'x-aaccountid']:
                print(f"   {key}: {value}")

        if response.status_code == 200:
            print(f"\n✅ SUCCESS! Authentication working correctly.")
            data = response.json()
            spaces = data.get('results', [])
            print(f"\n📚 Found {len(spaces)} space(s):")
            for space in spaces[:5]:  # Show first 5
                print(f"   - {space.get('key')}: {space.get('name')}")
            return True

        elif response.status_code == 401:
            print(f"\n❌ UNAUTHORIZED (401)")
            print(f"\nPossible causes:")
            print(f"   1. API token is invalid or expired")
            print(f"   2. Email doesn't match the token owner")
            print(f"   3. Token doesn't have Confluence permissions")
            print(f"\n💡 Solution: Regenerate API token with Confluence access")
            print(f"   URL: https://id.atlassian.com/manage-profile/security/api-tokens")

            # Try to get more details from response
            try:
                error_data = response.json()
                print(f"\n🔍 Error details:")
                print(f"   {error_data}")
            except:
                print(f"\n📄 Response body: {response.text[:200]}")

            return False

        elif response.status_code == 404:
            print(f"\n❌ NOT FOUND (404)")
            print(f"   Confluence may not be enabled on this site")
            print(f"   URL: {base_url}/wiki")
            return False

        else:
            print(f"\n⚠️  Unexpected status code: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        print(f"\n❌ TIMEOUT - Server not responding")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR - Cannot reach server")
        print(f"   Check if URL is correct: {base_url}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_atlassian_library():
    """Test using atlassian-python-api library"""
    print("\n" + "="*60)
    print("Test 2: Atlassian Python API Library")
    print("="*60)

    try:
        from atlassian import Confluence

        site = os.getenv("ATLASSIAN_SITE", "letscoding.atlassian.net")
        email = os.getenv("ATLASSIAN_USER_EMAIL")
        token = os.getenv("ATLASSIAN_API_TOKEN")

        if not site.startswith("http"):
            url = f"https://{site}"
        else:
            url = site

        print(f"\n📦 Testing with Confluence() class")
        print(f"   URL: {url}")
        print(f"   Username: {email}")
        print(f"   Cloud: True")

        confluence = Confluence(
            url=url,
            username=email,
            password=token,
            cloud=True
        )

        # Try to get spaces
        print(f"\n🔄 Calling get_all_spaces()...")
        result = confluence.get_all_spaces(start=0, limit=10)

        spaces = result.get('results', [])
        print(f"\n✅ SUCCESS! Found {len(spaces)} space(s):")
        for space in spaces:
            print(f"   - {space.get('key')}: {space.get('name')}")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"\n💡 This confirms the authentication issue")
        return False


def test_space_access(space_key: str = "DIN"):
    """Test access to specific space"""
    print("\n" + "="*60)
    print(f"Test 3: Access to '{space_key}' Space")
    print("="*60)

    site = os.getenv("ATLASSIAN_SITE", "letscoding.atlassian.net")
    email = os.getenv("ATLASSIAN_USER_EMAIL")
    token = os.getenv("ATLASSIAN_API_TOKEN")

    if not site.startswith("http"):
        base_url = f"https://{site}"
    else:
        base_url = site

    # Create auth header
    auth_string = f"{email}:{token}"
    auth_b64 = b64encode(auth_string.encode('ascii')).decode('ascii')

    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Accept': 'application/json'
    }

    api_url = f"{base_url}/wiki/api/v2/spaces/{space_key}"

    print(f"\n🔗 Testing: {api_url}")

    try:
        response = requests.get(api_url, headers=headers, timeout=10)

        print(f"📊 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Space found!")
            print(f"   Name: {data.get('name')}")
            print(f"   Key: {data.get('key')}")
            print(f"   Type: {data.get('type')}")
            return True
        elif response.status_code == 401:
            print(f"\n❌ Unauthorized - Authentication failed")
            return False
        elif response.status_code == 404:
            print(f"\n⚠️  Space '{space_key}' not found")
            print(f"   Create it at: {base_url}/wiki/spaces")
            return False
        else:
            print(f"\n⚠️  Status {response.status_code}: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def check_environment():
    """Check environment variables"""
    print("\n" + "="*60)
    print("Environment Variable Check")
    print("="*60)

    vars_to_check = [
        "ATLASSIAN_SITE",
        "ATLASSIAN_USER_EMAIL",
        "ATLASSIAN_API_TOKEN"
    ]

    all_set = True

    for var in vars_to_check:
        value = os.getenv(var)
        if value:
            if "TOKEN" in var:
                display_value = f"{'*' * 20}...{value[-4:]}"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
            all_set = False

    return all_set


def main():
    print("\n🔍 Confluence Authentication Diagnostic Tool")
    print("="*60)

    # Check environment
    if not check_environment():
        print("\n❌ Environment variables not properly set!")
        print("   Load from .mcp.json first")
        sys.exit(1)

    # Run tests
    results = []

    results.append(("Basic Auth", test_basic_auth()))
    results.append(("Python Library", test_atlassian_library()))
    results.append(("Space Access", test_space_access("DIN")))

    # Summary
    print("\n" + "="*60)
    print("📊 Diagnostic Summary")
    print("="*60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    # Recommendations
    print("\n" + "="*60)
    print("💡 Recommendations")
    print("="*60)

    if not any(r[1] for r in results):
        print("""
⚠️  All tests failed - API Token Issue

ACTION REQUIRED:
1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Create NEW API token with these settings:
   - Name: "Claude Code Automation"
   - Permissions: Full access to Jira AND Confluence
3. Copy the token immediately (you won't see it again!)
4. Update .mcp.json with new token
5. Reload environment and re-test

IMPORTANT: The token must be created by a user who has:
   - Confluence access enabled
   - View permissions on the DIN space
   - Admin rights (recommended)
        """)
    elif results[0][1] and not results[1][1]:
        print("""
✅ Authentication works but Python library has issues

SOLUTION:
   The library may need updated configuration.
   Try using direct requests instead of Confluence() class.
        """)
    else:
        print("\n✅ Authentication working! You can now use Confluence automation.")


if __name__ == "__main__":
    main()
