export const logger = {
  info: (message: string, ...args: any[]): void => {
    console.log(`%c[INFO]%c ${message}`, 'color: #3b82f6; font-weight: bold;', '', ...args);
  },
  warn: (message: string, ...args: any[]): void => {
    console.warn(`%c[WARN]%c ${message}`, 'color: #f59e0b; font-weight: bold;', '', ...args);
  },
  error: (message: string, ...args: any[]): void => {
    console.error(`%c[ERROR]%c ${message}`, 'color: #ef4444; font-weight: bold;', '', ...args);
  },
};
export default logger;
