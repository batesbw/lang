#!/usr/bin/env python3
"""
Debug script to test JWT Bearer Flow authentication directly with simple-salesforce.
This will help us identify the exact issue with the authentication.
"""

import os
from dotenv import load_dotenv
from simple_salesforce import Salesforce

# Load environment variables
load_dotenv()

def test_jwt_auth():
    """Test JWT Bearer Flow authentication with detailed error reporting."""
    print("🔍 Testing JWT Bearer Flow Authentication")
    print("=" * 50)
    
    # Get environment variables
    org_alias = "E2E_TEST_ORG"
    username = os.getenv(f"SF_USERNAME_{org_alias}")
    consumer_key = os.getenv(f"SF_CONSUMER_KEY_{org_alias}")
    private_key_file = os.getenv(f"SF_PRIVATE_KEY_FILE_{org_alias}")
    instance_url = os.getenv(f"SF_INSTANCE_URL_{org_alias}")
    
    print(f"📋 Configuration:")
    print(f"   Username: {username}")
    print(f"   Consumer Key: {consumer_key[:20]}..." if consumer_key else "   Consumer Key: None")
    print(f"   Private Key File: {private_key_file}")
    print(f"   Instance URL: {instance_url}")
    
    # Check if private key file exists
    if not private_key_file or not os.path.exists(private_key_file):
        print(f"❌ Private key file not found: {private_key_file}")
        return
    
    print(f"✅ Private key file exists")
    
    # Check file permissions
    import stat
    file_stat = os.stat(private_key_file)
    file_mode = stat.filemode(file_stat.st_mode)
    print(f"   File permissions: {file_mode}")
    
    # Try to read the private key file
    try:
        with open(private_key_file, 'r') as f:
            key_content = f.read()
            print(f"✅ Private key file readable ({len(key_content)} characters)")
            if key_content.startswith('-----BEGIN'):
                print("✅ Private key format looks correct")
            else:
                print("❌ Private key format may be incorrect")
    except Exception as e:
        print(f"❌ Error reading private key file: {e}")
        return
    
    print(f"\n🔐 Attempting JWT Bearer Flow authentication...")
    
    try:
        # Attempt authentication
        sf_kwargs = {
            'username': username,
            'consumer_key': consumer_key,
            'privatekey_file': private_key_file
        }
        
        # Add domain if it's a sandbox
        if instance_url and 'sandbox' in instance_url.lower():
            print("🏖️  Detected sandbox - setting domain to 'test'")
            sf_kwargs['domain'] = 'test'
        
        print(f"🚀 Connecting to Salesforce...")
        sf = Salesforce(**sf_kwargs)
        
        print(f"✅ Authentication successful!")
        print(f"   Session ID: {sf.session_id[:20]}...")
        print(f"   Instance URL: {sf.sf_instance}")
        print(f"   User ID: {sf.user_id if hasattr(sf, 'user_id') and sf.user_id else 'Available'}")
        
        # Test a simple query with correct SOQL syntax
        print(f"\n🧪 Testing API access...")
        result = sf.query("SELECT Id, Name FROM User LIMIT 1")
        if result['records']:
            print(f"✅ API test successful - Found user: {result['records'][0]['Name']}")
        else:
            print(f"✅ API test successful - Query executed (no records returned)")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        
        # Provide specific troubleshooting based on error
        error_str = str(e).lower()
        print(f"\n🔧 Troubleshooting suggestions:")
        
        if "invalid_grant" in error_str:
            print("   • Check that the certificate uploaded to Salesforce matches the private key")
            print("   • Verify the Consumer Key is correct")
            print("   • Ensure the user is pre-authorized for the Connected App")
            print("   • Check that JWT Bearer Flow is enabled in the Connected App")
        elif "invalid_client" in error_str:
            print("   • Verify the Consumer Key is correct")
            print("   • Check that the Connected App exists and is active")
        elif "private key" in error_str:
            print("   • Check the private key file format")
            print("   • Ensure the private key matches the uploaded certificate")
        
        return False

if __name__ == "__main__":
    test_jwt_auth() 