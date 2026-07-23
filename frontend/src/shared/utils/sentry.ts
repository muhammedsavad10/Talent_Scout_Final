import { logger } from './logger';

export interface SentryConfig {
  dsn: string;
  environment: string;
  tracesSampleRate: number;
}

export const sentry = {
  init: (config: SentryConfig): void => {
    logger.info(`Sentry tracing initialized. Environment: ${config.environment}`);
  },
  captureException: (error: Error, extraInfo?: Record<string, any>): void => {
    logger.error(`[Sentry Alert] Captured exception: ${error.message}`, {
      stack: error.stack,
      ...extraInfo,
    });
  },
  captureMessage: (message: string, level: 'info' | 'warning' | 'error' = 'info'): void => {
    logger.info(`[Sentry Message] [${level.toUpperCase()}] ${message}`);
  },
};
export default sentry;
