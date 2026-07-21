/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useReducer, useEffect } from 'react';
import { mapEvaluationResponse } from '../../../services/evaluationMapper';

const EvaluationContext = createContext(null);

const initialState = {
  // Ingestion & Workflow State
  jdText: '',
  jdSkills: '',
  files: [],
  activeStep: 1,
  isLoading: false,
  error: null,

  // Batch State
  activeBatchId: null,
  batchStatus: null,
  batchResult: null,
  selectedCandidates: [],
  showSideBySide: false,
  filterTier: 'All',
  sortConfig: { key: 'rank', direction: 'asc' },

  // Active Candidate Result State
  evaluationId: null,
  result: null,

  // Screening Decision & Comm State
  emailTemplateType: 'interview_invite',
  emailDraft: null,
  isGeneratingEmail: false,
  notesEditable: false,
  editedNotes: '',
  overrideDecision: '',
  isSubmittingScreening: false,
  screeningSuccess: false,

  // Chat Assistant State
  chatMessages: [],
  isChatLoading: false
};

function dashboardReducer(state, action) {
  switch (action.type) {
    case 'INGEST/SET_JD_TEXT':
      return { ...state, jdText: action.payload };
    case 'INGEST/SET_JD_SKILLS':
      return { ...state, jdSkills: action.payload };
    case 'INGEST/SET_FILES':
      return { ...state, files: action.payload };
    case 'INGEST/ADD_FILES':
      return { ...state, files: [...state.files, ...action.payload] };
    case 'INGEST/REMOVE_FILE':
      return { ...state, files: state.files.filter((_, idx) => idx !== action.payload) };
    case 'INGEST/SET_STEP':
      return { ...state, activeStep: action.payload };
    case 'INGEST/START_LOADING':
      return { ...state, isLoading: true, error: null };
    case 'INGEST/STOP_LOADING':
      return { ...state, isLoading: false };
    case 'INGEST/SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    case 'INGEST/CLEAR_ERROR':
      return { ...state, error: null };

    // Batch Actions
    case 'BATCH/SUBMIT_START':
      return { ...state, isLoading: true, error: null, files: [] };
    case 'BATCH/SUBMIT_SUCCESS':
      return {
        ...state,
        activeBatchId: action.payload.batch_id,
        batchStatus: action.payload,
        isLoading: false
      };
    case 'BATCH/POLL_TICK':
      return { ...state, batchStatus: action.payload };
    case 'BATCH/POLL_SUCCESS':
      return {
        ...state,
        batchResult: action.payload,
        batchStatus: { ...state.batchStatus, status: 'COMPLETED', results: action.payload }
      };
    case 'BATCH/SELECT_CANDIDATE': {
      const isSelected = state.selectedCandidates.includes(action.payload);
      return {
        ...state,
        selectedCandidates: isSelected
          ? state.selectedCandidates.filter(id => id !== action.payload)
          : state.selectedCandidates.length < 4
            ? [...state.selectedCandidates, action.payload]
            : state.selectedCandidates
      };
    }
    case 'BATCH/CLEAR_SELECTION':
      return { ...state, selectedCandidates: [] };
    case 'BATCH/TOGGLE_SIDE_BY_SIDE':
      return { ...state, showSideBySide: action.payload };
    case 'BATCH/SET_FILTER_TIER':
      return { ...state, filterTier: action.payload };
    case 'BATCH/SET_SORT_CONFIG':
      return { ...state, sortConfig: action.payload };

    // Single Result Actions
    case 'EVALUATION/LOAD_SUCCESS':
      return {
        ...state,
        result: action.payload.mapped,
        evaluationId: action.payload.evaluationId,
        editedNotes: action.payload.mapped.recommendation?.reasoning || '',
        overrideDecision: action.payload.mapped.recommendation?.tier || '',
        isLoading: false,
        activeStep: 2
      };
    case 'EVALUATION/BACK_TO_COMPARISON':
      return {
        ...state,
        result: null,
        evaluationId: null,
        activeStep: 1.5
      };

    // Screening Override & Comm Actions
    case 'DECISION/SET_EMAIL_TEMPLATE':
      return { ...state, emailTemplateType: action.payload };
    case 'DECISION/GENERATE_EMAIL_START':
      return { ...state, isGeneratingEmail: true };
    case 'DECISION/GENERATE_EMAIL_SUCCESS':
      return { ...state, emailDraft: action.payload, isGeneratingEmail: false };
    case 'DECISION/SET_NOTES_EDITABLE':
      return { ...state, notesEditable: action.payload };
    case 'DECISION/UPDATE_NOTES':
      return { ...state, editedNotes: action.payload };
    case 'DECISION/UPDATE_DECISION':
      return { ...state, overrideDecision: action.payload };
    case 'DECISION/SUBMIT_START':
      return { ...state, isSubmittingScreening: true };
    case 'DECISION/SUBMIT_SUCCESS':
      return {
        ...state,
        isSubmittingScreening: false,
        screeningSuccess: true
      };
    case 'DECISION/RESET_STATE':
      return {
        ...state,
        result: null,
        evaluationId: null,
        activeStep: 1,
        screeningSuccess: false,
        overrideDecision: '',
        editedNotes: '',
        emailDraft: null
      };

    // Chat Assistant Actions
    case 'CHAT/ADD_MESSAGE':
      return { ...state, chatMessages: [...state.chatMessages, action.payload] };
    case 'CHAT/START_LOADING':
      return { ...state, isChatLoading: true };
    case 'CHAT/STOP_LOADING':
      return { ...state, isChatLoading: false };
    case 'CHAT/CLEAR':
      return { ...state, chatMessages: [] };

    default:
      return state;
  }
}

export function EvaluationProvider({ children }) {
  const [state, dispatch] = useReducer(dashboardReducer, initialState);

  // Auto-load last evaluation result from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem('lastEvaluation');
      if (stored) {
        const parsed = JSON.parse(stored);
        const rawToMap = parsed.rawPayload || parsed;
        const mapped = mapEvaluationResponse(rawToMap);
        if (mapped) {
          dispatch({
            type: 'EVALUATION/LOAD_SUCCESS',
            payload: { mapped, evaluationId: mapped.evaluationId }
          });
        }
      }
    } catch (e) {
      console.warn("Failed to load last evaluation from localStorage:", e);
    }
  }, []);

  return (
    <EvaluationContext.Provider value={{ state, dispatch }}>
      {children}
    </EvaluationContext.Provider>
  );
}

export function useEvaluation() {
  const context = useContext(EvaluationContext);
  if (!context) {
    throw new Error('useEvaluation must be used within an EvaluationProvider');
  }
  return context;
}
