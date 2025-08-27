# GitHub App Setup Guide

This guide walks you through creating and configuring the **PatchPanda-Dev** umbrella GitHub App that includes the PatchPanda Gateway as one of its components. The guide covers setting up the required permissions and webhook events for the gateway functionality.

## Prerequisites

- GitHub account with admin access to the target repository
- Access to the PatchPanda Gateway environment variables
- **Development setup**: ngrok, Cloudflare Tunnel, or similar tool to expose localhost publicly

## Step 1: Create the GitHub App

1. Go to [GitHub Developer Settings](https://github.com/settings/apps)
2. Click "New GitHub App"
3. Fill in the basic information:
   - **GitHub App name**: `PatchPanda-Dev` (or your preferred name)
   - **Description**: `Umbrella app for PatchPanda development tools including automated test generation and coverage analysis`
   - **Homepage URL**: `http://localhost:8000` (for development)
   - **Webhook**: Check "Active"
   - **Webhook URL**: Use a publicly accessible URL (see development options below)
   - **Webhook secret**: Generate a secure random string (32+ characters)

**Note**: GitHub requires publicly accessible webhook URLs. For development, you can use:
- **ngrok**: `https://your-ngrok-url.ngrok.io/webhooks/github`
- **Cloudflare Tunnel**: `https://your-tunnel-url.trycloudflare.com/webhooks/github`
- **Production URL**: If you have a deployed gateway, use that URL

## Step 2: Configure Permissions

Set the following permissions:

### Repository Permissions
- **Contents**: `Read & write` - To read repository files and create test files
- **Pull requests**: `Read & write` - To read PR details and post comments/checks
- **Issues**: `Read & write` - To read issue comments and respond
- **Checks**: `Read & write` - To create and update check runs

### Account Permissions
- **Metadata**: `Read-only` - Required for all GitHub Apps

## Step 3: Subscribe to Webhook Events

Select these webhook events:
- `Issue comments` - To trigger test generation from comments
- `Pull requests` - To handle PR state changes and updates

**Note**: The `Check suite` event is optional and only needed if you want to monitor check run status. You can add additional webhook events later as needed.

## Step 4: Install the App

1. After creating the app, click "Install App"
2. Choose the target repository (sandbox repo for testing)
3. Grant access to the selected repositories

## Step 5: Update Environment Variables

Copy the following values to your `.env` file:

```bash
# GitHub App Configuration
GITHUB_APP_ID=<your_app_id>
GITHUB_APP_PRIVATE_KEY=<your_private_key>
GITHUB_WEBHOOK_SECRET=<your_webhook_secret>

# Development (Optional)
NGROK_URL=<your_ngrok_url>
```

### Getting the Values

- **App ID**: Found on the app's main page
- **Private Key**:
  1. Go to "Private keys" section
  2. Click "Generate private key"
  3. Download the `.pem` file
  4. Copy the entire content (including `-----BEGIN RSA PRIVATE KEY-----`)
- **Webhook Secret**: The secret you generated in Step 1

### Setting ngrok URL (Optional)

If you're using ngrok for development, you can easily set the URL:

```bash
make set-ngrok-url
```

This will prompt you to enter your ngrok URL and automatically add it to your `.env` file.

## Step 6: Development Setup (Public Webhook URL)

Since GitHub requires publicly accessible webhook URLs, you'll need to expose your local gateway during development:

### Option 1: Using ngrok (Recommended for development)

1. **Install ngrok**: Download from [ngrok.com](https://ngrok.com/) or install via package manager
2. **Start your gateway**: `make run`
3. **Expose your local gateway**:
   ```bash
   ngrok http 8000
   ```
4. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)
5. **Update your GitHub App webhook URL** to: `https://abc123.ngrok.io/webhooks/github`
6. **Keep ngrok running** while testing webhooks

### Option 2: Using Cloudflare Tunnel

1. **Install cloudflared**: Download from [cloudflare.com](https://cloudflare.com/)
2. **Start your gateway**: `make run`
3. **Create tunnel**:
   ```bash
   cloudflared tunnel --url http://localhost:8000
   ```
4. **Use the provided HTTPS URL** for your webhook

### Option 3: Production Deployment

If you have a deployed gateway, use that URL directly.

## Step 7: Test the Setup

1. Start the gateway: `make run`
2. Set up your public webhook URL (using one of the options above)
3. **Optional**: Set your ngrok URL in `.env` for easier testing:
   ```bash
   make set-ngrok-url
   ```
4. Test the integration:
   ```bash
   make test-github-integration
   ```
5. Make a change to your sandbox repository
6. Check the webhook logs in your terminal
7. Verify the app has the correct permissions

## Troubleshooting

### Common Issues

1. **Webhook delivery failures**
   - Check if the gateway is running
   - Verify the webhook URL is publicly accessible (not localhost)
   - Ensure your ngrok/cloudflared tunnel is running
   - Check webhook secret matches
   - Verify the webhook URL is HTTPS (GitHub requires secure URLs)

2. **Permission denied errors**
   - Verify the app has the required permissions
   - Check if the app is installed on the repository
   - Ensure the installation token is valid

3. **Signature verification failures**
   - Verify the webhook secret is correct
   - Check the signature verification logic

### Testing Webhook Delivery

You can test webhook delivery using tools like:
- [ngrok](https://ngrok.com/) for exposing localhost
- [GitHub's webhook testing](https://docs.github.com/en/developers/webhooks-and-events/webhooks/testing-webhooks)

## Security Considerations

- Keep the private key secure and never commit it to version control
- Use environment variables for all sensitive configuration
- Regularly rotate the webhook secret
- Monitor webhook delivery for suspicious activity

## Next Steps

After setting up the GitHub App:
1. Test webhook handling with real repository events
2. Implement the TODO items in the webhook handlers
3. Add proper error handling and logging
4. Set up monitoring and alerting for webhook failures
