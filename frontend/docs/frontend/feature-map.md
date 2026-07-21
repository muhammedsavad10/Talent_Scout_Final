# Feature Module Mapping

This document lists the feature modules, components, and responsibilities.

## Feature Modules Table

| Feature Module | Key Components | State Scope | Dependencies | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`batch`** | `UploadWizard`<br>`BatchProgress`<br>`BatchCompleteCard` | Ingestion, active batch files, upload indicators | `batchService` | Manages pasting Job Descriptions, uploading multiple candidate resume PDFs, showing pipeline queues, and triggering workspace transitions. |
| **`comparison`** | `ComparisonFeature`<br>`ComparisonTable`<br>`CandidateCard` | Filter options, sort keys, multi-candidate modal selections | None | Displays candidates matrix, controls columns sorting, filters recommendation tiers, and displays up to 4 candidates side-by-side. |
| **`evaluation`** | `EvaluationWizard`<br>`SuitabilityStep`<br>`EvidenceStep`<br>`LearningStep`<br>`CommunicationStep`<br>`DecisionStep` | Dimension scores, custom recruiter notes, email template bodies | `candidateService`, `evaluationService` | Steps 2-6 evaluation router. Contains skills mapping, difficulty checklists, email generator, and recruiter overrides lock. |
| **`assistant`** | `AssistantFeature`<br>`ChatPanel`<br>`MessageBubble`<br>`CitationCard` | Chat thread history, streaming assistant loading indicators | `chatService` | Multi-agent chatbot sidebar. Provides RAG query interfaces and formats factual citation links. |
| **`developer`** | `DeveloperConsole` | Local drawer toggle, password buffers | `evaluationService` | Gated console drawer. Renders node transition timings, execution loops, latency benchmarks, and raw JSON logs. |
