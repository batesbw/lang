import os
from typing import Type
import requests # Added for making HTTP requests
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from simple_salesforce import Salesforce # SalesforceAuthenticationFailed might not be directly thrown by client_credentials

from src.schemas.auth_schemas import AuthenticationResponse, SalesforceSessionDetails

class SalesforceAuthenticatorToolInput(BaseModel):
    """Input schema for the SalesforceAuthenticatorTool."""
    org_alias: str = Field(description="The alias for the Salesforce org to authenticate against. Credentials for OAuth Client Credentials Flow will be fetched from environment variables based on this alias.")

class SalesforceAuthenticatorTool(BaseTool):
    """
    A LangChain tool to authenticate to a Salesforce org using the OAuth 2.0 Client Credentials Flow.
    
    Requires a Connected App in Salesforce configured for Client Credentials Flow with a designated 'Run As' user.
    
    Environment variable patterns (per org_alias):
    - SF_CONSUMER_KEY_{ORG_ALIAS} (Connected App's Consumer Key)
    - SF_CONSUMER_SECRET_{ORG_ALIAS} (Connected App's Consumer Secret)
    - SF_MY_DOMAIN_URL_{ORG_ALIAS} (Salesforce 'My Domain' URL, e.g., https://yourdomain.my.salesforce.com)
    """
    name: str = "salesforce_authenticator_tool"
    description: str = (
        "Authenticates to a Salesforce organization using the OAuth 2.0 Client Credentials Flow "
        "via an organization alias. Reads Consumer Key, Consumer Secret, and My Domain URL "
        "from environment variables prefixed with SF_ and suffixed with the uppercase ORG_ALIAS. "
        "Returns session details on success or an error message on failure."
    )
    args_schema: Type[BaseModel] = SalesforceAuthenticatorToolInput

    def _run(self, org_alias: str) -> AuthenticationResponse:
        """Execute the OAuth 2.0 Client Credentials authentication process."""
        uppercase_alias = org_alias.upper()

        consumer_key = os.getenv(f"SF_CONSUMER_KEY_{uppercase_alias}")
        consumer_secret = os.getenv(f"SF_CONSUMER_SECRET_{uppercase_alias}")
        my_domain_url = os.getenv(f"SF_MY_DOMAIN_URL_{uppercase_alias}")

        if not all([consumer_key, consumer_secret, my_domain_url]):
            missing_vars = []
            if not consumer_key: missing_vars.append(f"SF_CONSUMER_KEY_{uppercase_alias}")
            if not consumer_secret: missing_vars.append(f"SF_CONSUMER_SECRET_{uppercase_alias}")
            if not my_domain_url: missing_vars.append(f"SF_MY_DOMAIN_URL_{uppercase_alias}")
            return AuthenticationResponse(
                success=False,
                error_message=f"Missing one or more environment variables for org alias '{org_alias}': {', '.join(missing_vars)}."
            )

        token_url = f"{my_domain_url.rstrip('/')}/services/oauth2/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": consumer_key,
            "client_secret": consumer_secret
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            response = requests.post(token_url, data=payload, headers=headers, timeout=30)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
            
            token_data = response.json()
            access_token = token_data.get("access_token")
            instance_url = token_data.get("instance_url")

            if not access_token or not instance_url:
                return AuthenticationResponse(
                    success=False,
                    error_message=f"OAuth token request succeeded but did not return access_token or instance_url for org '{org_alias}'. Response: {token_data}"
                )

            # Verify the connection and get Org ID and User ID using the access token
            sf = Salesforce(session_id=access_token, instance_url=instance_url)
            
            session_details = SalesforceSessionDetails(
                session_id=access_token, # This is the access_token
                instance_url=instance_url,
                org_id=str(sf.sf_instance), # sf_instance is actually the org_id, cast to string
                user_id=str(sf.user_id), # This will be the 'Run As' user, cast to string
                org_alias=org_alias
            )
            return AuthenticationResponse(success=True, session_details=session_details)

        except requests.exceptions.HTTPError as e:
            error_content = e.response.text
            try:
                error_json = e.response.json()
                error_description = error_json.get("error_description", error_content)
            except requests.exceptions.JSONDecodeError:
                error_description = error_content
            return AuthenticationResponse(
                success=False, 
                error_message=f"Salesforce OAuth token request failed for org '{org_alias}' with status {e.response.status_code}: {error_description}"
            )
        except requests.exceptions.RequestException as e:
            # Catch other requests-related errors (timeout, connection error, etc.)
            return AuthenticationResponse(
                success=False, 
                error_message=f"Network error during Salesforce OAuth token request for org '{org_alias}': {str(e)}"
            )
        except Exception as e:
            # Catch any other unexpected errors (e.g., simple-salesforce instantiation if token is bad)
            return AuthenticationResponse(
                success=False, 
                error_message=f"An unexpected error occurred during Client Credentials authentication for org '{org_alias}': {str(e)}"
            )

    async def _arun(self, org_alias: str) -> AuthenticationResponse:
        """Asynchronously execute the authentication process. For now, it wraps the sync version."""
        # To make this truly async, the requests.post call would need to use an async HTTP client like httpx.
        return self._run(org_alias)

# Example Usage (for testing purposes, not part of the tool itself):
if __name__ == "__main__":
    # Before running, set up environment variables for your org_alias (e.g., MYSANDBOX):
    # export SF_CONSUMER_KEY_MYSANDBOX="YOUR_CONNECTED_APP_CONSUMER_KEY"
    # export SF_CONSUMER_SECRET_MYSANDBOX="YOUR_CONNECTED_APP_CONSUMER_SECRET"
    # export SF_MY_DOMAIN_URL_MYSANDBOX="https://yourorgdomain.my.salesforce.com"

    tool = SalesforceAuthenticatorTool()
    
    # Test with an alias for which env vars might be missing or incorrect
    test_alias_missing = "MISSING_CREDS_OAUTH"
    print(f"\nAttempting authentication for: {test_alias_missing}")
    result_missing_creds = tool.invoke({"org_alias": test_alias_missing})
    print(f"Result for {test_alias_missing}: {result_missing_creds}")

    # To test a successful connection:
    # 1. Replace 'MYSANDBOX_ACTUAL' with your actual alias used in env var names.
    # 2. Ensure your environment variables (SF_CONSUMER_KEY_MYSANDBOX_ACTUAL, etc.) are correctly set.
    # 3. Ensure your Connected App is configured for Client Credentials flow with a 'Run As' user.
    # test_alias_valid = "MYSANDBOX_ACTUAL" 
    # print(f"\nAttempting authentication for: {test_alias_valid}")
    # result_valid = tool.invoke({"org_alias": test_alias_valid})
    # print(f"Result for {test_alias_valid}: {result_valid}") 