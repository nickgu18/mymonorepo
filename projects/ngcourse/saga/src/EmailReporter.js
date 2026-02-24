/**
 * @fileoverview Handles sending summary email reports.
 */

/**
 * Sends a summary email report after processing.
 *
 * @param {number} totalThreadsFound Total threads matching the initial query.
 * @param {number} processedPass1 Count of emails successfully scored in Pass 1.
 * @param {number} errorsPass1 Count of errors during Pass 1 (preprocessing or AI).
 * @param {number} attemptedPass2 Count of emails attempted for task extraction in Pass 2.
 * @param {Array<object>} proposedTasks Array of proposed task objects { taskName, targetDate, sourceEmailId, dateProposed }.
 * @param {number} errorsPass2 Count of batch errors during Pass 2 AI calls/parsing.
 * @param {number} markedReadCount Count of threads successfully marked as read.
 * @param {Array<object>} highRelevanceEmailInfo Array of objects {subject, from, score, threadId} for emails meeting relevance threshold.
 * @private
 */
function sendDailySummaryEmail_(totalThreadsFound, processedPass1, errorsPass1,
                                attemptedPass2, proposedTasks, errorsPass2,
                                markedReadCount, highRelevanceEmailInfo) {
  const functionName = 'sendDailySummaryEmail_';
  logToRunLog_(`[${functionName}] Preparing summary email...`);

  try {
    // --- 1. Get Configuration ---
    const config = getConfig_();
    if (!config) {
      logToRunLog_(`[${functionName}] ERROR: Cannot send email. Failed to load configuration.`);
      return;
    }
    const recipientEmail = config['RECIPIENT_EMAIL'];
    const taskProposalSheetName = config['TASK_PROPOSAL_SHEET'] || 'Task Proposal';
    const runLogSheetName = config['RUN_LOG_SHEET'] || 'Run Log';
    const relevanceThreshold = parseInt(config['RELEVANCE_THRESHOLD_FOR_TASKS'] || '4', 10); // Get threshold for context

    if (!recipientEmail || recipientEmail === 'YOUR_EMAIL_HERE') {
      logToRunLog_(`[${functionName}] WARNING: Recipient email not configured. Skipping summary email.`);
      return;
    }

    // --- 2. Get Spreadsheet Info ---
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const spreadsheetUrl = ss.getUrl();
    const spreadsheetName = ss.getName();
    const runLogSheetUrl = `${spreadsheetUrl}#gid=${ss.getSheetByName(runLogSheetName)?.getSheetId() || ''}`;
    const taskProposalSheetUrl = `${spreadsheetUrl}#gid=${ss.getSheetByName(taskProposalSheetName)?.getSheetId() || ''}`;

    // --- 3. Construct Email ---
    const subject = `Saga Assistant Daily Summary - ${spreadsheetName}`;
    const totalErrors = errorsPass1 + errorsPass2;
    const tasksProposedCount = proposedTasks.length; // Get count from array

    // --- Construct Task List ---
    let proposedTasksHtml = '<h3>Proposed Tasks:</h3>';
    if (tasksProposedCount > 0) {
      proposedTasksHtml += '<ul>';
      proposedTasks.forEach(task => {
        // Basic HTML escaping for task names
        const escapedTaskName = task.taskName.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>');
        proposedTasksHtml += `<li>${escapedTaskName}${task.targetDate ? ` (Target: ${task.targetDate})` : ''}</li>`;
      });
      proposedTasksHtml += '</ul>';
    } else {
      proposedTasksHtml += '<p><i>No new tasks were proposed in this run.</i></p>';
    }
    proposedTasksHtml += '<hr>'; // Add separator

    // --- Construct High Relevance Email List ---
    let highRelevanceEmailsHtml = `<h3>High Relevance Emails (Score >= ${relevanceThreshold}):</h3>`;
    if (highRelevanceEmailInfo && highRelevanceEmailInfo.length > 0) {
       highRelevanceEmailsHtml += '<ul>';
       highRelevanceEmailInfo.forEach(email => {
           const escapedSubject = (email.subject || '(No Subject)').replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>');
           const escapedFrom = (email.from || 'Unknown Sender').replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>');
           const emailUrl = `https://mail.google.com/mail/#all/${email.threadId}`;
           highRelevanceEmailsHtml += `<li>[${email.score}] <a href="${emailUrl}">${escapedSubject}</a> (From: ${escapedFrom})</li>`;
       });
       highRelevanceEmailsHtml += '</ul>';
    } else {
        highRelevanceEmailsHtml += `<p><i>No emails met the relevance threshold (>= ${relevanceThreshold}) in this run.</i></p>`;
    }
    highRelevanceEmailsHtml += '<hr>';

    const body = `
      <html><body>
      <h2>Saga Assistant Daily Run Summary</h2>
      <p><strong>Spreadsheet:</strong> <a href="${spreadsheetUrl}">${spreadsheetName}</a></p>
      ${proposedTasksHtml}
      ${highRelevanceEmailsHtml}
      <h3>Processing Overview:</h3>
      <ul>
        <li>Threads Found Matching Query: ${totalThreadsFound}</li>
        <li>Threads Scored (Pass 1): ${processedPass1} (Errors: ${errorsPass1})</li>
        <li>Relevant Threads Analyzed for Tasks (Pass 2): ${attemptedPass2} (Batch Errors: ${errorsPass2})</li>
        <li><b>Total Tasks Proposed: ${tasksProposedCount}</b></li>
        <li>Threads Marked as Read: ${markedReadCount}</li>
        <li>Total Errors Encountered: ${totalErrors}</li>
      </ul>
      <hr>
      <h3>Next Steps:</h3>
      <ul>
        <li>Review proposed tasks in the <a href="${taskProposalSheetUrl}">"${taskProposalSheetName}" sheet</a>.</li>
        <li>Check the <a href="${runLogSheetUrl}">"${runLogSheetName}" sheet</a> for detailed logs${totalErrors > 0 ? ' and error messages' : ''}.</li>
      </ul>
      <p><small>This is an automated email from the Saga Assistant Apps Script.</small></p>
      </body></html>
    `;

    // --- 4. Send Email ---
    MailApp.sendEmail(recipientEmail, subject, "", { htmlBody: body, name: "Saga Assistant" });
    logToRunLog_(`[${functionName}] Summary email sent successfully to ${recipientEmail}.`);

  } catch (e) {
    logToRunLog_(`[${functionName}] ERROR sending summary email: ${e.message}\nStack: ${e.stack || 'N/A'}`);
  }
}