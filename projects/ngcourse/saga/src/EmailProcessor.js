/**
 * @fileoverview Contains functions for fetching emails, scoring relevance, and extracting tasks using batch processing.
 */

// --- Constants ---
const AI_MODEL_TEMPERATURE = 0.5; // Adjust creativity/randomness (0.0 - 1.0)
const MAX_BODY_LENGTH = 15000; // Limit email body length sent to AI
const RELEVANCE_THRESHOLD_FOR_TASKS = 4; // Minimum score (inclusive) from Pass 1 to trigger Pass 2
const MAX_EMAILS_PER_BATCH_PASS1 = 50; // Limit emails per AI call in Pass 1 (Relevance)
const MAX_EMAILS_PER_BATCH_PASS2 = 20; // Limit emails per AI call in Pass 2 (Tasks) - Potentially smaller due to response size

/**
 * Fetches unread emails, gets AI relevance score (Pass 1 - BATCHED), then extracts tasks
 * for highly relevant emails (Pass 2 - BATCHED). Writes results to sheets and marks
 * successfully processed emails as read.
 */
function fetchAndProcessEmails_() {
    const functionName = 'fetchAndProcessEmails_';
    logToRunLog_(`[${functionName}] Starting TWO-PASS email fetch and processing (BOTH PASSES BATCHED)...`);

    let config; // Declare config here for broader scope

    try {
        // --- 1. Get Configuration ---
        config = getConfig_(); // From SheetManager.gs
        if (!config) {
            throw new Error("Failed to load configuration.");
        }
        let daysToQuery = parseInt(config['EMAIL_QUERY_DAYS'] || '1', 10);
        const summaryLogSheetName = config['SUMMARY_LOG_SHEET'] || 'Summary Log';
        const taskProposalSheetName = config['TASK_PROPOSAL_SHEET'] || 'Task Proposal';
        const apiKey = getApiKey_(); // From SheetManager.gs
        const apiEndpoint = config['AI_API_ENDPOINT']; // Get endpoint from config
        const myGoals = config['MY_GOALS'] || ''; // Load My Goals config
        const rules = config['RULES'] || []; // Load RULES. Expects an array.

        if (!apiKey || !apiEndpoint || apiEndpoint === 'YOUR_AI_ENDPOINT_URL_HERE') {
            logToRunLog_(`[${functionName}] ERROR: AI API Key or Endpoint not configured.`);
            safeAlert_('AI API Key or Endpoint not configured. Please check configuration and run "Set AI API Key" from the menu.');
            return;
        }
        if (isNaN(daysToQuery) || daysToQuery <= 0) {
            logToRunLog_(`[${functionName}] Invalid EMAIL_QUERY_DAYS: ${config['EMAIL_QUERY_DAYS']}. Using default 1 day.`);
            daysToQuery = 1;
        }
        if (!myGoals) {
            logToRunLog_(`[${functionName}] Warning: 'MY_GOALS' not configured in Configuration sheet. Relevance scoring may be less accurate.`);
        } else {
            logToRunLog_(`[${functionName}] Using My Goals for relevance scoring: ${myGoals.substring(0, 100)}...`);
        }
        if (rules.length > 0) {
            logToRunLog_(`[${functionName}] Using ${rules.length} custom RULES for filtering.`);
        }

        // --- 2. Build Gmail Query & Fetch Threads ---
        const queryDate = new Date();
        queryDate.setDate(queryDate.getDate() - daysToQuery);
        const formattedDate = Utilities.formatDate(queryDate, Session.getScriptTimeZone(), "yyyy/MM/dd");
        const searchQuery = `is:unread after:${formattedDate}`;
        logToRunLog_(`[${functionName}] Using Gmail query: "${searchQuery}"`);

        const MAX_THREADS_PER_RUN = 50; // Limit threads per run overall
        const threads = GmailApp.search(searchQuery, 0, MAX_THREADS_PER_RUN);
        logToRunLog_(`[${functionName}] Found ${threads.length} unread thread(s) matching query (limit ${MAX_THREADS_PER_RUN}).`);

        if (threads.length === 0) {
            logToRunLog_(`[${functionName}] No new unread emails to process.`);
            safeAlert_('No new unread emails found matching the criteria.');
            return;
        }

        // --- 3. Initialize Results ---
        let pass1Results = []; // Stores { threadId, messageId, subject, from, date, score, justification, pass1Success, emailBody, error? }
        let allProposedTasks = []; // Stores tasks from Pass 2
        let processedCountPass1 = 0;
        let errorCountPass1 = 0;
        let errorCountPass2 = 0;
        let threadsToMarkRead = new Set(); // Threads where Pass 1 succeeded

        // --- 4. PASS 1: Relevance Scoring (BATCH PROCESSING) ---
        logToRunLog_(`[${functionName}] --- Starting Pass 1: Relevance Scoring for ${threads.length} threads (Batches of ${MAX_EMAILS_PER_BATCH_PASS1}) ---`);

        // 4a. Pre-process: Gather email data
        let allEmailDataForPass1 = [];
        threads.forEach(thread => {
            const threadId = thread.getId();
            const subject = thread.getFirstMessageSubject();
            let emailData = { threadId: threadId, subject: subject, pass1Success: false };
            try {
                const messages = thread.getMessages();
                if (messages.length === 0) throw new Error("No messages found");
                const lastMessage = messages[messages.length - 1];
                emailData.messageId = lastMessage.getId();
                emailData.from = lastMessage.getFrom();
                emailData.date = lastMessage.getDate();
                emailData.emailBody = lastMessage.getPlainBody().substring(0, MAX_BODY_LENGTH);
                allEmailDataForPass1.push(emailData);
            } catch (err) {
                errorCountPass1++;
                emailData.error = `Error preprocessing: ${err.message}`;
                pass1Results.push(emailData);
                logToRunLog_(`[${functionName}] Pass 1 Pre-process ERROR for thread ${threadId}: ${err.message}`);
            }
        });

        // 4b. Process Relevance in Batches
        const scoringResults = scoreEmailsInBatches_(allEmailDataForPass1, myGoals, rules, apiKey, apiEndpoint);

        // 4c. Merge Results
        scoringResults.forEach(result => {
            if (result.pass1Success) {
                processedCountPass1++;
                threadsToMarkRead.add(result.threadId);
            } else {
                errorCountPass1++;
            }
            pass1Results.push(result);
        });

        logToRunLog_(`[${functionName}] --- Finished Pass 1 (Batched): Scored=${processedCountPass1}, Errors=${errorCountPass1} ---`);

        // --- 5. Write Pass 1 Results to Log ---
        if (pass1Results.length > 0) {
            writeRelevanceScoresToLog_(pass1Results, summaryLogSheetName);
        } else {
            logToRunLog_(`[${functionName}] No Pass 1 results to write to log.`);
        }

        // --- 6. PASS 2: Task Extraction (BATCH PROCESSING for relevant emails) ---
        const relevantEmailsForTasks = pass1Results.filter(r => r.pass1Success && r.score >= RELEVANCE_THRESHOLD_FOR_TASKS);
        logToRunLog_(`[${functionName}] --- Starting Pass 2: Task Extraction for ${relevantEmailsForTasks.length} relevant threads (Batches of ${MAX_EMAILS_PER_BATCH_PASS2}) ---`);

        if (relevantEmailsForTasks.length > 0) {
            for (let i = 0; i < relevantEmailsForTasks.length; i += MAX_EMAILS_PER_BATCH_PASS2) {
                const batchTaskData = relevantEmailsForTasks.slice(i, i + MAX_EMAILS_PER_BATCH_PASS2);
                const batchNum = Math.floor(i / MAX_EMAILS_PER_BATCH_PASS2) + 1;
                logToRunLog_(`[${functionName}] Pass 2: Processing Task Batch ${batchNum} (${batchTaskData.length} emails)`);

                if (batchTaskData.length === 0) continue;

                // 6a. Construct Batch Task Prompt
                let taskEmailListString = batchTaskData.map(e => `
--- Email Start ---
ID: ${e.threadId}
Subject: ${e.subject}
From: ${e.from}
Body Preview (up to ${MAX_BODY_LENGTH} chars):
${e.emailBody}
--- Email End ---`).join("\n");

                const batchTaskPrompt = `Analyze the following list of emails. For EACH email ID, identify the 1-3 most critical action items/tasks for the recipient. Focus on tasks advancing key objectives or resolving urgent issues.

Format the output ONLY as a single JSON object where keys are the Email IDs.
The value for each Email ID MUST be a JSON array of task objects. Each task object MUST have:
- "taskName": A string describing the specific action.
- "targetDate": A string "YYYY-MM-DD" if mentioned, otherwise the JSON value null.

If no critical tasks are found for an email, the value for its ID MUST be an empty JSON array: []

Example valid output fragment:
{
  "threadIdABC": [
    {"taskName": "Prepare Q3 budget draft", "targetDate": "2024-07-15"},
    {"taskName": "Follow up with Marketing", "targetDate": null}
  ],
  "threadIdDEF": [],
  "threadIdGHI": [
    {"taskName": "Review project proposal", "targetDate": null}
  ]
}

If analysis fails for an ID, you MAY omit it from the response JSON.

--- Email List ---
${taskEmailListString}
--- End Email List ---

JSON Output:`;

                // 6b. Call AI & Parse Batch Tasks
                try {
                    const batchTaskResultText = callGenerativeAI_(batchTaskPrompt, apiKey, apiEndpoint);
                    // Pass batchTaskData to parser to get original threadId, subject etc. for context if needed during parsing/logging
                    const extractedTasksFromBatch = parseBatchTaskResponse_(batchTaskResultText, batchTaskData);
                    allProposedTasks = allProposedTasks.concat(extractedTasksFromBatch); // Add successfully parsed tasks
                    logToRunLog_(`[${functionName}] Pass 2 Batch ${batchNum}: AI call successful. Extracted ${extractedTasksFromBatch.length} total tasks from batch.`);
                    // Note: Error count below handles cases where AI *doesn't return* an entry for an email in the batch

                } catch (batchErr) {
                    errorCountPass2 += batchTaskData.length; // Count all emails in the failed batch as errors for Pass 2
                    logToRunLog_(`[${functionName}] Pass 2 Batch ${batchNum} ERROR: AI call/parsing failed. Error: ${batchErr.message}. Skipping tasks for this batch.`);
                    // Optionally, add error indicators to the individual pass1Results objects for these emails?
                    // For now, just count the error and skip task creation.
                }
            } // End Pass 2 Batch Loop
        } else {
            logToRunLog_(`[${functionName}] No relevant emails found meeting threshold (Score >= ${RELEVANCE_THRESHOLD_FOR_TASKS}) for Pass 2.`);
        }

        // Calculate final Pass 2 error count (includes emails missed within successful batches)
        const emailsAttemptedPass2 = relevantEmailsForTasks.length;
        const emailsWithTasksFound = new Set(allProposedTasks.map(t => t.sourceEmailId)).size;
        // Initial error count is from failed batches. Add emails from successful batches that didn't yield tasks.
        // This calculation is slightly approximate as parseBatchTaskResponse logs specific missing IDs.
        // A more precise way would be for the parser to return which IDs failed.
        // errorCountPass2 = (emailsAttemptedPass2 - emailsWithTasksFound); // Overwrite previous count? Or add? Let's refine.
        // Let's stick to counting batch failures in errorCountPass2 for now, and rely on logs for missing IDs within batches.

        logToRunLog_(`[${functionName}] --- Finished Pass 2 (Batched): Attempted=${emailsAttemptedPass2}, Batch Errors=${errorCountPass2}, Total Tasks Proposed=${allProposedTasks.length} ---`);

        // --- 7. Write Proposed Tasks (from Pass 2) ---
        if (allProposedTasks.length > 0) {
            writeTasksToProposalSheet_(allProposedTasks, taskProposalSheetName);
        } else {
            logToRunLog_(`[${functionName}] No tasks proposed in Pass 2 to write to sheet.`);
        }

        // --- 8. Mark Threads as Read ---
        // Mark threads read ONLY if Pass 1 was successful for them
        logToRunLog_(`[${functionName}] Attempting to mark ${threadsToMarkRead.size} threads as read (where Pass 1 succeeded)...`);
        const markedReadCount = markThreadsAsRead_(threadsToMarkRead); // Get the count of successfully marked threads
        logToRunLog_(`[${functionName}] Finished marking threads as read attempt.`);

        // --- 9. Final Logging & User Feedback ---
        const finalErrorCount = errorCountPass1 + errorCountPass2; // Sum errors from both passes

        // Prepare concise info for summary email about high-relevance emails
        const highRelevanceEmailInfo = relevantEmailsForTasks.map(e => ({
            subject: e.subject,
            from: e.from,
            score: e.score,
            threadId: e.threadId
        }));

        // --- 10. Send Summary Email ---
        // Pass relevant counts, the actual proposed tasks array, and high-relevance email info
        sendDailySummaryEmail_(threads.length, processedCountPass1, errorCountPass1, // Pass 1 info
            emailsAttemptedPass2, allProposedTasks, errorCountPass2, // Pass 2 info (pass task array)
            markedReadCount, highRelevanceEmailInfo); // Other info + High relevance list

        const completionMessage = `Processing complete. Pass 1: ${processedCountPass1}/${threads.length} emails scored (${errorCountPass1} errors). Pass 2: ${emailsAttemptedPass2} relevant emails analyzed (${errorCountPass2} batch errors), ${allProposedTasks.length} tasks proposed. Summary email sent. Check logs/sheets.`;
        logToRunLog_(`[${functionName}] ${completionMessage}`);
        safeAlert_(completionMessage + (finalErrorCount > 0 ? ` ${finalErrorCount} total errors occurred.` : ''));

    } catch (e) {
        // Catch fatal errors
        const errorMessage = `[${functionName}] FATAL Error: ${e.message}\nStack: ${e.stack || 'No stack trace available'}`;
        logToRunLog_(errorMessage);
        let safeConfig; try { safeConfig = getConfig_(); } catch (_) { }
        const userMessage = `FATAL Error: ${e.message}. Check '${safeConfig ? (safeConfig['RUN_LOG_SHEET'] || 'Run Log') : 'Run Log'}' sheet.`;
        safeAlert_(userMessage);
    }
}

/**
 * Scores a list of emails in batches using the AI.
 * @param {Array<object>} emailDataList List of email data objects {threadId, subject, from, date, emailBody, ...}
 * @param {string} goals User goals string
 * @param {Array<string>} rules User rules array
 * @param {string} apiKey AI API Key
 * @param {string} apiEndpoint AI API Endpoint
 * @return {Array<object>} List of email data objects with 'score', 'justification', 'pass1Success', 'error' added.
 */
function scoreEmailsInBatches_(emailDataList, goals, rules, apiKey, apiEndpoint) {
    const functionName = 'scoreEmailsInBatches_';
    const results = [];

    if (!emailDataList || emailDataList.length === 0) return results;

    logToRunLog_(`[${functionName}] Scoring ${emailDataList.length} emails in batches of ${MAX_EMAILS_PER_BATCH_PASS1}...`);

    for (let i = 0; i < emailDataList.length; i += MAX_EMAILS_PER_BATCH_PASS1) {
        const batchEmailData = emailDataList.slice(i, i + MAX_EMAILS_PER_BATCH_PASS1);
        const batchNum = Math.floor(i / MAX_EMAILS_PER_BATCH_PASS1) + 1;
        logToRunLog_(`[${functionName}] Processing Batch ${batchNum} (${batchEmailData.length} emails)`);

        // Construct Batch Relevance Prompt
        let emailListString = batchEmailData.map(e => `
--- Email Start ---
ID: ${e.threadId}
Subject: ${e.subject}
From: ${e.from}
Date: ${Utilities.formatDate(e.date, Session.getScriptTimeZone(), "yyyy-MM-dd")}
Body Preview (up to ${MAX_BODY_LENGTH} chars):
${e.emailBody}
--- Email End ---`).join("\n");

        // Include My Goals in the prompt if available
        const goalsContext = goals ? `
My current priorities/goals are:
${goals}
Consider these goals when rating relevance. High relevance (4-5) emails directly relate to or significantly impact these goals.
` : `Consider general business importance for relevance scoring.`;

        const rulesContext = Array.isArray(rules) && rules.length > 0 ? `
Additionally, apply these filtering RULES:
${rules.map(rule => `- ${rule}`).join('\n')}
Emails matching these rules might have their relevance adjusted. For example, an email from a specific sender mentioned in the rules might be considered less relevant.
` : '';

        const batchRelevancePrompt = `Analyze the following list of emails. For EACH email, rate relevance (1-5) based on its importance and urgency to me, and provide a brief justification.

${goalsContext}
${rulesContext}

Relevance Scale:
1=Noise/Spam/Unimportant
2=Low Priority/Informational/FYI
3=Moderate Importance/Routine Operations
4=High Importance/Requires Attention/Actionable for Goals
5=Critical/Urgent/Directly Impacts Key Goals

Respond ONLY with a single JSON object where keys are Email IDs and values are {"relevanceScore": number, "justification": string}. Max 100 chars for justification.
Example: {"threadId123": {"relevanceScore": 4, "justification": "Impacts Q3 roadmap goal."}, "threadId456": {"relevanceScore": 2, "justification": "Team update FYI."}}
If analysis fails for an ID, omit it from the JSON.

--- Email List ---
${emailListString}
--- End Email List ---

JSON Output:`;

        // Call AI & Parse Batch Relevance
        let batchResultsMap = {};
        let batchAiCallSuccess = false;
        try {
            const batchResultText = callGenerativeAI_(batchRelevancePrompt, apiKey, apiEndpoint);
            batchResultsMap = parseBatchRelevanceResponse_(batchResultText, batchEmailData.map(e => e.threadId));
            batchAiCallSuccess = true;
            logToRunLog_(`[${functionName}] Batch ${batchNum}: AI call successful. Parsed ${Object.keys(batchResultsMap).length} results.`);
        } catch (batchErr) {
            logToRunLog_(`[${functionName}] Batch ${batchNum} ERROR: AI call/parsing failed. Error: ${batchErr.message}`);
            batchEmailData.forEach(emailInfo => {
                results.push({ ...emailInfo, pass1Success: false, error: `Batch AI call/parse failed: ${batchErr.message.substring(0, 150)}` });
            });
            continue; // Next batch
        }

        // Merge Batch Relevance Results
        batchEmailData.forEach(emailInfo => {
            const { threadId } = emailInfo;
            const resultFromAi = batchResultsMap[threadId];
            if (resultFromAi) {
                results.push({ ...emailInfo, score: resultFromAi.score, justification: resultFromAi.justification, pass1Success: true, error: null });
            } else {
                results.push({ ...emailInfo, pass1Success: false, error: batchAiCallSuccess ? "AI did not return score for this ID." : `Batch AI call/parse failed.` });
                logToRunLog_(`[${functionName}] ERROR: Thread ${threadId} (Batch ${batchNum}) - AI response missing/invalid for this ID.`);
            }
        });
    }

    return results;
}



// ==========================================================================
// Helper Functions: AI Calling & Parsing (ADD Batch Task Parser)
// ==========================================================================

/**
 * Calls the configured Generative AI endpoint. (Unchanged)
 * @private
 */
function callGenerativeAI_(prompt, apiKey, apiEndpoint) {
    const functionName = 'callGenerativeAI_';
    // Ensure endpoint has the key
    let effectiveEndpoint = apiEndpoint;
    if (!effectiveEndpoint.includes('?key=')) {
        effectiveEndpoint += (effectiveEndpoint.includes('?') ? '&' : '?') + 'key=' + apiKey;
    }

    logToRunLog_(`[${functionName}] Calling Gemini endpoint: ${effectiveEndpoint.split('?')[0]}... (Prompt length: ${prompt.length})`);

    const payload = {
        "contents": [{ "parts": [{ "text": prompt }] }],
        "generationConfig": {
            "temperature": AI_MODEL_TEMPERATURE,
            "responseMimeType": "application/json"
        }
    };

    const options = {
        'method': 'post',
        'contentType': 'application/json',
        'payload': JSON.stringify(payload),
        'muteHttpExceptions': true,
        'validateHttpsCertificates': false,
        'readTimeoutMillis': 120000, // 2 minutes
    };

    try {
        const response = UrlFetchApp.fetch(effectiveEndpoint, options);
        const responseCode = response.getResponseCode();
        const responseBody = response.getContentText();
        logToRunLog_(`[${functionName}] Received response code: ${responseCode}. Body length: ${responseBody ? responseBody.length : 0}`);

        if (responseCode >= 200 && responseCode < 300) {
            const jsonData = JSON.parse(responseBody);

            // Gemini Response Parsing
            if (jsonData.candidates && jsonData.candidates[0]?.content?.parts[0]?.text) {
                try {
                    const innerJsonText = jsonData.candidates[0].content.parts[0].text;
                    if (typeof innerJsonText === 'string') {
                        return innerJsonText.trim().replace(/^```json\s*|```$/g, '').trim();
                    } else {
                        return JSON.stringify(innerJsonText);
                    }
                } catch (innerParseError) {
                    throw new Error(`Failed to parse inner JSON from Gemini: ${innerParseError.message}`);
                }
            } else {
                throw new Error('Gemini response missing expected candidates/content/parts/text path.');
            }
        } else {
            let errorDetails = `Gemini API error (${responseCode}).`;
            try {
                const errorJson = JSON.parse(responseBody);
                errorDetails += ` Message: ${errorJson?.error?.message || responseBody}`;
            } catch (e) {
                errorDetails += ` Response: ${responseBody}`;
            }
            logToRunLog_(`[${functionName}] API call failed. ${errorDetails}`);
            throw new Error(errorDetails.substring(0, 500));
        }
    } catch (error) {
        logToRunLog_(`[${functionName}] Exception during Gemini call: ${error.message}`);
        throw new Error(`Gemini call failed: ${error.message}`);
    }
}


/**
 * Parses the AI batch relevance score response (expected JSON string map). (Unchanged)
 * @param {string} jsonResponseText Raw AI response text.
 * @param {string[]} expectedThreadIds Array of thread IDs sent in the batch.
 * @return {object} Map of threadId to { score: number, justification: string }.
 * @throws {Error} If parsing fails or response is fundamentally malformed.
 * @private
 */
function parseBatchRelevanceResponse_(jsonResponseText, expectedThreadIds) {
    // ... (Keep the existing implementation of parseBatchRelevanceResponse_) ...
    const functionName = 'parseBatchRelevanceResponse_';
    const resultsMap = {};

    if (!jsonResponseText || jsonResponseText.trim() === "") {
        throw new Error("[parseBatchRelevanceResponse_] Received empty response text from AI.");
    }
    const cleanedJsonText = jsonResponseText.trim().replace(/^```json\s*|```$/g, '').trim();

    let parsedData;
    try {
        parsedData = JSON.parse(cleanedJsonText);
        if (typeof parsedData !== 'object' || parsedData === null || Array.isArray(parsedData)) {
            if (parsedData?.error?.message) { throw new Error(`AI API returned error: ${parsedData.error.message}`); }
            throw new Error("Parsed JSON is not an object map.");
        }
    } catch (e) {
        logToRunLog_(`[${functionName}] ERROR parsing JSON: ${e.message}. Response: ${cleanedJsonText.substring(0, 500)}`);
        throw new Error(`Failed to parse AI batch relevance JSON: ${e.message}`);
    }

    // Validate each entry
    const receivedIds = new Set();
    for (const threadId in parsedData) {
        if (!parsedData.hasOwnProperty(threadId)) continue;
        receivedIds.add(threadId);

        if (!expectedThreadIds.includes(threadId)) {
            logToRunLog_(`[${functionName}] Warning: AI returned score for unexpected thread ID ${threadId}. Ignoring.`);
            continue;
        }

        const item = parsedData[threadId];
        let score = 3; // Default
        let justification = "Invalid data format.";
        let isValid = false;

        if (typeof item === 'object' && item !== null) {
            if (typeof item.relevanceScore === 'number' && item.relevanceScore >= 1 && item.relevanceScore <= 5) {
                score = Math.floor(item.relevanceScore);
                isValid = true;
            } else {
                logToRunLog_(`[${functionName}] Warning: Invalid 'relevanceScore' for ${threadId}: ${item.relevanceScore}.`);
            }

            if (typeof item.justification === 'string') {
                justification = item.justification.substring(0, 200);
            } else {
                logToRunLog_(`[${functionName}] Warning: Missing/invalid 'justification' for ${threadId}.`);
                if (isValid) justification = `Score ${score} - No justification provided.`;
                else justification = `Invalid score (${item.relevanceScore}) - No justification provided.`;
            }
        } else {
            logToRunLog_(`[${functionName}] Warning: Invalid data structure for ${threadId}. Expected object, got ${typeof item}.`);
        }

        if (isValid) {
            resultsMap[threadId] = { score, justification };
        } else {
            logToRunLog_(`[${functionName}] Skipping result for ${threadId} due to invalid score/data.`);
            // Don't add to resultsMap, the merging logic will mark it as an error
        }
    }

    // Log missing IDs
    const missingIds = expectedThreadIds.filter(id => !receivedIds.has(id));
    if (missingIds.length > 0) {
        logToRunLog_(`[${functionName}] Warning: AI response did not include results for ${missingIds.length} expected thread IDs: [${missingIds.slice(0, 5).join(', ')}${missingIds.length > 5 ? '...' : ''}]`);
    }

    // logToRunLog_(`[${functionName}] Finished parsing batch relevance. Valid results mapped: ${Object.keys(resultsMap).length}/${expectedThreadIds.length}`);
    return resultsMap;
}

/**
 * Parses the AI batch task extraction response (expected JSON map where values are task arrays).
 * @param {string} jsonResponseText The raw text from the AI.
 * @param {Array<object>} batchSourceEmailData Array of email data objects {threadId, subject, messageId,...} included in the batch request. Used for context and creating final task objects.
 * @return {Array<object>} A flat array of validated task objects [{ taskName, targetDate, sourceEmailId, dateProposed }].
 * @throws {Error} If the response is not valid JSON or fundamentally malformed.
 * @private
 */
function parseBatchTaskResponse_(jsonResponseText, batchSourceEmailData) {
    const functionName = 'parseBatchTaskResponse_';
    const allTasks = [];
    const proposedDate = new Date();
    const expectedThreadIds = batchSourceEmailData.map(e => e.threadId);

    if (!jsonResponseText || jsonResponseText.trim() === "") {
        throw new Error("[parseBatchTaskResponse_] Received empty response text from AI.");
    }

    const cleanedJsonText = jsonResponseText.trim().replace(/^```json\s*|```$/g, '').trim();

    let parsedData;
    try {
        parsedData = JSON.parse(cleanedJsonText);
        if (typeof parsedData !== 'object' || parsedData === null || Array.isArray(parsedData)) {
            if (parsedData?.error?.message) { throw new Error(`AI API returned error: ${parsedData.error.message}`); }
            throw new Error("Parsed JSON task response is not an object map.");
        }
        // logToRunLog_(`[${functionName}] Successfully parsed batch task JSON. Found ${Object.keys(parsedData).length} keys.`);
    } catch (e) {
        logToRunLog_(`[${functionName}] ERROR parsing JSON task response: ${e.message}. Raw response text: ${cleanedJsonText.substring(0, 500)}`);
        throw new Error(`Failed to parse AI batch task JSON: ${e.message}`);
    }

    const receivedIds = new Set();
    // Iterate through the thread IDs returned by the AI
    for (const threadId in parsedData) {
        if (!parsedData.hasOwnProperty(threadId)) continue;
        receivedIds.add(threadId);

        // Find the original email data for context (optional, but good practice)
        const sourceEmail = batchSourceEmailData.find(e => e.threadId === threadId);

        if (!sourceEmail) {
            logToRunLog_(`[${functionName}] Warning: AI returned tasks for an unexpected thread ID ${threadId}. Ignoring.`);
            continue;
        }

        const taskArray = parsedData[threadId];

        // Validate that the value is an array
        if (!Array.isArray(taskArray)) {
            logToRunLog_(`[${functionName}] Warning: Expected task array for thread ${threadId}, but received type ${typeof taskArray}. Skipping tasks for this email.`);
            continue; // Skip to the next thread ID
        }

        if (taskArray.length === 0) {
            logToRunLog_(`[${functionName}] Info: AI returned empty task array [] for thread ${threadId}.`);
            continue; // No tasks for this email
        }

        // Process tasks within the array for this threadId
        taskArray.forEach((taskItem, index) => {
            try {
                if (!taskItem || typeof taskItem.taskName !== 'string' || !taskItem.taskName.trim()) {
                    logToRunLog_(`[${functionName}] Skipping task item ${index} for thread ${threadId} due to missing/invalid 'taskName'. Item: ${JSON.stringify(taskItem)}`);
                    return; // continue to next task item in the array
                }

                let targetDate = taskItem.targetDate; // string "YYYY-MM-DD" or null

                // Date Validation/Correction
                if (targetDate !== null) {
                    if (typeof targetDate !== 'string') {
                        logToRunLog_(`[${functionName}] Warning: targetDate is not null/string for task "${taskItem.taskName}" (Thread ${threadId}). Received: ${JSON.stringify(targetDate)}. Ignoring date.`);
                        targetDate = null;
                    } else if (targetDate === "null") { // Handle literal string "null"
                        logToRunLog_(`[${functionName}] Warning: targetDate was string "null" for task "${taskItem.taskName}" (Thread ${threadId}). Correcting to null.`);
                        targetDate = null;
                    } else if (!isValidDate_(targetDate)) {
                        logToRunLog_(`[${functionName}] Warning: Invalid date format for task "${taskItem.taskName}" (Thread ${threadId}). Received: "${targetDate}". Ignoring date.`);
                        targetDate = null;
                    }
                }

                // Add validated task to the main list
                allTasks.push({
                    taskName: taskItem.taskName.trim(),
                    targetDate: targetDate, // Already validated/corrected
                    sourceEmailId: threadId, // Add the source thread ID
                    dateProposed: proposedDate
                });

            } catch (loopError) {
                logToRunLog_(`[${functionName}] ERROR processing parsed task item ${index} for thread ${threadId}: ${loopError.message}. Item: ${JSON.stringify(taskItem)}`);
            }
        }); // End processing task items for one email
    } // End iterating through thread IDs in response

    // Log missing IDs
    const missingIds = expectedThreadIds.filter(id => !receivedIds.has(id));
    if (missingIds.length > 0) {
        logToRunLog_(`[${functionName}] Warning: AI task response did not include results for ${missingIds.length} expected thread IDs: [${missingIds.slice(0, 5).join(', ')}${missingIds.length > 5 ? '...' : ''}]`);
        // Note: This contributes to the error count implicitly, as tasks won't be generated.
    }

    logToRunLog_(`[${functionName}] Finished parsing batch tasks. Total valid tasks extracted: ${allTasks.length}. Issues found for ${missingIds.length} expected IDs.`);
    return allTasks; // Return the flat array of all validated tasks
}





/**
 * Basic check if a string looks like YYYY-MM-DD. (Unchanged)
 * @private
 */
function isValidDate_(dateString) {
    if (!dateString) return false;
    return /^\d{4}-\d{2}-\d{2}$/.test(dateString);
}


// ==========================================================================
// Helper Functions: Sheet Writing & Gmail Actions (Unchanged)
// ==========================================================================

/**
 * Appends relevance scores from Pass 1 to the specified log sheet. (Unchanged)
 * @private
 */
function writeRelevanceScoresToLog_(relevanceResults, sheetName) {
    // ... (Keep the existing implementation of writeRelevanceScoresToLog_) ...
    const functionName = 'writeRelevanceScoresToLog_';
    if (!relevanceResults || relevanceResults.length === 0) { return; }
    logToRunLog_(`[${functionName}] Writing ${relevanceResults.length} relevance scores/errors to sheet '${sheetName}'...`);
    try {
        const ss = SpreadsheetApp.getActiveSpreadsheet();
        const sheet = ss.getSheetByName(sheetName);
        if (!sheet) { throw new Error(`Sheet "${sheetName}" not found.`); }

        const headers = ['Timestamp', 'Score', 'Justification', 'Subject', 'From', 'Date', 'Thread ID', 'Message ID', 'Pass1 Status', 'Error'];
        let startRow = sheet.getLastRow() + 1;
        if (startRow <= 1) {
            sheet.appendRow(headers);
            sheet.getRange(1, 1, 1, headers.length).setFontWeight("bold");
            SpreadsheetApp.flush(); startRow = 2;
        } // Optional header check can be added here

        const rows = relevanceResults.map(r => {
            const status = r.pass1Success ? 'Success' : 'Error';
            const score = r.pass1Success ? r.score : 'N/A';
            const just = r.pass1Success ? r.justification : 'N/A';
            const errorMsg = r.pass1Success ? '' : r.error || 'Unknown';
            const date = r.date ? Utilities.formatDate(r.date, Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss") : 'N/A';
            return [new Date(), score, just, r.subject || 'N/A', r.from || 'N/A', date, r.threadId || 'N/A', r.messageId || 'N/A', status, errorMsg];
        });

        if (rows.length > 0) {
            sheet.getRange(startRow, 1, rows.length, headers.length).setValues(rows);
            logToRunLog_(`[${functionName}] Successfully wrote ${rows.length} relevance rows.`);
        }
    } catch (e) {
        logToRunLog_(`[${functionName}] ERROR writing relevance scores: ${e.message}`);
        safeAlert_(`Error writing relevance scores to sheet '${sheetName}': ${e.message}`);
    }
}

/**
 * Appends proposed tasks to the specified proposal sheet. (Unchanged)
 * @private
 */
function writeTasksToProposalSheet_(tasks, sheetName) {
    // ... (Keep the existing implementation of writeTasksToProposalSheet_) ...
    const functionName = 'writeTasksToProposalSheet_';
    if (!tasks || tasks.length === 0) { return; }
    logToRunLog_(`[${functionName}] Preparing to write ${tasks.length} proposed tasks to sheet '${sheetName}'...`);
    let sheet;
    try {
        const ss = SpreadsheetApp.getActiveSpreadsheet();
        sheet = ss.getSheetByName(sheetName);
        if (!sheet) { throw new Error(`Sheet "${sheetName}" not found.`); }

        const headers = ['Task Name', 'Target Date', 'Approve', 'Status', 'Source Email ID', 'Date Proposed'];
        let startRow = sheet.getLastRow() + 1;
        if (startRow <= 1) {
            sheet.appendRow(headers);
            sheet.getRange("A1:F1").setFontWeight("bold");
            SpreadsheetApp.flush(); startRow = 2;
        } // Optional header check

        const rows = [];
        tasks.forEach((t, index) => {
            try {
                if (!t || !t.taskName || !t.sourceEmailId || !(t.dateProposed instanceof Date)) throw new Error(`Invalid task data at index ${index}`);
                const url = `https://mail.google.com/mail/#all/${t.sourceEmailId}`;
                const link = `=HYPERLINK("${url}", "${t.sourceEmailId}")`;
                rows.push([t.taskName, t.targetDate || "", "", "Pending", link, Utilities.formatDate(t.dateProposed, Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss")]);
            } catch (mapErr) { logToRunLog_(`[${functionName}] ERROR mapping task index ${index}: ${mapErr.message}. Data: ${JSON.stringify(t)}`); }
        });

        if (rows.length > 0) {
            const numRows = rows.length;
            const numCols = headers.length;
            const targetRange = sheet.getRange(startRow, 1, numRows, numCols);
            targetRange.setValues(rows);
            targetRange.offset(0, 2, numRows, 1).insertCheckboxes(); // Add checkboxes to 'Approve' column
            logToRunLog_(`[${functionName}] Successfully wrote ${rows.length} tasks.`);
        } else { logToRunLog_(`[${functionName}] No valid task rows to write after mapping.`); }

    } catch (e) {
        const sheetNameToLog = sheet ? sheet.getName() : sheetName;
        logToRunLog_(`[${functionName}] ERROR writing tasks to sheet '${sheetNameToLog}': ${e.message}\nStack: ${e.stack || 'N/A'}`);
        safeAlert_(`Error writing tasks to sheet '${sheetNameToLog}': ${e.message}.`);
    }
}


/**
 * Marks a set of Gmail threads as read. (Unchanged)
 * @private
 * @return {number} The number of threads successfully marked as read.
 */
function markThreadsAsRead_(threadIdsToMark) {
    // ... (Keep the existing implementation of markThreadsAsRead_) ...
    const functionName = 'markThreadsAsRead_';
    let markedReadSuccessCount = 0;
    let successCount = 0, failCount = 0;
    if (!threadIdsToMark || threadIdsToMark.size === 0) { return 0; } // Return 0 if none to mark

    threadIdsToMark.forEach(threadId => {
        try {
            const thread = GmailApp.getThreadById(threadId);
            if (thread) {
                thread.markRead();
                successCount++;
            }
            else {
                logToRunLog_(`[${functionName}] Warning: Could not find thread ${threadId} to mark read.`);
                failCount++;
            }
        } catch (markReadError) {
            failCount++;
            logToRunLog_(`[${functionName}] WARNING: Failed to mark thread ${threadId} read. Error: ${markReadError.message}`);
        }
        // Utilities.sleep(50); // Optional delay
    });
    logToRunLog_(`[${functionName}] Finished marking threads: ${successCount} success, ${failCount} failures.`);
    return successCount; // Return the count
}

/**
 * Analyzes summaries - Less relevant now, kept for potential future use.
 * @param {Array<object>} summaries Array of summary objects from Pass 1 results.
 * @private
 */
function analyzeAndSuggestFilters_(summaries) {
    // ... (Keep the existing implementation of analyzeAndSuggestFilters_)
    const functionName = 'analyzeAndSuggestFilters_';
    // Example: Filter based on score <= 2
    const lowRelevanceSummaries = summaries.filter(s => s.pass1Success && s.score <= 2); // Filter successful Pass 1 results

    if (lowRelevanceSummaries.length === 0) {
        // logToRunLog_(`[${functionName}] No low-relevance emails found for filter analysis.`);
        return;
    }

    logToRunLog_(`[${functionName}] Analyzing ${lowRelevanceSummaries.length} low-relevance emails (Score <= 2) for filter suggestions...`);

    const senderCounts = {};
    lowRelevanceSummaries.forEach(s => {
        const from = s.from; // Assumes 'from' is stored in the result object
        if (!from) return; // Skip if 'from' is missing

        const emailMatch = from.match(/<([^>]+)>/); // Extract email from "Name <email@example.com>"
        const senderEmail = emailMatch ? emailMatch[1].toLowerCase() : from.toLowerCase(); // Use email address, normalize case
        senderCounts[senderEmail] = (senderCounts[senderEmail] || 0) + 1;
    });

    // Filter out senders with only 1 occurrence and sort
    const sortedSenders = Object.entries(senderCounts)
        .filter(([, count]) => count > 1) // Only suggest if sender appeared more than once
        .sort(([, countA], [, countB]) => countB - countA);

    if (sortedSenders.length > 0) {
        logToRunLog_(`[${functionName}] --- Filter Suggestions (Based on Low Relevance Score Senders, Count > 1) ---`);
        sortedSenders.slice(0, 5).forEach(([sender, count]) => { // Limit suggestions
            logToRunLog_(`[${functionName}] Consider filtering sender: ${sender} (Low Relevance Count: ${count})`);
        });
        logToRunLog_(`[${functionName}] --- End Filter Suggestions ---`);
    } else {
        logToRunLog_(`[${functionName}] No clear repeating sender patterns found in low-relevance emails.`);
    }
}