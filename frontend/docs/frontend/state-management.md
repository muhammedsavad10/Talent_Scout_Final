# Frontend State Management

This document details the state management model of the TalentScout Enterprise client.

## Context and Reducer Model

The core state management is driven by a React Context-based `useReducer` pattern defined in `EvaluationContext.jsx`. This centralized provider maintains ingestion parameters, batch evaluation logs, comparison selection caches, currently loaded single-candidate evaluations, and chat logs.

```javascript
const [state, dispatch] = useReducer(dashboardReducer, initialState);
```

---

## Action Prefixing and Domain Grouping

To prevent action-collision and structure developer trace logging, all actions are grouped by their domain prefixes:

* **`INGEST/`** (Ingestion and Workspace Workflow)
  - `INGEST/SET_JD_TEXT`: Sets Job Description text buffer.
  - `INGEST/SET_JD_SKILLS`: Custom overrides list.
  - `INGEST/SET_FILES`: Overwrites active drop list.
  - `INGEST/ADD_FILES`: Appends new PDF documents.
  - `INGEST/REMOVE_FILE`: Removes single resume item.
  - `INGEST/SET_STEP`: Navigates main workspace step routing.
  - `INGEST/START_LOADING` / `INGEST/STOP_LOADING` / `INGEST/SET_ERROR` / `INGEST/CLEAR_ERROR`

* **`BATCH/`** (Batch candidate queues and comparison matrices)
  - `BATCH/SUBMIT_START`: Triggers file upload array to backend pipeline.
  - `BATCH/SUBMIT_SUCCESS`: Receives batch ID.
  - `BATCH/POLL_TICK`: Updates completed progress count.
  - `BATCH/POLL_SUCCESS`: Caches candidates list.
  - `BATCH/SELECT_CANDIDATE`: Adds candidate to selection list.
  - `BATCH/CLEAR_SELECTION`: Purges selection cache.
  - `BATCH/TOGGLE_SIDE_BY_SIDE`: Triggers side-by-side comparison modal.
  - `BATCH/SET_FILTER_TIER`: Filters table candidates.
  - `BATCH/SET_SORT_CONFIG`: Sets table column sorting keys.

* **`EVALUATION/`** (Loaded single evaluation details)
  - `EVALUATION/LOAD_SUCCESS`: Maps backend response and sets editing buffers.
  - `EVALUATION/BACK_TO_COMPARISON`: Safely returns to table view.

* **`DECISION/`** (Recruiter screening logs and email communications)
  - `DECISION/SET_EMAIL_TEMPLATE`: Template type switcher.
  - `DECISION/GENERATE_EMAIL_START` / `DECISION/GENERATE_EMAIL_SUCCESS`
  - `DECISION/SET_NOTES_EDITABLE`: Toggles note editor locks.
  - `DECISION/UPDATE_NOTES` / `DECISION/UPDATE_DECISION`
  - `DECISION/SUBMIT_START` / `DECISION/SUBMIT_SUCCESS` / `DECISION/RESET_STATE`

* **`CHAT/`** (Recruiter AI swarm chatbot)
  - `CHAT/ADD_MESSAGE` / `CHAT/START_LOADING` / `CHAT/STOP_LOADING` / `CHAT/CLEAR`

---

## Local State Delegation Rules

Keep presentational, local-only states isolated inside components to prevent redundant global renders:
- Toggle states (e.g. `isDevDrawerOpen`, `selectedQuestionsTab`) should live in local `useState` hooks.
- Form inputs (e.g. password inputs, chat text inputs) must be managed locally within component states until submission.
