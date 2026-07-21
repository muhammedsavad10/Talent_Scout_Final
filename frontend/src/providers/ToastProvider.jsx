/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useCallback } from 'react';

const ToastContext = createContext(undefined);

let toastId = 0;

/**
 * Toast types: 'success' | 'error' | 'warning' | 'info'
 */
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback(({ type = 'info', title, message, duration = 5000 }) => {
    const id = ++toastId;
    const toast = { id, type, title, message };
    setToasts(prev => [...prev, toast]);

    if (duration > 0) {
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
      }, duration);
    }

    return id;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  // Convenience methods
  const success = useCallback((title, message) => addToast({ type: 'success', title, message }), [addToast]);
  const error = useCallback((title, message) => addToast({ type: 'error', title, message }), [addToast]);
  const warning = useCallback((title, message) => addToast({ type: 'warning', title, message }), [addToast]);
  const info = useCallback((title, message) => addToast({ type: 'info', title, message }), [addToast]);

  const value = { toasts, addToast, removeToast, success, error, warning, info };

  const typeStyles = {
    success: { bg: 'bg-emerald-50 dark:bg-emerald-950/50', border: 'border-emerald-200 dark:border-emerald-800', text: 'text-emerald-800 dark:text-emerald-200', icon: '✓' },
    error:   { bg: 'bg-red-50 dark:bg-red-950/50', border: 'border-red-200 dark:border-red-800', text: 'text-red-800 dark:text-red-200', icon: '✕' },
    warning: { bg: 'bg-amber-50 dark:bg-amber-950/50', border: 'border-amber-200 dark:border-amber-800', text: 'text-amber-800 dark:text-amber-200', icon: '!' },
    info:    { bg: 'bg-blue-50 dark:bg-blue-950/50', border: 'border-blue-200 dark:border-blue-800', text: 'text-blue-800 dark:text-blue-200', icon: 'i' },
  };

  return (
    <ToastContext.Provider value={value}>
      {children}

      {/* Toast Container */}
      {toasts.length > 0 && (
        <div className="fixed bottom-4 right-4 z-[9999] flex flex-col gap-2 max-w-sm w-full pointer-events-none">
          {toasts.map((toast) => {
            const style = typeStyles[toast.type] || typeStyles.info;
            return (
              <div
                key={toast.id}
                className={`${style.bg} ${style.border} border rounded-xl p-4 shadow-elevated animate-slide-up pointer-events-auto`}
                role="alert"
                aria-live="polite"
              >
                <div className="flex items-start gap-3">
                  <span className={`${style.text} w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 border ${style.border}`}>
                    {style.icon}
                  </span>
                  <div className="flex-1 min-w-0">
                    {toast.title && (
                      <p className={`${style.text} font-semibold text-sm`}>{toast.title}</p>
                    )}
                    {toast.message && (
                      <p className={`${style.text} text-xs mt-0.5 opacity-80`}>{toast.message}</p>
                    )}
                  </div>
                  <button
                    onClick={() => removeToast(toast.id)}
                    className={`${style.text} opacity-50 hover:opacity-100 text-lg leading-none transition-opacity flex-shrink-0`}
                    aria-label="Dismiss notification"
                  >
                    ×
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

export default ToastProvider;
