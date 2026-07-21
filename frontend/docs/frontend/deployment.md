# Frontend Deployment & Operational Playbook

This document describes the environment variables, build configuration, development behaviors, and release procedures for the TalentScout Enterprise client.

---

## 1. Environment Variables

The frontend application utilizes Vite-based environment variables prefixing. Ensure these are defined in the deployment environment:

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `VITE_API_URL` | `http://localhost:8000` | The backend API server gateway endpoint URL. |
| `VITE_DEV_PASSWORD` | `scoutdev123` | The matching developer console verification password. |

---

## 2. Compilation and Build Process

The project compiles to static html, css, and js bundles using the Vite build manager:

* **Development Server**:
  ```bash
  npm run dev
  ```
* **Production Compilation**:
  ```bash
  npm run build
  ```
  The production artifacts are bundled under the `/dist` directory. This static bundle can be served from static CDNs, Nginx servers, or bucket storage (AWS S3, GCP Cloud Storage, etc.).

---

## 3. Required Backend Specifications

* **Backend Version Compatibility**: `V1.2.7` or higher.
* The adapter logic in `evaluationMapper.js` actively validates incoming response envelopes against this target version.

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
1. **Lint Check**: Validate formatting rules.
2. **Unit Test Pass**: Confirm all Vitest suites pass (`npm run test:run` or `npx vitest run`).
3. **Vite Compile Check**: Execute the production bundler to confirm compilation warnings are zero.
4. **Environment Check**: Ensure correct API and database routing environments are declared.
