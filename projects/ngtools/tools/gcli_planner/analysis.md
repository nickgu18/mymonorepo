# gplanner: Analysis and Design Document

## 1. Overview

The goal of the "gplanner" project is to create a GUI-based interface for the Gemini CLI. This tool will provide users with an interactive way to leverage the planning capabilities of the Gemini model, as described in `tools/gcli_planner/design.md`. The application will allow users to input complex tasks, receive a detailed plan from the agent, and interactively edit that plan before execution or for reference.

## 2. Architecture Design

A decoupled frontend-backend architecture is proposed. This allows for a clean separation of concerns, making the application easier to develop, test, and maintain.

### 2.1. High-Level Architecture

The system will consist of two main components:

-   **Frontend:** A desktop application built with web technologies (React and Electron/Tauri) that provides the user interface.
-   **Backend:** A local server (Node.js with Express or Python with FastAPI) that acts as a bridge between the frontend and the Gemini CLI.

```
+-----------------+      +------------------+      +------------------+
|   Frontend      |      |   Backend        |      |   Gemini CLI     |
| (React +        |      | (Node.js/Python) |      | (Subprocess)     |
|  Electron/Tauri)|      |                  |      |                  |
+-------+---------+      +--------+---------+      +--------+---------+
        |                       |                       |
        |  HTTP/WebSocket       |                       |
        +---------------------->|                       |
        <----------------------+                       |
        |                       |                       |
        |                       |  Invoke as Subprocess |
        |                       +---------------------->|
        |                       <----------------------+
        |                       |                       |
```

### 2.2. Frontend

-   **Technology Stack:**
    -   **Framework:** React
    -   **UI Library:** A modern component library like Material-UI or Chakra UI for a consistent and professional look.
    -   **Desktop Bundler:** Electron or Tauri to package the web application as a desktop app. This is ideal for a tool that needs to interact with the local file system and shell commands.
    -   **State Management:** Redux Toolkit or Zustand for managing application state.

-   **Key Components:**
    -   **Main Layout:** A clean interface with a prompt input area, a plan display/editor, and a panel for agent interactions.
    -   **Prompt Input:** A text area where users can describe their task. It will implement the `Shift + Tab` shortcut to initiate planning mode.
    -   **Plan Editor:** A component that can render and allow editing of Markdown. A library like `react-markdown` combined with an editor like `react-simplemde-editor` could be used.
    -   **Interaction Panel:** A dedicated area for the agent to ask clarifying questions and for the user to respond.
    -   **Controls:** Buttons for saving the plan, and potentially for future features like executing the plan.

### 2.3. Backend

-   **Technology Stack:**
    -   **Framework:** Node.js with Express.js is a good choice due to its non-blocking I/O, which is well-suited for managing subprocesses like the Gemini CLI. Python with FastAPI is also a viable alternative.
    -   **Process Management:** The backend will use Node.js's `child_process` module to spawn and manage the Gemini CLI process.

-   **Core Modules:**
    -   **`GeminiCLIRunner`:** A module that encapsulates the logic from `agent-prototypes/agent_prototypes/utils/gemini_cli_runner.py`. It will be responsible for:
        -   Constructing the `npx` command to run the Gemini CLI.
        -   Managing API keys and other environment variables.
        -   Executing the command as a subprocess.
        -   Capturing and parsing the stdout/stderr streams to communicate with the frontend.
    -   **API Server:** An Express.js server that exposes RESTful endpoints for the frontend.
    -   **File System Service:** A module to handle reading files from the user's workspace (for context) and writing the plan to a Markdown file. Access will be restricted to the current working directory for security.

-   **API Endpoints:**
    -   `POST /api/plan/generate`: Starts a new planning session.
        -   **Request Body:** `{ "prompt": "user's task description" }`
        -   **Response:** A stream of updates or a session ID to poll for status.
    -   `GET /api/plan/:sessionId`: Retrieves the current state of a planning session.
    -   `POST /api/plan/:sessionId/respond`: Sends a user's response to a clarifying question from the agent.
    -   `PUT /api/plan/:sessionId`: Updates the plan with user edits from the frontend editor.
    -   `POST /api/plan/:sessionId/save`: Saves the current plan to a Markdown file.

### 2.4. Communication Protocol

-   **HTTP/REST:** For standard request/response interactions like starting a plan or saving it.
-   **WebSockets (Optional but Recommended):** For real-time, bidirectional communication between the frontend and backend. This would be ideal for streaming the agent's output (including clarifying questions) to the UI without the need for polling.

## 3. Implementation Plan

The implementation can be broken down into the following phases:

### 3.1. Phase 1: Backend Foundation

1.  **Project Setup:** Initialize a new Node.js project with Express.js.
2.  **Gemini CLI Runner:** Port the logic from `gemini_cli_runner.py` to a TypeScript/JavaScript module. This will be the most critical part of the backend.
3.  **API Scaffolding:** Create the basic API endpoints defined above, with placeholder logic.

### 3.2. Phase 2: Frontend Scaffolding

1.  **Project Setup:** Create a new React application using a tool like Create React App or Vite.
2.  **UI Layout:** Build the main UI components (input, display, etc.) with placeholder content.
3.  **API Connection:** Connect the frontend to the backend's API endpoints.

### 3.3. Phase 3: Core Functionality - Interactive Planning

1.  **Backend:** Implement the full logic for the `GeminiCLIRunner`, allowing it to start and manage a Gemini CLI process.
2.  **Frontend:**
    -   Implement the logic to send the user's prompt to the backend and display the generated plan.
    -   Integrate a Markdown editor for the plan display.
    -   Implement the interaction panel for clarifying questions.

### 3.4. Phase 4: Finalizing Features

1.  **Plan Saving:** Implement the file-saving functionality on both the backend and frontend.
2.  **UI/UX Polish:** Refine the user interface, add loading states, error handling, and improve the overall user experience.
3.  **Desktop App Packaging:** Integrate Electron or Tauri to package the application for desktop use.

### 3.5. Phase 5: Testing

1.  **Unit Tests:** Write unit tests for the `GeminiCLIRunner` and other backend logic.
2.  **Integration Tests:** Test the integration between the frontend and backend.
3.  **End-to-End (E2E) Tests:** Use a framework like Cypress or Playwright to test the complete user workflow.

## 4. Key Considerations

-   **Security:** The application will be executing shell commands and accessing the file system. It's crucial to validate and sanitize all inputs and restrict file system access to the user's intended workspace.
-   **Cross-Platform Compatibility:** Using Electron/Tauri and Node.js will help ensure that the application can run on different operating systems (Windows, macOS, Linux).
-   **Configuration:** The application will need a way to configure settings, such as the path to the Gemini CLI or API key management.
