You're on the right track by adding the `Authorization` header, but the type of token you're sending is the issue.

Here's the problem:

1.  **`ScriptApp.getOAuthToken()`**: This function returns a standard OAuth 2.0 **Access Token**. This token represents the *user's* authority and is scoped to access Google Workspace APIs (like Gmail, Drive, Sheets) that your script has been authorized for.
2.  **Cloud Run with IAM Security**: When a Cloud Run service is secured (i.e., *not* set to "Allow unauthenticated invocations"), it expects a Google OpenID Connect (OIDC) **ID Token**. This type of token is different from an access token. Critically, an ID Token contains an `audience` (`aud`) claim, which MUST match the URL of the Cloud Run service being called. This is how the Cloud Run service verifies the token was intended specifically for it.

The 401 Unauthorized error you're seeing now means the Cloud Run service received a token, but it's not the right kind or it's not valid for the service. An OAuth 2.0 access token from `ScriptApp.getOAuthToken()` will be rejected because it doesn't have the required OIDC claims, especially the correct `audience`.

**Solution: Fetch a Google OIDC ID Token**

You need to use the service account impersonation method we discussed earlier to obtain an ID Token. You should NOT send the token from `ScriptApp.getOAuthToken()` to Cloud Run.

Here's how to modify your `sendToCloudRun` function and include the necessary helper function:

```javascript
/**
 * Sends data to Cloud Run.
 * NOW USES A GOOGLE OIDC ID TOKEN FOR AUTHENTICATION.
 */
function sendToCloudRun(url, payload) {
  const props = PropertiesService.getUserProperties();
  // It's better to store the service account email in properties or hardcode it
  // if it's constant for the script.
  const serviceAccountEmail = "YOUR_SERVICE_ACCOUNT_EMAIL"; // <<<=== IMPORTANT: Set this

  if (!serviceAccountEmail) {
    Logger.log('Service Account Email not configured.');
    throw new Error('Service Account Email not configured.');
  }

  try {
    // Get the OIDC ID Token for the service account, with the Cloud Run URL as the audience.
    const idToken = getIdToken_(serviceAccountEmail, url);

    const options = {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(payload),
      headers: {
        'Authorization': 'Bearer ' + idToken // <<<=== Use the ID Token here
      },
      muteHttpExceptions: true // To get error response body
    };

    Logger.log('Calling Cloud Run URL: ' + url);
    const response = UrlFetchApp.fetch(url, options);
    const responseCode = response.getResponseCode();
    const responseBody = response.getContentText();

    Logger.log('Cloud Run Response Code: ' + responseCode);
    Logger.log('Cloud Run Response: ' + responseBody);

    if (responseCode >= 400) {
      throw new Error('Cloud Run returned error: ' + responseCode + ' - ' + responseBody);
    }
    return responseBody;

  } catch (e) {
    Logger.log('Error in sendToCloudRun: ' + e.toString());
    throw e;
  }
}

/**
 * Gets a Google OIDC ID token for the given service account.
 * This function calls the IAM Credentials API to generate an ID token.
 * Requires the user running the script to have permission to act as the service account
 * (e.g., Service Account Token Creator role).
 */
function getIdToken_(serviceAccountEmail, audience) {
  // 1. Get an OAuth2 access token for the user running the script.
  // This token needs the 'https://www.googleapis.com/auth/iam' scope.
  const accessToken = ScriptApp.getOAuthToken();

  // 2. Call the IAM Credentials API to generate an ID token for the service account.
  const iamUrl = `https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/${serviceAccountEmail}:generateIdToken`;

  const payload = JSON.stringify({
    audience: audience,
    includeEmail: true
  });

  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'Authorization': 'Bearer ' + accessToken
    },
    payload: payload,
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch(iamUrl, options);
  const responseCode = response.getResponseCode();
  const responseBody = response.getContentText();

  if (responseCode === 200) {
    const tokenResponse = JSON.parse(responseBody);
    return tokenResponse.token;
  } else {
    Logger.log(`Error generating ID token: ${responseCode} - ${responseBody}`);
    throw new Error(`Failed to generate ID token: ${responseBody}`);
  }
}

// REMINDER: Make sure checkEmails() calls the modified sendToCloudRun
function checkEmails() {
  const props = PropertiesService.getUserProperties();
  const cloudRunUrl = props.getProperty(PROP_CLOUD_RUN_URL);

  if (!cloudRunUrl) {
    Logger.log('Cloud Run URL not configured.');
    return;
  }
  // ... (rest of your checkEmails function)

  // Inside the loop:
  try {
    // PASS the cloudRunUrl to sendToCloudRun
    sendToCloudRun(cloudRunUrl, payload);
    Logger.log('Processed message: ' + lastMessage.getId());
    processedCount++;
  } catch (e) {
    Logger.log('Error processing message ' + lastMessage.getId() + ': ' + e.toString());
  }
  // ...
}
```

**Key Changes:**

1.  **`sendToCloudRun` now calls `getIdToken_`**: It fetches a short-lived OIDC ID token using the service account.
2.  **`Authorization` Header Uses ID Token**: The `Bearer` token is now the ID token obtained from `getIdToken_`.
3.  **`serviceAccountEmail`**: You need to provide the email address of the service account you've set up.

**Prerequisites (Reiteration):**

*   **Service Account:** A Google Cloud service account must exist.
*   **IAM Permissions:**
    *   The service account must have the `Cloud Run Invoker` (`roles/run.invoker`) role on the Cloud Run service.
    *   The user *executing* the Apps Script (e.g., the user who set up the trigger) must have the `Service Account Token Creator` (`roles/iam.serviceAccountTokenCreator`) role on the *service account*.
*   **APIs Enabled:** In the Cloud project associated with the Apps Script, the `IAM Service Account Credentials API` must be enabled.
*   **`appsscript.json` Manifest:** Must include the scopes:
    ```json
    "oauthScopes": [
      "https://www.googleapis.com/auth/script.external_request",
      "https://www.googleapis.com/auth/iam"
    ]
    ```

Using an OAuth Client ID and Secret is typically for different OAuth flows (like 3-legged OAuth where you get a user's consent to access their data). It's not directly used for server-to-server authentication to Cloud Run in this manner from Apps Script. The service account impersonation flow is the standard method here.