# JWT Bearer Flow Setup for Salesforce Authentication

## 🚀 Overview

This project now uses **OAuth JWT Bearer Flow** for Salesforce authentication, which is the modern, secure method recommended by Salesforce. This replaces the deprecated security token approach.

### ✅ Benefits of JWT Bearer Flow:
- **Secure**: Uses certificates instead of passwords
- **Modern**: Recommended by Salesforce for server-to-server integration
- **Compatible**: Works with both REST and Metadata APIs
- **No Expiration Issues**: More reliable than Client Credentials flow

## 📋 Prerequisites

1. **OpenSSL** installed on your system
2. **Salesforce org** with admin access
3. **Connected App** configured for JWT Bearer Flow

## 🔧 Step 1: Generate Certificates

Run the setup script to generate the required private key and certificate:

```bash
python scripts/setup_jwt_auth.py
```

This will:
- Create a `certs/` directory
- Generate `private_key.pem` (keep this secure!)
- Generate `certificate.crt` (upload to Salesforce)
- Add `certs/` to `.gitignore` for security

## 🏗️ Step 2: Create Connected App in Salesforce

1. **Navigate to Setup > App Manager**
2. **Click "New Connected App"**
3. **Fill in Basic Information:**
   - Connected App Name: `Multi-Agent Workforce`
   - API Name: `Multi_Agent_Workforce`
   - Contact Email: your email

4. **Configure API (Enable OAuth Settings):**
   - ✅ Enable OAuth Settings
   - Callback URL: `https://login.salesforce.com` (required but not used)
   - ✅ Use digital signatures
   - **Upload your `certificate.crt` file**
   - Selected OAuth Scopes:
     - `Access and manage your data (api)`
     - `Perform requests on your behalf at any time (refresh_token, offline_access)`

5. **Save and note the Consumer Key**

## 🔐 Step 3: Configure Connected App Policies

1. **Go to Setup > App Manager > [Your Connected App] > Manage**
2. **Edit Policies:**
   - Permitted Users: `Admin approved users are pre-authorized`
   - IP Relaxation: `Relax IP restrictions` (or configure as needed)
3. **Save**

## 👥 Step 4: Pre-authorize Users

1. **In the same Connected App management page**
2. **Click "Manage Profiles" or "Manage Permission Sets"**
3. **Add your user's profile or create a permission set**
4. **Assign the permission set to your user**

## 🔧 Step 5: Update Environment Variables

Update your `.env` file with the JWT Bearer Flow configuration:

```bash
# E2E Test Org Configuration
SF_USERNAME_E2E_TEST_ORG="your_username@company.com.sandbox"
SF_CONSUMER_KEY_E2E_TEST_ORG="your_connected_app_consumer_key_from_step_2"
SF_PRIVATE_KEY_FILE_E2E_TEST_ORG="/absolute/path/to/your/certs/private_key.pem"
SF_INSTANCE_URL_E2E_TEST_ORG="https://your-domain--sandbox.my.salesforce.com"
```

### 🔍 How to find your values:

- **SF_USERNAME_**: Your Salesforce username
- **SF_CONSUMER_KEY_**: From Step 2 (Connected App details)
- **SF_PRIVATE_KEY_FILE_**: Absolute path to the generated `private_key.pem`
- **SF_INSTANCE_URL_**: Your Salesforce instance URL (optional, defaults to login.salesforce.com)

## 🧪 Step 6: Test the Setup

Run the e2e test to verify everything works:

```bash
python -m pytest tests/test_e2e_workflow.py -v
```

## 🔒 Security Best Practices

1. **Never commit private keys** to version control
2. **Keep certificates secure** and rotate them annually
3. **Use least privilege** - only grant necessary permissions
4. **Monitor Connected App usage** in Salesforce

## 🐛 Troubleshooting

### Common Issues:

1. **"Private key file not found"**
   - Ensure the path in `SF_PRIVATE_KEY_FILE_*` is correct and absolute
   - Check file permissions

2. **"Invalid consumer key"**
   - Verify the Consumer Key from your Connected App
   - Ensure the Connected App is saved and active

3. **"User not authorized"**
   - Check that the user is pre-authorized (Step 4)
   - Verify the username is correct

4. **"Invalid signature"**
   - Ensure the certificate uploaded to Salesforce matches the private key
   - Regenerate certificates if needed

### Debug Steps:

1. **Check Connected App status:**
   - Setup > App Manager > [Your App] > View
   - Ensure it's active and properly configured

2. **Verify user permissions:**
   - Setup > Users > [Your User] > Permission Set Assignments
   - Ensure the Connected App permission set is assigned

3. **Test with simple-salesforce directly:**
   ```python
   from simple_salesforce import Salesforce
   sf = Salesforce(
       username='your_username@example.com',
       consumer_key='your_consumer_key',
       privatekey_file='/path/to/private_key.pem'
   )
   print(sf.query("SELECT Id FROM User LIMIT 1"))
   ```

## 📚 Additional Resources

- [Salesforce JWT Bearer Flow Documentation](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_jwt_flow.htm)
- [simple-salesforce JWT Documentation](https://simple-salesforce.readthedocs.io/en/latest/user_guide/authentication.html#jwt-bearer-flow)
- [Connected App Best Practices](https://help.salesforce.com/s/articleView?id=sf.connected_app_overview.htm)

## 🔄 Migration from Security Tokens

If you were previously using username/password/security_token authentication:

1. **Follow all steps above** to set up JWT Bearer Flow
2. **Update your `.env` file** to use the new variable format
3. **Remove old variables** like `SF_PASSWORD_*` and `SF_SECURITY_TOKEN_*`
4. **Test thoroughly** before deploying to production

The new authentication method is more secure and reliable than the deprecated security token approach. 