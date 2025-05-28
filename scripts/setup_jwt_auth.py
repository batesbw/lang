#!/usr/bin/env python3
"""
Helper script to generate private key and certificate for Salesforce JWT Bearer Flow authentication.

This script creates the necessary cryptographic files needed for secure server-to-server
authentication with Salesforce using OAuth JWT Bearer Flow.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        sys.exit(1)

def main():
    """Generate private key and certificate for JWT Bearer Flow."""
    print("🚀 Setting up JWT Bearer Flow authentication for Salesforce")
    print("=" * 60)
    
    # Create certs directory if it doesn't exist
    certs_dir = Path("certs")
    certs_dir.mkdir(exist_ok=True)
    
    # File paths
    private_key_file = certs_dir / "private_key.pem"
    csr_file = certs_dir / "certificate.csr"
    cert_file = certs_dir / "certificate.crt"
    
    # Check if files already exist
    if private_key_file.exists():
        response = input(f"⚠️  Private key already exists at {private_key_file}. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("🛑 Aborted. Using existing private key.")
            return
    
    print(f"📁 Creating certificates in: {certs_dir.absolute()}")
    
    # Step 1: Generate private key
    run_command(
        f"openssl genrsa -out {private_key_file} 2048",
        "Generating 2048-bit RSA private key"
    )
    
    # Step 2: Generate certificate signing request (non-interactive with defaults)
    print("\n📝 Creating certificate signing request with default values...")
    
    # Create a config file for non-interactive certificate generation
    config_content = """[req]
distinguished_name = req_distinguished_name
prompt = no

[req_distinguished_name]
C = US
ST = CA
L = San Francisco
O = Salesforce Multi-Agent Workforce
OU = IT Department
CN = Multi-Agent-Workforce
emailAddress = admin@example.com
"""
    
    config_file = certs_dir / "openssl.conf"
    with open(config_file, "w") as f:
        f.write(config_content)
    
    run_command(
        f"openssl req -new -key {private_key_file} -out {csr_file} -config {config_file}",
        "Generating certificate signing request"
    )
    
    # Step 3: Generate self-signed certificate
    run_command(
        f"openssl x509 -req -days 365 -in {csr_file} -signkey {private_key_file} -out {cert_file}",
        "Generating self-signed certificate (valid for 1 year)"
    )
    
    # Clean up temporary files
    csr_file.unlink()
    config_file.unlink()
    
    print("\n🎉 JWT Bearer Flow certificates generated successfully!")
    print("=" * 60)
    print(f"📄 Private Key: {private_key_file.absolute()}")
    print(f"📄 Certificate: {cert_file.absolute()}")
    
    print("\n📋 Next Steps:")
    print("1. Upload the certificate.crt to your Salesforce Connected App:")
    print("   - Setup > App Manager > [Your Connected App] > Edit")
    print("   - Enable OAuth Settings > Use digital signatures > Choose File")
    print("   - Upload the certificate.crt file")
    
    print("\n2. Update your .env file with:")
    print(f"   SF_PRIVATE_KEY_FILE_E2E_TEST_ORG=\"{private_key_file.absolute()}\"")
    print("   SF_CONSUMER_KEY_E2E_TEST_ORG=\"your_connected_app_consumer_key\"")
    print("   SF_USERNAME_E2E_TEST_ORG=\"your_username@example.com\"")
    
    print("\n3. Ensure your user is pre-authorized for the Connected App:")
    print("   - Setup > App Manager > [Your Connected App] > Manage")
    print("   - Manage Profiles/Permission Sets > Add your user's profile")
    
    print("\n🔒 Security Note:")
    print(f"Keep your private key ({private_key_file}) secure and never commit it to version control!")
    
    # Add to .gitignore if it exists
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            content = f.read()
        
        if "certs/" not in content:
            with open(gitignore_path, "a") as f:
                f.write("\n# JWT Bearer Flow certificates (keep private!)\ncerts/\n")
            print(f"✅ Added certs/ to .gitignore")

if __name__ == "__main__":
    # Check if OpenSSL is available
    try:
        subprocess.run(["openssl", "version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ OpenSSL is not installed or not in PATH.")
        print("Please install OpenSSL:")
        print("  - Ubuntu/Debian: sudo apt-get install openssl")
        print("  - macOS: brew install openssl")
        print("  - Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        sys.exit(1)
    
    main() 