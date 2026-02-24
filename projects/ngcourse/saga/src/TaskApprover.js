/**
 * @fileoverview Contains functions for processing approved tasks from the sheet
 * and creating them in Google Tasks.
 */

// --- Constants ---
const TASK_STATUS_PENDING = "Pending";
const TASK_STATUS_ADDED = "Added to Tasks";
const TASK_STATUS_ERROR = "Error adding task";
const TASK_STATUS_DECLINED = "Declined";
const APPROVE_COLUMN_INDEX = 3; // 1-based index for 'Approve' checkbox column
const STATUS_COLUMN_INDEX = 4;  // 1-based index for 'Status' column
const TASK_NAME_COLUMN_INDEX = 1; // 1-based index for 'Task Name'
const TARGET_DATE_COLUMN_INDEX = 2; // 1-based index for 'Target Date'
const SOURCE_LINK_COLUMN_INDEX = 5; // 1-based index for 'Source Email ID' (contains HYPERLINK)

/**
 * Main function triggered by the menu item. Reads the Task Proposal sheet, 
 * finds approved tasks, creates them in Google Tasks, and updates the sheet status.
 */
function processApprovedTasks_() {
  const functionName = 'processApprovedTasks_';
  logToRunLog_(`[${functionName}] Starting task approval processing...`);

  let config;
  let taskProposalSheet;
  let taskListId;
  let proposalSheetName;

  try {
    // --- 1. Get Configuration ---
    config = getConfig_(); // From SheetManager.gs
    if (!config) {
      throw new Error("Failed to load configuration.");
    }
    taskListId = config['TASK_LIST_ID'];
    proposalSheetName = config['TASK_PROPOSAL_SHEET'] || 'Task Proposal';

    if (!taskListId || taskListId === 'YOUR_TASK_LIST_ID_HERE') {
      throw new Error('Google Tasks List ID is not configured in the Configuration sheet.');
    }

    // --- 2. Get Task Proposal Sheet ---
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    taskProposalSheet = ss.getSheetByName(proposalSheetName);
    if (!taskProposalSheet) {
      throw new Error(`Task Proposal sheet "${proposalSheetName}" not found.`);
    }

    // --- 3. Read Task Proposals ---
    const proposals = readTaskProposals_(taskProposalSheet);
    if (proposals.length === 0) {
      logToRunLog_(`[${functionName}] No task proposals found in the sheet.`);
      safeAlert_('No task proposals found to process.');
      return;
    }

    // --- 4. Filter for Pending Tasks ---
    const pendingTasks = proposals.filter(p => p.status === TASK_STATUS_PENDING);

    if (pendingTasks.length === 0) {
      logToRunLog_(`[${functionName}] No tasks with status "${TASK_STATUS_PENDING}" found.`);
      safeAlert_(`No tasks with status "${TASK_STATUS_PENDING}" found to process.`);
      return;
    }

    logToRunLog_(`[${functionName}] Found ${pendingTasks.length} pending task(s) to process.`);

    // --- 5. Process Each Pending Task ---
    let successCount = 0;
    let errorCount = 0;
    let declinedCount = 0;

    pendingTasks.forEach(taskData => {
      try {
        // Check if the task is approved (checkbox checked)
        if (taskData.approve === true) {
          logToRunLog_(`[${functionName}] Processing APPROVED task: "${taskData.taskName}" (Row ${taskData.rowIndex})`);

          // 5a. Create Google Task
          const createdTask = createGoogleTask_(taskListId, taskData.taskName, taskData.targetDate, taskData.sourceLink);
          logToRunLog_(`[${functionName}] Successfully created Google Task ID: ${createdTask.id}`);

          // 5b. Update Sheet Status to Success
          updateTaskStatusInSheet_(taskProposalSheet, taskData.rowIndex, TASK_STATUS_ADDED);
          successCount++;

        } else {
          // 5c. Task is NOT approved (checkbox unchecked) - Mark as Declined
          logToRunLog_(`[${functionName}] Marking task as DECLINED: "${taskData.taskName}" (Row ${taskData.rowIndex})`);
          updateTaskStatusInSheet_(taskProposalSheet, taskData.rowIndex, TASK_STATUS_DECLINED);
          declinedCount++;
        }
      } catch (taskError) {
        logToRunLog_(`[${functionName}] ERROR processing task "${taskData.taskName}" (Row ${taskData.rowIndex}): ${taskError.message}`);
        // 5c. Update Sheet Status to Error
        updateTaskStatusInSheet_(taskProposalSheet, taskData.rowIndex, TASK_STATUS_ERROR, taskError.message);
        errorCount++;
      }
    });

    // --- 6. Final Feedback ---
    const completionMessage = `Task processing complete. Added: ${successCount}, Errors: ${errorCount}.`;
    logToRunLog_(`[${functionName}] ${completionMessage}`);
    safeAlert_(completionMessage);

  } catch (e) {
    // Catch fatal errors during setup or processing loop
    const errorMessage = `[${functionName}] FATAL Error: ${e.message}\nStack: ${e.stack || 'No stack trace available'}`;
    logToRunLog_(errorMessage);
    const userMessage = `FATAL Error during task processing: ${e.message}. Check '${proposalSheetName || 'Task Proposal'}' and '${config ? (config['RUN_LOG_SHEET'] || 'Run Log') : 'Run Log'}' sheets.`;
    safeAlert_(userMessage);
  }
}

// ==========================================================================
// Helper Functions: Reading, Creating, Updating
// ==========================================================================

/**
 * Reads task proposals from the sheet.
 * @param {Sheet} sheet The Task Proposal sheet object.
 * @return {Array<object>} Array of proposal objects:
 *   [{ taskName, targetDate, approve, status, sourceLink, rowIndex }, ...]
 * @private
 */
function readTaskProposals_(sheet) {
  const functionName = 'readTaskProposals_';
  const proposals = [];
  const dataRange = sheet.getDataRange();
  const values = dataRange.getValues();
  const formulas = dataRange.getFormulas(); // Get formulas to extract URL from HYPERLINK

  if (values.length <= 1) {
    logToRunLog_(`[${functionName}] Task proposal sheet is empty or has only headers.`);
    return proposals; // No data rows
  }

  // Start from row 1 to skip header
  for (let i = 1; i < values.length; i++) {
    const row = values[i];
    const rowIndex = i + 1; // 1-based index for sheet operations

    try {
      // Extract URL from HYPERLINK formula in the Source Email ID column
      let sourceUrl = '';
      const formula = formulas[i][SOURCE_LINK_COLUMN_INDEX - 1]; // 0-based for array
      if (formula && formula.toUpperCase().startsWith('=HYPERLINK("')) {
        const match = formula.match(/=HYPERLINK\("([^"]+)"/);
        if (match && match[1]) {
          sourceUrl = match[1];
        }
      }
      if (!sourceUrl && row[SOURCE_LINK_COLUMN_INDEX - 1]) {
        // Fallback if it's not a formula but has text (might be just the ID)
        sourceUrl = `https://mail.google.com/mail/#all/${row[SOURCE_LINK_COLUMN_INDEX - 1]}`;
      }


      proposals.push({
        taskName: row[TASK_NAME_COLUMN_INDEX - 1] || '', // 0-based for array
        targetDate: row[TARGET_DATE_COLUMN_INDEX - 1] || null, // Keep as string or null
        approve: row[APPROVE_COLUMN_INDEX - 1] === true, // Checkbox value
        status: row[STATUS_COLUMN_INDEX - 1] || '',
        sourceLink: sourceUrl, // Extracted URL
        rowIndex: rowIndex
      });
    } catch (parseError) {
      logToRunLog_(`[${functionName}] Error parsing row ${rowIndex}: ${parseError.message}. Skipping row.`);
    }
  }
  logToRunLog_(`[${functionName}] Read ${proposals.length} proposals from sheet.`);
  return proposals;
}

/**
 * Creates a task in Google Tasks.
 * Requires the Google Tasks API Advanced Service to be enabled.
 * @param {string} taskListId The ID of the target task list.
 * @param {string} taskName The name/title of the task.
 * @param {string|null} targetDateStr The target date string ("YYYY-MM-DD") or null.
 * @param {string} sourceLink The URL link to the source email.
 * @return {object} The created Google Task resource.
 * @throws {Error} If the Tasks API call fails.
 * @private
 */
function createGoogleTask_(taskListId, taskName, targetDateStr, sourceLink) {
  const functionName = 'createGoogleTask_';
  if (!Tasks || !Tasks.Tasks) {
    throw new Error("Google Tasks API Advanced Service is not enabled or not loaded.");
  }

  const taskResource = {
    title: taskName.substring(0, 1000), // Limit title length
    notes: `Source: ${sourceLink || 'N/A'}` // Add source email link to notes
  };

  // Format and add the due date if provided and valid
  if (targetDateStr && isValidDate_(targetDateStr)) {
    try {
      taskResource.due = formatDateToRFC3339UTC_(targetDateStr);
    } catch (dateError) {
      logToRunLog_(`[${functionName}] Warning: Could not format date "${targetDateStr}" for task "${taskName}". Creating task without due date. Error: ${dateError.message}`);
    }
  } else if (targetDateStr) {
    logToRunLog_(`[${functionName}] Warning: Invalid target date format "${targetDateStr}" for task "${taskName}". Creating task without due date.`);
  }

  try {
    // logToRunLog_(`[${functionName}] Creating task: ${JSON.stringify(taskResource)} in list ${taskListId}`);
    const createdTask = Tasks.Tasks.insert(taskResource, taskListId);
    if (!createdTask || !createdTask.id) {
      throw new Error("Tasks.insert call succeeded but returned invalid task object.");
    }
    return createdTask;
  } catch (e) {
    // Log the detailed error from the API if possible
    const apiError = e.message || JSON.stringify(e);
    logToRunLog_(`[${functionName}] Google Tasks API Error: ${apiError}`);
    throw new Error(`Failed to create Google Task: ${apiError.substring(0, 200)}`); // Re-throw simplified error
  }
}

/**
 * Updates the status cell for a specific task row in the sheet.
 * @param {Sheet} sheet The Task Proposal sheet object.
 * @param {number} rowIndex The 1-based row index to update.
 * @param {string} newStatus The new status text (e.g., "Added to Tasks", "Error", "Declined").
 * @param {string} [errorMessage] Optional error message to append if status is Error.
 * @private
 */
function updateTaskStatusInSheet_(sheet, rowIndex, newStatus, errorMessage) {
  try {
    const statusCell = sheet.getRange(rowIndex, STATUS_COLUMN_INDEX);

    let statusValue = newStatus;

    if (newStatus === TASK_STATUS_ERROR && errorMessage) {
      statusValue += `: ${errorMessage.substring(0, 250)}`; // Append error details, limit length
    }
    statusCell.setValue(statusValue);

    // Optional: Hide the row if the status is Declined
    if (newStatus === TASK_STATUS_DECLINED) {
      sheet.hideRows(rowIndex);
    }

    // Optional: Clear the checkbox after processing (success or error)
    // sheet.getRange(rowIndex, APPROVE_COLUMN_INDEX).setValue(false); // Or clearCheckbox()

    SpreadsheetApp.flush(); // Apply the change immediately
  } catch (e) {
    logToRunLog_(`[updateTaskStatusInSheet_] ERROR updating status for row ${rowIndex}: ${e.message}`);
    // Don't throw here, as the main error is already logged.
  }
}

/**
 * Formats a "YYYY-MM-DD" date string to RFC3339 UTC format (YYYY-MM-DDTHH:mm:ss.sssZ)
 * required by the Google Tasks API. Sets time to midnight UTC.
 * @param {string} dateString The date string in "YYYY-MM-DD" format.
 * @return {string} The formatted date string in RFC3339 UTC.
 * @throws {Error} If the date string is invalid.
 * @private
 */
function formatDateToRFC3339UTC_(dateString) {
  if (!isValidDate_(dateString)) {
    throw new Error(`Invalid date format: "${dateString}". Expected YYYY-MM-DD.`);
  }
  // Parse as YYYY-MM-DD and create date object assumed to be local time zone midnight.
  // Then format as UTC. Tasks API interprets YYYY-MM-DDTHH:mm:ssZ correctly.
  try {
    // Split and create Date object using UTC constructor to avoid timezone issues
    const parts = dateString.split('-');
    const year = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1; // Month is 0-indexed
    const day = parseInt(parts[2], 10);
    const utcDate = new Date(Date.UTC(year, month, day, 0, 0, 0));

    if (isNaN(utcDate.getTime())) {
      throw new Error("Parsed date is invalid.");
    }

    // Format using Utilities.formatDate in UTC timezone
    return Utilities.formatDate(utcDate, "UTC", "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'");
  } catch (e) {
    throw new Error(`Error formatting date "${dateString}" to RFC3339 UTC: ${e.message}`);
  }
}

/**
 * Basic check if a string looks like YYYY-MM-DD.
 * (Copied from EmailProcessor.gs for self-containment, could be moved to a common Util file)
 * @param {string} dateString The string to check.
 * @return {boolean} True if the format matches, false otherwise.
 * @private
 */
function isValidDate_(dateString) {
  if (!dateString || typeof dateString !== 'string') return false;
  return /^\d{4}-\d{2}-\d{2}$/.test(dateString);
}
