/**
 * Code.js
 * Meeting Scheduler MVP - Frontend / Trigger
 */

// Keys for PropertiesService
const PROP_CLOUD_RUN_URL = 'CLOUD_RUN_URL';
const PROP_TRIGGER_DURATION = 'TRIGGER_DURATION';
const PROP_PREFERRED_DURATION = 'PREFERRED_DURATION';
const PROP_TIMEZONE = 'TIMEZONE';

/**
 * Serves the configuration page (WebApp).
 */
function doGet(e) {
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle('Meeting Scheduler Config')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * Saves settings from the UI.
 */
function saveSettings(settings) {
  const props = PropertiesService.getUserProperties();
  props.setProperties({
    [PROP_CLOUD_RUN_URL]: settings.cloudRunUrl,
    [PROP_TRIGGER_DURATION]: settings.triggerDuration,
    [PROP_PREFERRED_DURATION]: settings.preferredDuration,
    [PROP_TIMEZONE]: settings.timezone
  });

  // Update Trigger
  manageTrigger(parseInt(settings.triggerDuration));
}

/**
 * Retrieves settings for the UI.
 */
function getSettings() {
  const props = PropertiesService.getUserProperties();
  return {
    cloudRunUrl: props.getProperty(PROP_CLOUD_RUN_URL),
    triggerDuration: props.getProperty(PROP_TRIGGER_DURATION),
    preferredDuration: props.getProperty(PROP_PREFERRED_DURATION),
    timezone: props.getProperty(PROP_TIMEZONE)
  };
}

/**
 * Manages the time-based trigger.
 */
function manageTrigger(durationMinutes) {
  const triggers = ScriptApp.getProjectTriggers();
  for (const trigger of triggers) {
    if (trigger.getHandlerFunction() === 'checkEmails') {
      ScriptApp.deleteTrigger(trigger);
    }
  }

  if (durationMinutes > 0) {
    ScriptApp.newTrigger('checkEmails')
      .timeBased()
      .everyMinutes(durationMinutes)
      .create();
  }
}

/**
 * Main Logic: Checks for new emails and sends them to Cloud Run.
 */
function checkEmails() {
  const props = PropertiesService.getUserProperties();
  const cloudRunUrl = props.getProperty(PROP_CLOUD_RUN_URL);

  if (!cloudRunUrl) {
    Logger.log('Cloud Run URL not configured.');
    return;
  }

  // SEARCH QUERY: Adjust this based on requirements.
  // MVP: "to:TOKEN_EMAIL+meeting-scheduler@..." or "to:me" + keyword
  // Current default: Is unread and has "meeting", "schedule", or "calendar" in text.
  // Note: Only processing UNREAD threads to avoid loops, and marking as read is optional but recommended.
  const query = 'is:unread to:me (meeting OR schedule OR calendar)';

  const threads = GmailApp.search(query, 0, 10); // Batch size 10
  let processedCount = 0;

  for (const thread of threads) {
    const messages = thread.getMessages();
    // We process the LAST message in the thread usually, or the whole thread context?
    // MVP says: "AppScript must send: messages: [{role, content, time}] from the thread."
    // We'll send the latest message as the trigger, but include thread context.

    const lastMessage = messages[messages.length - 1];

    if (!lastMessage.isUnread()) {
      continue; // Skip if already read (though search 'is:unread' helps, granularity matters)
    }

    const payload = {
      token: ScriptApp.getOAuthToken(),
      user_email: Session.getActiveUser().getEmail(),
      message_id: lastMessage.getId(),
      thread_id: thread.getId(),
      email_content: lastMessage.getBody() || lastMessage.getPlainBody(), // Prefer Body (HTML) for parsing, or Plain? MVP says Body/Snippet.
      // detailed thread context could be added here if the backend expects it immediately
      // or backend uses thread_id + token to fetch it.
      // MVP says: "AppScript must send: messages: [...]".
      // Let's stick to the minimal payload defined in MVP Doc first, 
      // which lists `email_content` (Body/Snippet).
      // If the backend needs full thread, it can use the token.
    };

    try {
      sendToCloudRun(cloudRunUrl, payload);
      // Mark as read/labeled to prevent reprocessing?
      // lastMessage.markRead(); // Uncomment when ready to consume
      Logger.log('Processed message: ' + lastMessage.getId());
      processedCount++;
    } catch (e) {
      Logger.log('Error sending to Cloud Run: ' + e.toString());
    }
  }

  return 'Check complete. Processed ' + processedCount + ' threads.';
}


/**
 * Sends data to Cloud Run.
 */
/**
 * Sends data to Cloud Run using a Service Account ID Token.
 */
function sendToCloudRun(url, payload) {
  const serviceAccountEmail = 'meeting-invoker@agents-at-work-hackathon.iam.gserviceaccount.com';

  try {
    const idToken = getIdToken_(serviceAccountEmail, url);

    const options = {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(payload),
      headers: {
        'Authorization': 'Bearer ' + idToken
      },
      muteHttpExceptions: true
    };

    Logger.log('Calling Cloud Run URL: ' + url);
    const response = UrlFetchApp.fetch(url, options);
    Logger.log('Cloud Run Response Code: ' + response.getResponseCode());
    Logger.log('Cloud Run Response: ' + response.getContentText());

    if (response.getResponseCode() >= 400) {
      throw new Error('Cloud Run returned error: ' + response.getResponseCode());
    }
  } catch (e) {
    Logger.log('Error in sendToCloudRun: ' + e.toString());
    throw e;
  }
}

/**
 * Generates an OIDC ID Token for the Service Account.
 */
function getIdToken_(serviceAccountEmail, audience) {
  const accessToken = ScriptApp.getOAuthToken();
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

  if (response.getResponseCode() === 200) {
    const tokenResponse = JSON.parse(response.getContentText());
    return tokenResponse.token;
  } else {
    throw new Error(`Failed to generate ID token: ${response.getContentText()}`);
  }
}
