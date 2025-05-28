import os
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from simple_salesforce import Salesforce

from src.schemas.auth_schemas import AuthenticationResponse, SalesforceSessionDetails

class SalesforceAuthenticatorToolInput(BaseModel):
    """Input schema for the SalesforceAuthenticatorTool."""
    org_alias: str = Field(description="The alias for the Salesforce org to authenticate against. Credentials for OAuth JWT Bearer Flow will be fetched from environment variables based on this alias.")

class SalesforceAuthenticatorTool(BaseTool):
    """
    A LangChain tool to authenticate to a Salesforce org using OAuth JWT Bearer Flow.
    
    This is the modern, secure authentication method that provides session IDs compatible 
    with both REST and Metadata APIs. It uses certificates instead of passwords.
    
    Environment variable patterns (per org_alias):
    - SF_USERNAME_{ORG_ALIAS} (Salesforce username for JWT subject)
    - SF_CONSUMER_KEY_{ORG_ALIAS} (Connected App's Consumer Key)
    - SF_PRIVATE_KEY_FILE_{ORG_ALIAS} (Path to private key file for JWT signing)
    - SF_INSTANCE_URL_{ORG_ALIAS} (Optional: Salesforce instance URL, defaults to login.salesforce.com)
    """
    name: str = "salesforce_authenticator_tool"
    description: str = (
        "Authenticates to a Salesforce organization using OAuth JWT Bearer Flow "
        "via an organization alias. Reads Username, Consumer Key, Private Key File path, "
        "and optional Instance URL from environment variables prefixed with SF_ and "
        "suffixed with the uppercase ORG_ALIAS. Returns session details on success or "
        "an error message on failure."
    )
    args_schema: Type[BaseModel] = SalesforceAuthenticatorToolInput

    def _run(self, org_alias: str) -> AuthenticationResponse:
        """Execute the OAuth JWT Bearer Flow authentication process."""
        uppercase_alias = org_alias.upper()

        username = os.getenv(f"SF_USERNAME_{uppercase_alias}")
        consumer_key = os.getenv(f"SF_CONSUMER_KEY_{uppercase_alias}")
        private_key_file = os.getenv(f"SF_PRIVATE_KEY_FILE_{uppercase_alias}")
        instance_url = os.getenv(f"SF_INSTANCE_URL_{uppercase_alias}")

        if not all([username, consumer_key, private_key_file]):
            missing_vars = []
            if not username: missing_vars.append(f"SF_USERNAME_{uppercase_alias}")
            if not consumer_key: missing_vars.append(f"SF_CONSUMER_KEY_{uppercase_alias}")
            if not private_key_file: missing_vars.append(f"SF_PRIVATE_KEY_FILE_{uppercase_alias}")
            return AuthenticationResponse(
                success=False,
                error_message=f"Missing one or more environment variables for org alias '{org_alias}': {', '.join(missing_vars)}."
            )

        # Check if private key file exists
        if not os.path.exists(private_key_file):
            return AuthenticationResponse(
                success=False,
                error_message=f"Private key file not found: {private_key_file}"
            )

        try:
            # Use simple-salesforce's JWT Bearer Flow authentication
            sf_kwargs = {
                'username': username,
                'consumer_key': consumer_key,
                'privatekey_file': private_key_file
            }
            
            # Add instance URL if specified (for sandbox or custom domains)
            if instance_url:
                # Extract domain from full URL for simple-salesforce
                if instance_url.startswith('https://'):
                    domain = instance_url.replace('https://', '').replace('.my.salesforce.com', '')
                    if '.sandbox' in domain or 'test' in domain.lower():
                        sf_kwargs['domain'] = 'test'
                    # For custom domains, simple-salesforce will handle it automatically
            
            sf = Salesforce(**sf_kwargs)
            
            # Extract session details
            # Note: sf.user_id might be an SFType object, so we need to extract the actual ID
            user_id_str = str(sf.user_id.id) if hasattr(sf.user_id, 'id') else str(sf.user_id) if sf.user_id else "unknown"
            
            session_details = SalesforceSessionDetails(
                session_id=sf.session_id,  # This is a proper session ID that works with Metadata API
                instance_url=sf.sf_instance,
                org_id=user_id_str[:15] if user_id_str != "unknown" else "unknown",  # Extract org ID from user ID (first 15 chars)
                user_id=user_id_str,
                org_alias=org_alias
            )
            
            return AuthenticationResponse(success=True, session_details=session_details)

        except Exception as e:
            # Catch any authentication errors
            error_msg = str(e)
            if "private key" in error_msg.lower():
                error_msg += " (Check that the private key file is valid and matches the certificate in your Connected App)"
            elif "consumer key" in error_msg.lower():
                error_msg += " (Check that the Consumer Key matches your Connected App)"
            elif "username" in error_msg.lower():
                error_msg += " (Check that the username is authorized for this Connected App)"
            
            return AuthenticationResponse(
                success=False, 
                error_message=f"Salesforce JWT authentication failed for org '{org_alias}': {error_msg}"
            )

    async def _arun(self, org_alias: str) -> AuthenticationResponse:
        """Asynchronously execute the authentication process. For now, it wraps the sync version."""
        return self._run(org_alias)

# Example Usage (for testing purposes, not part of the tool itself):
if __name__ == "__main__":
    # Before running, set up environment variables for your org_alias (e.g., MYSANDBOX):
    # export SF_USERNAME_MYSANDBOX="your_username@example.com"
    # export SF_CONSUMER_KEY_MYSANDBOX="your_connected_app_consumer_key"
    # export SF_PRIVATE_KEY_FILE_MYSANDBOX="/path/to/your/private_key.pem"
    # export SF_INSTANCE_URL_MYSANDBOX="https://your-domain.my.salesforce.com"  # Optional

    tool = SalesforceAuthenticatorTool()
    
    # Test with an alias for which env vars might be missing or incorrect
    test_alias_missing = "MISSING_CREDS"
    print(f"\nAttempting authentication for: {test_alias_missing}")
    result_missing_creds = tool.invoke({"org_alias": test_alias_missing})
    print(f"Result for {test_alias_missing}: {result_missing_creds}")

    # To test a successful connection:
    # 1. Replace 'MYSANDBOX_ACTUAL' with your actual alias used in env var names.
    # 2. Ensure your environment variables are correctly set.
    # 3. Ensure your Connected App is configured for JWT Bearer Flow.
    # test_alias_valid = "MYSANDBOX_ACTUAL" 
    # print(f"\nAttempting authentication for: {test_alias_valid}")
    # result_valid = tool.invoke({"org_alias": test_alias_valid})
    # print(f"Result for {test_alias_valid}: {result_valid}") 