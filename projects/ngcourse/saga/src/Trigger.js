/**
 * @fileoverview Contains functions for managing time-driven triggers.
 */

/**
 * Creates a time-driven trigger to run the email processing function daily.
 * Deletes existing triggers for the same function first to avoid duplicates.
 */
function createDailyEmailProcessingTrigger_() {
  const functionNameToTrigger = 'fetchAndProcessEmails_';
  const functionName = 'createDailyEmailProcessingTrigger_';

  try {
    // Delete existing triggers for this function to prevent duplicates
    deleteSpecificTrigger_(functionNameToTrigger);

    // Create a new trigger to run daily at a random time between 1 AM and 5 AM
    // This helps distribute load on Google's servers.
    const triggerTime = new Date();
    triggerTime.setHours(Math.floor(Math.random() * 4) + 1); // Random hour 1-4
    triggerTime.setMinutes(Math.floor(Math.random() * 60)); // Random minute 0-59

    ScriptApp.newTrigger(functionNameToTrigger)
      .timeBased()
      .everyDays(1)
      .at(triggerTime) // Use the specific time object
      .create();

    const message = `Successfully created daily trigger for '${functionNameToTrigger}' to run around ${triggerTime.toLocaleTimeString()}.`;
    logToRunLog_(`[${functionName}] ${message}`);
    safeAlert_(message);

  } catch (e) {
    const errorMessage = `[${functionName}] ERROR creating trigger: ${e.message}`;
    logToRunLog_(errorMessage);
    safeAlert_(`Error creating trigger: ${e.message}`);
  }
}

/**
 * Deletes all triggers associated with the current script project.
 */
function deleteProjectTriggers_() {
  const functionName = 'deleteProjectTriggers_';
  try {
    const triggers = ScriptApp.getProjectTriggers();
    if (triggers.length === 0) {
      logToRunLog_(`[${functionName}] No project triggers found to delete.`);
      safeAlert_('No project triggers found to delete.');
      return;
    }

    let deletedCount = 0;
    triggers.forEach(trigger => {
      try {
        const handlerFunction = trigger.getHandlerFunction();
        ScriptApp.deleteTrigger(trigger);
        deletedCount++;
        logToRunLog_(`[${functionName}] Deleted trigger for function: ${handlerFunction}`);
      } catch (deleteErr) {
        logToRunLog_(`[${functionName}] ERROR deleting a trigger: ${deleteErr.message}`);
      }
    });

    const message = `Deleted ${deletedCount} project trigger(s).`;
    logToRunLog_(`[${functionName}] ${message}`);
    safeAlert_(message);

  } catch (e) {
    const errorMessage = `[${functionName}] ERROR deleting triggers: ${e.message}`;
    logToRunLog_(errorMessage);
    safeAlert_(`Error deleting triggers: ${e.message}`);
  }
}

/**
 * Deletes a specific trigger by its handler function name.
 * @param {string} functionName The name of the function the trigger runs.
 * @private
 */
function deleteSpecificTrigger_(functionName) {
  const triggers = ScriptApp.getProjectTriggers();
  let deletedCount = 0;
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === functionName) {
      try {
        ScriptApp.deleteTrigger(trigger);
        deletedCount++;
        logToRunLog_(`[deleteSpecificTrigger_] Deleted existing trigger for: ${functionName}`);
      } catch (e) {
        logToRunLog_(`[deleteSpecificTrigger_] ERROR deleting existing trigger for ${functionName}: ${e.message}`);
      }
    }
  });
  return deletedCount;
}