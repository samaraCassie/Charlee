/**
 * Retry utility with exponential backoff for failed API requests.
 *
 * Features:
 * - Automatic retry with configurable attempts
 * - Exponential backoff between retries
 * - Error type detection (network vs server errors)
 * - Offline detection and queueing
 */

export interface RetryOptions {
  maxAttempts?: number;
  initialDelay?: number; // milliseconds
  maxDelay?: number; // milliseconds
  backoffMultiplier?: number;
  retryableStatusCodes?: number[];
  onRetry?: (attempt: number, error: Error) => void;
}

const DEFAULT_OPTIONS: Required<RetryOptions> = {
  maxAttempts: 3,
  initialDelay: 1000,
  maxDelay: 10000,
  backoffMultiplier: 2,
  retryableStatusCodes: [408, 429, 500, 502, 503, 504],
  onRetry: () => {},
};

/**
 * Determines if an error is retryable.
 */
function isRetryableError(error: any, retryableStatusCodes: number[]): boolean {
  // Network errors (no response)
  if (!error.response) {
    return true;
  }

  // Server errors with specific status codes
  if (error.response?.status && retryableStatusCodes.includes(error.response.status)) {
    return true;
  }

  return false;
}

/**
 * Calculates delay for the next retry attempt using exponential backoff.
 */
function calculateDelay(
  attempt: number,
  initialDelay: number,
  maxDelay: number,
  backoffMultiplier: number
): number {
  const delay = initialDelay * Math.pow(backoffMultiplier, attempt - 1);
  return Math.min(delay, maxDelay);
}

/**
 * Waits for the specified number of milliseconds.
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Executes a function with retry logic and exponential backoff.
 *
 * @param fn - Async function to execute
 * @param options - Retry configuration options
 * @returns Promise with the function result
 *
 * @example
 * ```ts
 * const data = await retryWithBackoff(
 *   () => api.post('/endpoint', payload),
 *   {
 *     maxAttempts: 5,
 *     onRetry: (attempt) => console.log(`Retry attempt ${attempt}`)
 *   }
 * );
 * ```
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const config = { ...DEFAULT_OPTIONS, ...options };
  let lastError: Error;

  for (let attempt = 1; attempt <= config.maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error: any) {
      lastError = error;

      // Don't retry if it's the last attempt
      if (attempt === config.maxAttempts) {
        break;
      }

      // Don't retry if error is not retryable
      if (!isRetryableError(error, config.retryableStatusCodes)) {
        throw error;
      }

      // Calculate delay and notify
      const delay = calculateDelay(
        attempt,
        config.initialDelay,
        config.maxDelay,
        config.backoffMultiplier
      );

      config.onRetry(attempt, error);

      // Wait before retrying
      await sleep(delay);
    }
  }

  // All retries exhausted
  throw lastError!;
}

/**
 * Checks if the browser is currently online.
 */
export function isOnline(): boolean {
  return navigator.onLine;
}

/**
 * Waits until the browser is back online.
 *
 * @param timeout - Maximum time to wait in milliseconds (optional)
 * @returns Promise that resolves when online or rejects on timeout
 */
export function waitForOnline(timeout?: number): Promise<void> {
  return new Promise((resolve, reject) => {
    if (isOnline()) {
      resolve();
      return;
    }

    let timeoutId: number | undefined;

    const handleOnline = () => {
      if (timeoutId) {
        window.clearTimeout(timeoutId);
      }
      window.removeEventListener('online', handleOnline);
      resolve();
    };

    window.addEventListener('online', handleOnline);

    if (timeout) {
      timeoutId = window.setTimeout(() => {
        window.removeEventListener('online', handleOnline);
        reject(new Error('Timeout waiting for online connection'));
      }, timeout);
    }
  });
}

/**
 * Local storage key for offline queue
 */
const OFFLINE_QUEUE_KEY = 'charlee_offline_queue';

export interface QueuedRequest {
  id: string;
  timestamp: number;
  endpoint: string;
  method: string;
  data: any;
  retries: number;
}

/**
 * Offline queue manager for storing failed requests.
 */
export class OfflineQueue {
  /**
   * Adds a request to the offline queue.
   */
  static enqueue(request: Omit<QueuedRequest, 'id' | 'timestamp' | 'retries'>): void {
    const queue = this.getQueue();
    const newRequest: QueuedRequest = {
      ...request,
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      retries: 0,
    };

    queue.push(newRequest);
    localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue));
  }

  /**
   * Gets all queued requests.
   */
  static getQueue(): QueuedRequest[] {
    try {
      const stored = localStorage.getItem(OFFLINE_QUEUE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  /**
   * Removes a request from the queue by ID.
   */
  static dequeue(id: string): void {
    const queue = this.getQueue().filter((req) => req.id !== id);
    localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue));
  }

  /**
   * Clears all queued requests.
   */
  static clear(): void {
    localStorage.removeItem(OFFLINE_QUEUE_KEY);
  }

  /**
   * Gets the number of queued requests.
   */
  static size(): number {
    return this.getQueue().length;
  }

  /**
   * Increments retry count for a request.
   */
  static incrementRetries(id: string): void {
    const queue = this.getQueue();
    const request = queue.find((req) => req.id === id);

    if (request) {
      request.retries++;
      localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue));
    }
  }
}
