/**
 * @fileoverview Contains logic for running evaluations on email scoring.
 */

/**
 * Runs the evaluation pipeline:
 * 1. Reads 'evals' sheet for test cases.
 * 2. Scores them using 'Current Goal' (N2).
 * 3. Writes predictions to 'Predicted Category' (H).
 * 4. Generates a revised goal based on mistakes.
 * 5. Scores again using 'Revised Goal'.
 * 6. Writes revised predictions to 'Revised Category' (K).
 */
function runEvalCommand() {
    const functionName = 'runEvalCommand';
    logToRunLog_(`[${functionName}] Starting Evaluation Run...`);

    try {
        const ss = SpreadsheetApp.getActiveSpreadsheet();
        const evalSheet = ss.getSheetByName('evals');
        if (!evalSheet) {
            throw new Error("Sheet 'evals' not found.");
        }

        // 1. Configuration & Data Loading
        const config = getConfig_();
        const apiKey = getApiKey_();
        const apiEndpoint = config['AI_API_ENDPOINT'];
        
        if (!apiKey || !apiEndpoint) {
            safeAlert_('AI API Key or Endpoint not configured.');
            return;
        }

        const currentGoal = evalSheet.getRange('N2').getValue();
        logToRunLog_(`[${functionName}] Current Goal: ${currentGoal.substring(0, 50)}...`);

        // Read Test Cases
        const lastRow = evalSheet.getLastRow();
        if (lastRow < 2) {
            safeAlert_('No data in evals sheet.');
            return;
        }

        // Columns: A=1, B=2, C=3, D=4, E=5, F=6 (ThreadID), G=7 (MsgID), H=8 (Pred), I=9 (Actual), J=10 (Gap), K=11 (Revised)
        // Read A2:I(lastRow) to get IDs and Actual scores
        const dataRange = evalSheet.getRange(2, 1, lastRow - 1, 9);
        const dataValues = dataRange.getValues();

        // 2. Fetch Emails
        const emailDataList = [];
        const rowIndices = []; // Keep track of which row corresponds to which email

        logToRunLog_(`[${functionName}] Fetching emails for ${dataValues.length} test cases...`);

        dataValues.forEach((row, index) => {
            const threadId = row[5]; // Column F
            const messageId = row[6]; // Column G
            const actualScore = row[8]; // Column I (if needed for comparison later)
            
            if (threadId) {
                try {
                    // We need to fetch the email content. 
                    // Optimization: If we have messageId, get that specific message.
                    // If not, get thread.
                    let emailBody = "";
                    let subject = row[2]; // Column C
                    let from = row[3]; // Column D
                    let date = row[4]; // Column E

                    // If body is not in sheet, we MUST fetch it.
                    // Assuming body is NOT in sheet, we fetch from Gmail.
                    const thread = GmailApp.getThreadById(threadId);
                    if (thread) {
                        const msgs = thread.getMessages();
                        const msg = msgs.find(m => m.getId() === messageId) || msgs[0];
                        emailBody = msg.getPlainBody().substring(0, 15000); // MAX_BODY_LENGTH
                        if (!subject) subject = msg.getSubject();
                        if (!from) from = msg.getFrom();
                        if (!date) date = msg.getDate();
                    } else {
                        logToRunLog_(`[${functionName}] Warning: Thread ${threadId} not found in Gmail.`);
                    }

                    emailDataList.push({
                        threadId: threadId,
                        messageId: messageId,
                        subject: subject,
                        from: from,
                        date: new Date(date),
                        emailBody: emailBody
                    });
                    rowIndices.push(index + 2); // 1-based row index
                } catch (e) {
                    logToRunLog_(`[${functionName}] Error fetching thread ${threadId}: ${e.message}`);
                }
            }
        });

        if (emailDataList.length === 0) {
            safeAlert_('No valid emails found to process.');
            return;
        }

        // 3. Pass 1: Baseline Scoring
        logToRunLog_(`[${functionName}] Running Baseline Scoring...`);
        const baselineResults = scoreEmailsInBatches_(emailDataList, currentGoal, [], apiKey, apiEndpoint);

        // 4. Write Baseline Results
        const predColumnValues = new Array(lastRow - 1).fill([null]); // Initialize column H
        const baselineResultsMap = {}; // Map for easy lookup

        baselineResults.forEach(res => {
            baselineResultsMap[res.threadId] = res;
        });

        // Update predColumnValues based on row mapping
        dataValues.forEach((row, i) => {
            const threadId = row[5];
            if (baselineResultsMap[threadId]) {
                predColumnValues[i] = [baselineResultsMap[threadId].score];
            }
        });

        evalSheet.getRange(2, 8, lastRow - 1, 1).setValues(predColumnValues); // Column H
        SpreadsheetApp.flush(); // Ensure written before reading back if needed (though we have data in memory)

        // 5. Analyze Gaps & Generate Revision
        logToRunLog_(`[${functionName}] Analyzing gaps and generating revision...`);
        
        // Identify mistakes: Where Gap (Actual - Predicted) != 0
        // We can calculate gap in JS or read from sheet if formula exists. 
        // Let's calculate in JS to be safe and fast.
        const mistakes = [];
        dataValues.forEach((row, i) => {
            const threadId = row[5];
            const actualScore = row[8]; // Column I
            const notes = row[1]; // Column B
            const subject = row[2];
            const predictedScore = baselineResultsMap[threadId]?.score;

            if (typeof actualScore === 'number' && typeof predictedScore === 'number') {
                if (actualScore !== predictedScore) {
                    mistakes.push({
                        threadId,
                        subject,
                        notes,
                        actual: actualScore,
                        predicted: predictedScore
                    });
                }
            }
        });

        if (mistakes.length === 0) {
            logToRunLog_(`[${functionName}] No mistakes found! Perfect score.`);
            safeAlert_('Evaluation complete. No mistakes found!');
            return;
        }

        logToRunLog_(`[${functionName}] Found ${mistakes.length} mistakes. Generating revision...`);

        // Construct Prompt for Revision
        const mistakesContext = mistakes.map(m => 
            `- Subject: "${m.subject}"\n  Notes: ${m.notes}\n  Predicted: ${m.predicted}, Actual: ${m.actual}`
        ).join('\n');

        const revisionPrompt = `I am refining my email relevance scoring goals.
Current Goal: "${currentGoal}"

Here are some emails that were scored INCORRECTLY based on this goal:
${mistakesContext}

Please suggest a REVISED Goal string that would correctly handle these cases while maintaining the intent of the original goal.
The revised goal should be specific enough to catch these edge cases.
Respond ONLY with the revised goal text.`;

        let revisedGoal = "";
        try {
            revisedGoal = callGenerativeAI_(revisionPrompt, apiKey, apiEndpoint);
            // Clean up response if needed (remove quotes etc)
            revisedGoal = revisedGoal.replace(/^"|"$/g, '').trim();
            
            // Write to N4
            evalSheet.getRange('N4').setValue(revisedGoal);
            logToRunLog_(`[${functionName}] Suggested Revision written to N4.`);
        } catch (e) {
            logToRunLog_(`[${functionName}] Error generating revision: ${e.message}`);
            safeAlert_('Error generating revision. Check logs.');
            return;
        }

        // 6. Pass 2: Verification Scoring
        logToRunLog_(`[${functionName}] Running Verification Scoring with Revised Goal...`);
        const verificationResults = scoreEmailsInBatches_(emailDataList, revisedGoal, [], apiKey, apiEndpoint);

        // 7. Write Verification Results
        const revisedColumnValues = new Array(lastRow - 1).fill([null]); // Initialize column K
        const verificationResultsMap = {};

        verificationResults.forEach(res => {
            verificationResultsMap[res.threadId] = res;
        });

        dataValues.forEach((row, i) => {
            const threadId = row[5];
            if (verificationResultsMap[threadId]) {
                revisedColumnValues[i] = [verificationResultsMap[threadId].score];
            }
        });

        evalSheet.getRange(2, 11, lastRow - 1, 1).setValues(revisedColumnValues); // Column K
        
        logToRunLog_(`[${functionName}] Evaluation Run Complete.`);
        safeAlert_('Evaluation Run Complete. Check "evals" sheet.');

    } catch (e) {
        logToRunLog_(`[${functionName}] Error: ${e.message}\nStack: ${e.stack}`);
        safeAlert_(`Error running eval: ${e.message}`);
    }
}
