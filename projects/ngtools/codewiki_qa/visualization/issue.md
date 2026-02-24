### Instruction

Review the provided @task, write rootcause to @analysis section, add your @fix_plan and all relevant files under @files.

### Task

#### Directory A

##### verification_questions

 `*_verification_ansx.json`: Contains the verification questions for a given question ID.

```json
{
  "question_id": "3d8a1369",
  "instance_id": "Stremio__stremio-web",
  "original_question": "A user reports that sometimes, after leaving the app open for a long time, their session expires but the UI doesn't update to show the login screen. What is the mechanism for handling session state and API errors, and where would I look to find the logic that is supposed to redirect the user when their authentication fails?",
  "generated_answer": "Based on the investigation of the codebase, here's the mechanism for handling session state and API errors, and where to find the logic for redirection upon authentication failure:\n\n### Session State and API Error Handling:\n\nThe core of the session and API request management is centralized in `src/services/Core/middleware.js`. This file contains a middleware that intercepts actions, particularly those related to API calls (`CORE_API_REQUEST`).\n\n1.  **API Requests:** When an action of type `CORE_API_REQUEST` is dispatched, the middleware makes a request using a `fetch` wrapper.\n2.  **Authentication Token:** The user's authentication key (`authKey`) is retrieved from the state (`profile.authKey`) and added as a parameter to the API request.\n3.  **Error Handling:** The middleware checks the response from the API. If the response is an error, it dispatches a `CORE_API_ERROR` action.\n4.  **Authentication Failure:** Specifically, if the API response has `error.code === 1` and the `error.message` is `\"authKey not valid\"`, it indicates an expired or invalid session. In this case, it dispatches a `profile.logout` action to clear the user's session data from the application's state.\n\n### Redirect Logic:\n\nThe redirection logic is not directly tied to the API error itself but is a result of the application's state changing.\n\n1.  **Protected Routes:** The main application component, likely in `src/App/App.js`, uses a higher-order component or a similar mechanism (`withProtectedRoutes.js` is a strong candidate) to protect certain routes.\n2.  **State Change Trigger:** When the `profile.logout` action is dispatched from the middleware, the application's state is updated, clearing the user's profile and `authKey`.\n3.  **UI Update:** The protected route component listens for changes in the authentication state (e.g., the presence of `profile.authKey`). When `authKey` becomes `null`, the component will re-render.\n4.  **Redirection:** Upon re-rendering, because the user is no longer authenticated, the protected route logic will redirect the user to the login/intro screen. You can find this logic by examining how the router and protected components consume the `profile` state, likely within the `src/App/` or `src/router/` directories. The component that wraps the main routes in `src/App/App.js` is the place to start looking for the implementation of this redirection.\n\nIn summary, to debug the issue, you should investigate the following files:\n*   `src/services/Core/middleware.js`: To see how API errors and specifically authentication errors are handled.\n*   `src/App/withProtectedRoutes.js` and `src/App/App.js`: To understand how the application reacts to changes in the authentication state (`profile.authKey`) and triggers a redirect.\n\nThe problem likely lies in a scenario where the API error is not correctly caught by the middleware, or the state change is not correctly triggering a re-render and redirect in the UI components.",
  "verification_questions": [
    "In `src/services/Core/middleware.js`, is a `profile.logout` action dispatched when an API response contains an error with `code === 1` and a message of `\"authKey not valid\"`?",
    "Does the middleware defined in `src/services/Core/middleware.js` intercept and handle actions with the type `CORE_API_REQUEST`?",
    "Does the application's routing logic, for example in `src/App/App.js`, trigger a redirect to a login screen when the `authKey` is absent from the `profile` state?"
  ]
}
```

##### verification_results

- `*_verify_result_ansx.json`: Contains the verification results (decision and rationale) for a given question ID.

```json
{
  "question_id": "0d1951bc",
  "instance_id": "Stremio__stremio-web",
  "decision": "Fail",
  "verification_results": [
    {
      "verification_question": "Does the provided answer specify that the user's language selection is persisted using the browser's `localStorage`?",
      "verification_answer": "Yes",
      "decision": "Pass",
      "rationale": "The user's language selection is persisted using the browser's `localStorage`. The `src/common/useSettings.ts` file contains the logic for managing user settings, including the interface language. Specifically, the `useSettings` hook initializes its state from `localStorage` and uses a `useEffect` hook to save any changes to the settings back to `localStorage` with the key `SETTINGS`. The `interfaceLanguage` is one of the properties within the settings object that gets persisted."
    },
    {
      "verification_question": "Does the answer state that a React Context is used to make the current language available throughout the application's component tree?",
      "verification_answer": "Yes",
      "decision": "Pass",
      "rationale": "The application uses a `TranslateContext` to provide translation capabilities throughout the component tree. The `useTranslate` hook consumes this context to provide the `t` function, which is used for translating strings. This is evident in `src/common/useTranslate.js`, where `useContext(TranslateContext)` is called. The `TranslateProvider` component, which is not explicitly in the provided file structure but is a common pattern, would be responsible for providing the context value."
    },
    {
      "verification_question": "Does the answer explain that translated strings are loaded from language-specific JSON files?",
      "verification_answer": "No",
      "decision": "Fail",
      "rationale": "The codebase does not use language-specific JSON files for translations. Instead, it uses a `withI18n` higher-order component and a `useTranslate` hook, which appear to manage translations internally. The file `src/common/interfaceLanguages.json` lists the available languages, but the actual translated strings are not stored in individual JSON files. The translation logic seems to be handled by a system that fetches translations from a remote service or has them bundled within the application's JavaScript, rather than loading them from separate JSON files for each language."
    }
  ]
}
```

#### Directory B

 `*_verification_ansx.json`: Contains a verification question for a given question ID.

```json
{
  "question_id": "0d1951bc",
  "instance_id": "Stremio__stremio-web",
  "original_question": "The settings page allows users to change the application's language. What is the complete flow for how a new language selection is persisted and then applied throughout the entire UI, including fetching translated strings for dynamic content?",
  "generated_answer": "The process of changing and applying a new language in the Stremio web application follows a clear, event-driven flow from the user interface to the core application state, which then triggers UI updates. Here is the complete breakdown of the process:\n\n1.  **User Selection in Settings:**\n*   The user navigates to the settings page, where the `General` component (`src/routes/Settings/General/General.tsx`) renders a `MultiselectMenu` component for language selection.\n*   The options and the selection handler for this menu are provided by the `useGeneralOptions` custom hook (`src/routes/Settings/General/useGeneralOptions.ts`).\n\n2.  **Dispatching the Change:**\n*   When the user selects a new language, the `onSelect` callback within the `useGeneralOptions` hook is executed.\n*   This callback dispatches an action to the application's core service: `core.transport.dispatch({ action: 'Ctx', args: { action: 'UpdateSettings', args: { ...profile.settings, interfaceLanguage: value } } });`. This action contains the newly selected language code.\n\n3.  **Persistence and State Update:**\n*   The `Core` service (`src/services/Core/`) handles the `UpdateSettings` action. It updates the application's central state, specifically the `profile.settings.interfaceLanguage` property, and persists this change.\n*   After successfully updating the settings, the `Core` service emits a `SettingsUpdated` event via its transport layer. This event carries the new settings object as its payload.\n\n4.  **Applying the New Language:**\n*   The main `App` component (`src/App/App.js`) contains a `useEffect` hook that listens for events from the `Core` service.\n*   An event handler `onCoreEvent` is set up to listen for the `SettingsUpdated` event. When this event is caught, the handler extracts the `interfaceLanguage` from the event's arguments.\n*   It then calls `i18n.changeLanguage(args.settings.interfaceLanguage)`. `i18n` is an instance of i18next (from `react-i18next`), which is the translation library used in the application.\n\n5.  **UI Re-rendering with New Translations:**\n*   The `i18n.changeLanguage()` call triggers `i18next` to load the translation file for the selected language.\n*   All components throughout the application that use the `useTranslation` hook (or other `react-i18next` HOCs/render props) are automatically subscribed to language changes. These components re-render with the appropriate translated strings.\n\n6.  **Fetching Translated Dynamic Content:**\n*   For dynamic content that requires translated strings (like metadata for movies or series), the application makes API requests.\n*   When fetching this data, the `Core` service includes the current `interfaceLanguage` from the user's profile settings as a parameter in the API request, ensuring that the server returns data in the selected language. Any component that displays this data will then be updated with the translated content.",
  "verification_question": "In the `App` component located at `src/App/App.js`, does a `useEffect` hook contain an event listener for the `SettingsUpdated` event which, when triggered, calls `i18n.changeLanguage` with the `interfaceLanguage` value from the event's payload?"
}
```

- `*_verify_result_ansx.json`: Contains the verification results (decision and rationale) for a given question ID.

```json
{
  "question_id": "0d1951bc",
  "instance_id": "Stremio__stremio-web",
  "verification_answer": "Yes",
  "decision": "Pass",
  "rationale": "The `useTranslate` hook in `src/common/useTranslate.js` contains a `useEffect` that is triggered when `profile.settings.interfaceLanguage` changes. Inside this effect, the `i18next.changeLanguage` function is called with the new language code. This directly confirms the statement in the generated answer."
}
```


#### task description

Create a script to generate html page to analyze and visualize verification results from two directories A and B containing JSON files.

Each directory contains verification question(s) for a list of questions, indicated by question_id. The question_id in two directories are the same.

I want to create a visualization for the questions, see example

```
Q: how does this code work?
A: it works by implementing X and Y


(left column) single verification question: does this code implement X and Y
(right column) list of multiple verification question: does this code implement X? does this code implement Y?
```
directoryA: /usr/local/google/home/guyu/Desktop/gcli/agent-prototypes/experiments/qabench/2025-10-08/4-goofy-goodall/multi/Stremio__stremio-web

directoryB: /usr/local/google/home/guyu/Desktop/gcli/agent-prototypes/experiments/qabench/2025-10-08/4-goofy-goodall/Stremio__stremio-web

### analysis

  The user wants to create a Python script that generates an HTML page to visualize and compare
  verification results from two different directories, referred to as Directory A and Directory B.

  Directory A (Multi-Question Verification):
   - Contains JSON files with multiple verification questions (verification_questions) for a single
     generated answer.
   - The corresponding results file (*_verify_result_ansx.json) contains a list of decisions and
     rationales, one for each question.

  Directory B (Single-Question Verification):
   - Contains JSON files with a single, composite verification question (verification_question).
   - The results file contains a single decision and rationale for that question.

  Core Requirements:
   1. Input: The script should accept the paths to Directory A and Directory B as input.
   2. Data Aggregation: It needs to find matching question_id pairs from both directories, parsing both
      the question files (*_verification_ansx.json) and the result files (*_verify_result_ansx.json).
   3. HTML Generation: The script must generate a single HTML file.
   4. Visualization: The HTML page should display a side-by-side comparison for each question, with the
      single verification from Directory B on the left and the multiple verifications from Directory A
      on the right. The overall pass/fail status should be clearly visible, perhaps using color-coding.

  The goal is to create a visual tool to analyze the differences in verification outcomes when using
  a single, comprehensive verification question versus multiple, granular questions.

### fix_plan

   1. Create a Python Script (`visualize_results.py`): This script will orchestrate the entire process.
   2. Argument Parsing: Use Python's argparse library to accept the paths for Directory A, Directory B,
      and an optional output HTML file path.
   3. File Discovery and Parsing:
       - Implement a function to scan a directory and group the JSON files by question_id.
       - For each question_id, parse the *_verification_ansx.json to get the questions and the
         *_verify_result_ansx.json to get the results.
       - Handle the different structures of the JSON files from Directory A (lists) and Directory B
         (single items).
   4. Data Merging:
       - Create a consolidated data structure (e.g., a dictionary keyed by question_id) that merges the
         parsed data from both directories for each common question.
   5. HTML Generation:
       - Define a function that takes the merged data and generates an HTML string.
       - The HTML will include a header and embedded CSS for styling.
       - Iterate through each question_id in the merged data.
       - For each item, create a main container that displays the original question and the generated
         answer.
       - Inside this container, create a two-column layout (e.g., using CSS Flexbox or Grid).
       - Left Column (Directory B): Display the single verification question and its result. The
         container's style will change based on the "Pass" or "Fail" decision.
       - Right Column (Directory A): Iterate through the list of verification questions and results,
         displaying each one in its own styled container.
   6. Output: Write the generated HTML string to the specified output file.
   7. Add a `main` block: To tie everything together, the main execution block will parse arguments,
      call the data processing functions, generate the HTML, and save the file.
  files
   - codewiki_qa/visualization/visualize_results.py

### files
