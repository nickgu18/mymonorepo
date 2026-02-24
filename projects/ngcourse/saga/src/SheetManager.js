/**
 * @OnlyCurrentDoc
 *
 * The above comment directs Apps Script to limit the scope of authorization,
 * asking for permission only on the current spreadsheet.
 */

/**
 * Adds a custom menu to the spreadsheet.
 */
function onOpen(e) {
  // Consider adding setApiKey_ to the menu during initial setup/testing
  SpreadsheetApp.getUi()
    .createMenu('Saga Assistant')
    .addItem('Run Daily Summary Now', 'processEmailsAndProposeTasks') // Placeholder function name
    .addItem('Process Approved Tasks', 'processApprovedTasksAndUpdateSheet') // Placeholder function name
    .addSeparator()
    .addItem('Process Emails (Daily Trigger)', 'fetchAndProcessEmails_')
    .addItem('Process Approved Tasks', 'processApprovedTasks_')
    .addSeparator()
    .addItem('Run Eval', 'runEvalCommand')
    .addSeparator()
    .addItem('Set AI API Key', 'setApiKey_') // Add item to set the API key
    .addToUi();
}

/**
 * Creates the required sheets if they don't already exist.
 */
function setupSheets_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const requiredSheets = [
    'Task Proposal',
    'Configuration',
    'Summary Log', // Optional, but included based on checklist
    'Run Log'      // Optional, but included based on checklist
  ];

  requiredSheets.forEach(sheetName => {
    if (!ss.getSheetByName(sheetName)) {
      ss.insertSheet(sheetName);
      Logger.log(`Sheet "${sheetName}" created.`);
    } else {
      Logger.log(`Sheet "${sheetName}" already exists.`);
    }
  });

  // Optional: Pre-populate Configuration sheet headers if it was just created
  const configSheet = ss.getSheetByName('Configuration');
  if (configSheet && configSheet.getLastRow() === 0) { // Check if empty
    configSheet.appendRow(['Key', 'Value']);
    configSheet.getRange("A1:B1").setFontWeight("bold");
    // Add initial placeholder rows if desired
    configSheet.appendRow(['TASK_LIST_ID', 'YOUR_TASK_LIST_ID_HERE']);
    configSheet.appendRow(['APPROVAL_KEYWORD', 'Yes']);
    configSheet.appendRow(['EMAIL_QUERY_DAYS', '1']);
    configSheet.appendRow(['TASK_PROPOSAL_SHEET', 'Task Proposal']);
    configSheet.appendRow(['SUMMARY_LOG_SHEET', 'Summary Log']);
    configSheet.appendRow(['RUN_LOG_SHEET', 'Run Log']);
    configSheet.appendRow(['AI_API_ENDPOINT', 'YOUR_AI_ENDPOINT_URL_HERE']);
    configSheet.appendRow(['RECIPIENT_EMAIL', 'YOUR_EMAIL_HERE']); // Add recipient email placeholder
    configSheet.appendRow(['MY_GOALS', 'Example: Finalize Q3 roadmap; Onboard new team member; Reduce cloud costs.']); // Add My Goals placeholder
    // --- END ADD ---
    SpreadsheetApp.flush(); // Apply changes immediately
    Logger.log('Configuration sheet headers and initial values added.');
  }

  // Optional: Pre-populate Task Proposal sheet headers if it was just created
  const taskSheet = ss.getSheetByName('Task Proposal');
  if (taskSheet && taskSheet.getLastRow() === 0) { // Check if empty
    taskSheet.appendRow(['Task Name', 'Target Date', 'Approve', 'Status', 'Source Email ID', 'Date Proposed']);
    taskSheet.getRange("A1:F1").setFontWeight("bold");
    SpreadsheetApp.flush();
    Logger.log('Task Proposal sheet headers added.');
  }

  // Optional: Pre-populate Summary Log sheet headers if it was just created (New Relevance Format)
  const summarySheet = ss.getSheetByName('Summary Log');
  if (summarySheet && summarySheet.getLastRow() === 0) { // Check if empty
    const headers = ['Timestamp', 'Score', 'Justification', 'Subject', 'From', 'Date', 'Thread ID', 'Message ID', 'Pass1 Status', 'Error'];
    summarySheet.appendRow(headers);
    summarySheet.getRange(1, 1, 1, headers.length).setFontWeight("bold");
    SpreadsheetApp.flush();
    Logger.log('Summary Log sheet headers (for relevance scores) added.');
  }

  // Optional: Pre-populate Run Log sheet headers if it was just created
  const runLogSheet = ss.getSheetByName('Run Log');
  if (runLogSheet && runLogSheet.getLastRow() === 0) { // Check if empty
    runLogSheet.appendRow(['Timestamp', 'Message']);
    runLogSheet.getRange("A1:B1").setFontWeight("bold");
    SpreadsheetApp.flush();
    Logger.log('Run Log sheet headers added.');
  }


  SpreadsheetApp.getUi().alert('Sheet setup complete. Check the Configuration sheet to add necessary values (like Task List ID, AI Endpoint, My Goals).');
}

// Placeholder functions for menu items - replace with actual implementation later
function processEmailsAndProposeTasks() {
  fetchAndProcessEmails_(); // Call the actual implementation
}

function processApprovedTasksAndUpdateSheet() {
  processApprovedTasks_();
}

/**
 * Opens and activates the 'Configuration' sheet for easy access.
 * @private
 */
function openConfigurationSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const configSheet = ss.getSheetByName('Configuration');
  if (configSheet) {
    ss.setActiveSheet(configSheet);
  } else {
    SpreadsheetApp.getUi().alert('Error: Configuration sheet not found. Please run "Setup Sheets" first.');
  }
}

// --- Logging Utility ---

/**
 * Appends a message with a timestamp to the 'Run Log' sheet.
 * @param {string} message The message to log.
 * @private
 */
function logToRunLog_(message) {
  // Note: This now calls getConfig_ which reads directly from the sheet
  try {
    const config = getConfig_(); // Get config fresh each time
    const logSheetName = config ? config['RUN_LOG_SHEET'] : 'Run Log'; // Default name if config fails

    // Check if config loading itself failed (e.g., sheet missing)
    if (!config && message.indexOf("FATAL Error") === -1) { // Avoid infinite loop if getConfig_ throws
      Logger.log(`Could not load config to find Run Log sheet. Cannot log: ${message}`);
      return;
    }

    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const logSheet = ss.getSheetByName(logSheetName);

    if (logSheet) {
      const timestamp = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss");
      // Prepend timestamp if logSheet is empty or doesn't have it
      if (logSheet.getLastRow() > 0 && logSheet.getRange(logSheet.getLastRow(), 1).getValue() === '') {
        logSheet.getRange(logSheet.getLastRow(), 1).setValue(timestamp);
        logSheet.getRange(logSheet.getLastRow(), 2).setValue(message);
      } else {
        logSheet.appendRow([timestamp, message]);
      }
    } else {
      // Log to Logger if sheet not found
      Logger.log(`Run Log sheet ("${logSheetName}") not found. Could not log: ${message}`);
    }
  } catch (e) {
    // Log errors during logging itself to the default Logger
    Logger.log(`Error writing to Run Log: ${e} - Original Message: ${message}`);
  }
}
// --- Configuration Management ---


/**
 * Reads configuration values directly from the 'Configuration' sheet.
 * NO CACHING IS USED. Reads fresh values on every call.
 * @return {Object<string, (string|Array<string>)>|null} An object containing key-value pairs.
 * If a key appears multiple times, its value will be an array of strings.
 * Returns null if the sheet is not found.
 * @private
 */
function getConfig_() {
  Logger.log('Reading configuration directly from sheet...');

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const configSheet = ss.getSheetByName('Configuration');

  if (!configSheet) {
    Logger.log('Error: Configuration sheet not found. Please run "Setup Sheets" first.');
    return null;
  }

  if (configSheet.getLastRow() < 2) {
    Logger.log("Configuration sheet is empty or has only headers. No configuration loaded.");
    return {};
  }

  const dataRange = configSheet.getRange('A2:B' + configSheet.getLastRow());
  const values = dataRange.getValues();
  const config = {};

  values.forEach(row => {
    const key = row[0] ? row[0].toString().trim() : '';
    const value = (row[1] !== undefined && row[1] !== null) ? row[1].toString().trim() : '';

    if (key) {
      if (config.hasOwnProperty(key)) {
        // If key already exists, convert to array or push to existing array
        if (Array.isArray(config[key])) {
          config[key].push(value);
        } else {
          config[key] = [config[key], value];
        }
      } else {
        // First time seeing this key
        config[key] = value;
      }
    }
  });

  Logger.log('Configuration loaded directly from sheet.');
  return config;
}

/**
 * Retrieves the AI API Key from Script Properties.
 * @return {string|null} The API key, or null if not set.
 * @private
 */
function getApiKey_() {
  // Reads directly from Properties Service each time (no change needed here)
  return PropertiesService.getScriptProperties().getProperty('AI_API_KEY');
}

/**
 * Prompts the user and sets the AI API Key in Script Properties.
 * (Helper function, not added to menu by default)
 */
function setApiKey_() {
  const ui = SpreadsheetApp.getUi();
  const response = ui.prompt('Set AI API Key', 'Enter your AI API Key:', ui.ButtonSet.OK_CANCEL);
  if (response.getSelectedButton() == ui.Button.OK) {
    const apiKey = response.getResponseText();
    if (apiKey && apiKey.trim() !== '') {
      // Writes directly to Properties Service (no change needed here)
      PropertiesService.getScriptProperties().setProperty('AI_API_KEY', apiKey.trim());
      ui.alert('API Key set successfully.');
    } else {
      ui.alert('API Key cannot be empty.');
    }
  }
}

/**
 * Safely attempts to show an alert in the UI.
 * If the UI is not available (e.g., running in a time-driven trigger),
 * it logs the message to the Run Log instead of throwing an error.
 * @param {string} message The message to display or log.
 */
function safeAlert_(message) {
  try {
    SpreadsheetApp.getUi().alert(message);
  } catch (e) {
    // UI not available (likely running in a trigger)
    // Log to Run Log so the user can still see it if they check the logs
    logToRunLog_(`[safeAlert_] UI not available. Alert message: ${message}`);
    console.warn(`[safeAlert_] UI not available. Alert message: ${message}`);
  }
}