# Frontend Deployment & Operational Playbook

This document describes the environment variables, build configuration, development behaviors, and release procedures for the TalentScout Enterprise client.

---

## 1. Environment Variables & Production Constraints

The frontend application utilizes Vite-based environment variables prefixing. Ensure these are defined in the deployment environment:

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `VITE_API_URL` | `http://localhost:8000` | The backend API server gateway endpoint URL. |
| `VITE_DEV_PASSWORD` | `scoutdev123` | The matching developer console verification password. |

### Production Environment Requirements:
- **HTTPS Enforcement**: Production hosting must serve assets over HTTPS to secure session transfers.
- **CORS Configuration**: Backend API CORS policies must explicitly authorize the public domain origin of the frontend bundle.
- **API Target**: In production, `VITE_API_URL` must point to the production API domain gateway; it should never point to `localhost`.
- **Security Check**: Never commit `.env.local` or environment files containing actual production credentials to Git repository.

---

## 2. Compilation and Build Process

The project compiles to static html, css, and js bundles using the Vite build manager:

* **Install Dependencies**:
  ```bash
  npm install
  ```
* **Development Server**:
  ```bash
  npm run dev
  ```
* **Production Compilation**:
  ```bash
  npm run build
  ```
  The production build artifacts are written to the `/dist` directory.
* **Verify Production Bundle Locally**:
  ```bash
  npm run preview
  ```
  Run this command to serve the production build locally and verify that everything compiles and behaves correctly under production configuration before triggering external deployments.

---

## 3. Required Backend Specifications & Version Matrix

Compatibility mapping is locked as follows:

| System Layer | Current Release Version | Compatibility Notes |
| :--- | :--- | :--- |
| **Frontend Client** | `v2.0.0` | Modularized Feature-Architecture release. |
| **Compatible Backend** | `>= v1.2.7` | Requires LangGraph evidence states and metrics payloads. |
| **API Protocol Contract** | `v1.0.0` | Standardized JSON contract verified via `evaluationMapper.js`. |

---

## 4. Operational Logging Behaviors

* In **Development Mode** (`import.meta.env.DEV` is `true`), API request and response trace groups are printed directly to the recruiter's web inspector console.
* In **Production Mode**, trace logs are suppressed. Only critical network errors are logged to the standard console.

---

## 5. Browser Compatibility

The application utilizes native ES modules and CSS custom design variables. The client supports all modern evergreen web browsers:
- Google Chrome (latest 3 versions)
- Apple Safari (latest 2 versions)
- Microsoft Edge (latest 3 versions)
- Mozilla Firefox (latest 2 versions)

---

## 6. Pre-Release Smoke Checklist

Before committing code modifications to the release branch, execute the following validation tasks:

### Build & Quality Verification
1. **Lint Check**: Validate formatting rules.
2. **Unit Test Pass**: Confirm all Vitest suites pass (`npm run test:run` or `npx vitest run`).
3. **Vite Compile Check**: Execute the production bundler to confirm compilation warnings are zero.

### Runtime Smoke Verification
4. **Recruiter Workflows**: Log in and verify that candidate ingestion, dropzones, and wizard pipelines load successfully.
5. **Candidate Strategy**: Run through the evaluation steps (2-6) and check that score meters populate dynamically.
6. **Comparison Matrix**: Navigate to Step 1.5 grid, trigger a side-by-side modal, and confirm profile compare grids look clean.
7. **Swarm QA assistant**: Verify sending chat messages returns correct answers and citations from the RAG swarm.
8. **Developer Console**: Unlock console with password and confirm processing latency charts and Graph node steps load without crash.
9. **Error Inspection**: Open browser developer console and confirm there are no unexpected warning/error logs.

---

## 7. Rollback Procedures

If a deployment fails, exhibits runtime exceptions, or breaks service connectivity in production:
1. **Restore Previous Bundle**: Roll back the web hosting gateway to point to the last stable frontend bundle (e.g. from container registry or bucket deployment version control).
2. **Verify Backend Contract**: Confirm that the backend version is compatible with the fallback frontend version.
3. **Reset Environment Vars**: Revert any database connections or host URLs modified in environment variables if necessary.
4. **Validate Rollback**: Trigger a quick runtime smoke test to confirm active recruiters can access the dashboard.
