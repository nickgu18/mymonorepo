# gplanner: TDD Implementation Checklist

This document provides a step-by-step checklist for implementing the `gplanner` application, following a Test-Driven Development (TDD) methodology.

---

### Phase 1: Backend Foundation

-   [ ] **Testing (Backend Foundation):**
    -   [ ] Set up a testing framework (e.g., Jest) for the backend.
    -   [ ] Write unit tests for the `geminiCLIRunner.ts` module, covering command construction, environment variable handling, and subprocess mocking.
    -   [ ] Write integration tests for the initial API endpoints to define their expected behavior (e.g., request validation, response structure).

-   [ ] **Implementation (Backend Foundation):**
    -   [ ] Initialize the Node.js project and install dependencies.
    -   [ ] Implement the `geminiCLIRunner.ts` module until the unit tests pass.
    -   [ ] Implement the API endpoint scaffolding in `src/api.ts` until the integration tests pass.
    -   [ ] Integrate a logging library.

---

### Phase 2: Frontend Scaffolding

-   [ ] **Testing (Frontend Scaffolding):**
    -   [ ] Set up a testing framework for React (e.g., Vitest, React Testing Library).
    -   [ ] Write component tests for the main UI components (`PromptInput`, `PlanEditor`, `InteractionPanel`) to verify they render correctly with placeholder content.
    -   [ ] Write tests for the API connection service to mock and verify API calls.

-   [ ] **Implementation (Frontend Scaffolding):**
    -   [ ] Create the React project and install dependencies.
    -   [ ] Build the UI components until the component tests pass.
    -   [ ] Implement the API connection service until its tests pass.
    -   [ ] Configure the frontend proxy.

---

### Phase 3: Core Functionality - Interactive Planning

-   [ ] **Testing (Core Functionality):**
    -   [ ] Write integration tests for the backend to verify the full lifecycle of a planning session (e.g., starting a session, streaming data, handling responses).
    -   [ ] Write frontend tests to verify that the application correctly handles WebSocket/streaming data and updates the UI accordingly.
    -   [ ] Write tests for the Markdown editor component to ensure it loads content and handles user input.

-   [ ] **Implementation (Core Functionality):**
    -   [ ] **Backend:** Implement the full logic for managing the Gemini CLI process and streaming data until the integration tests pass.
    -   [ ] **Frontend:** Implement the logic to connect to the backend, handle real-time updates, and integrate the Markdown editor until the frontend tests pass.

---

### Phase 4: Finalizing Features & E2E Testing

-   [ ] **Testing (Finalizing Features):**
    -   [ ] Write integration tests for the file-saving functionality on the backend.
    -   [ ] Set up an End-to-End (E2E) testing framework (e.g., Cypress or Playwright).
    -   [ ] Write E2E tests for the complete user workflows:
        -   [ ] Starting a planning session.
        -   [ ] Receiving and displaying a plan.
        -   [ ] Editing the plan.
        -   [ ] Saving the plan to a file.

-   [ ] **Implementation (Finalizing Features):**
    -   [ ] Implement the plan-saving feature until its integration tests pass.
    -   [ ] Refine the UI/UX, adding loading states and error handling.
    -   [ ] Integrate Electron or Tauri for desktop app packaging.
    -   [ ] Run all E2E tests and iterate on the implementation until they all pass.
