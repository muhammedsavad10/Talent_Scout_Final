# API Request & Adapter Layer

This document details the API request wrapper, services, and the mapper adapter.

## API Client Config (`src/services/apiClient.js`)

TalentScout uses a pre-configured Axios network client pointing to the base backend URL endpoint.
- Context-based dev logs print request and response details during development environments.
- Normalizes content headers automatically for JSON payloads.

---

## Request Wrapper (`src/services/request.js`)

All network calls are wrapped inside `request.js` to ensure uniform error formatting and automatic timeouts (15s limits).

```javascript
import { request } from './request';

// Example:
const data = await request({
  url: `/status/${id}`,
  method: 'GET'
});
```

Normalizes errors into standard structures:
- `statusCode`: HTTP status code.
- `message`: User-friendly explanation.
- `raw`: Original underlying error.

---

## Service Classes

Network transactions are grouped into task-specific services under `src/services/`:

1. **`evaluationService`**: Retrieves health status, single candidate evaluation profiles, and password verification for developer access mode.
2. **`batchService`**: Triggers batch evaluation requests and polls for batch queue completion.
3. **`candidateService`**: Requests LLM-generated communication drafts from candidate profiles.
4. **`chatService`**: Sends chat inputs and dialogue histories to the AI assistant swarm.

---

## Response Adapter (`src/services/evaluationMapper.js`)

All incoming candidate evaluations must be processed by `mapEvaluationResponse(...)` before consumption by React. This guarantees:
- **1-to-1 Mapping Purity**: Maps nested backend attributes (e.g. `res.decision_engine.evidence_states.MATCHED`) to flat, normalized UI models (`mapped.evidenceStates.matched`).
- **Defensive Fallbacks**: Supplies safe defaults (empty arrays, fallback scoring scales, policy flags) to prevent UI crashes if the frozen backend response omits optional attributes.
- **Console Audits**: Prints structured evaluation summaries in development console.
