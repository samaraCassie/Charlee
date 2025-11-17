import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  retryWithBackoff,
  isOnline,
  waitForOnline,
  OfflineQueue,
  type RetryOptions,
} from '@/lib/retry';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

vi.stubGlobal('localStorage', localStorageMock);

describe('retry utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  describe('retryWithBackoff', () => {
    it('should succeed on first attempt', async () => {
      const fn = vi.fn().mockResolvedValue('success');

      const result = await retryWithBackoff(fn);

      expect(result).toBe('success');
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it('should retry on network error and eventually succeed', async () => {
      const fn = vi
        .fn()
        .mockRejectedValueOnce({ message: 'Network error' })
        .mockRejectedValueOnce({ message: 'Network error' })
        .mockResolvedValue('success');

      const onRetry = vi.fn();

      const promise = retryWithBackoff(fn, { maxAttempts: 3, onRetry });

      // Fast-forward through all retries
      await vi.runAllTimersAsync();

      const result = await promise;

      expect(result).toBe('success');
      expect(fn).toHaveBeenCalledTimes(3);
      expect(onRetry).toHaveBeenCalledTimes(2);
    });

    it('should retry on retryable status codes', async () => {
      const fn = vi
        .fn()
        .mockRejectedValueOnce({ response: { status: 503 } })
        .mockResolvedValue('success');

      const promise = retryWithBackoff(fn, { maxAttempts: 3 });

      await vi.runAllTimersAsync();

      const result = await promise;

      expect(result).toBe('success');
      expect(fn).toHaveBeenCalledTimes(2);
    });

    it('should not retry on non-retryable errors', async () => {
      const fn = vi.fn().mockRejectedValue({ response: { status: 400 } });

      const promise = retryWithBackoff(fn, { maxAttempts: 3 });

      await expect(promise).rejects.toEqual({ response: { status: 400 } });
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it('should throw last error after all retries exhausted', async () => {
      const lastError = { message: 'Final error' };
      const fn = vi.fn().mockRejectedValue(lastError);

      const promise = retryWithBackoff(fn, { maxAttempts: 3 });

      // Run timers and catch the rejection
      const runTimers = vi.runAllTimersAsync();

      // Wait for promise to reject
      await expect(promise).rejects.toEqual(lastError);

      // Complete timer operations
      await runTimers;

      expect(fn).toHaveBeenCalledTimes(3);
    });

    it('should use exponential backoff', async () => {
      const fn = vi
        .fn()
        .mockRejectedValueOnce({ message: 'Error 1' })
        .mockRejectedValueOnce({ message: 'Error 2' })
        .mockResolvedValue('success');

      const promise = retryWithBackoff(fn, {
        maxAttempts: 3,
        initialDelay: 1000,
        backoffMultiplier: 2,
      });

      // First retry after 1000ms
      await vi.advanceTimersByTimeAsync(1000);
      expect(fn).toHaveBeenCalledTimes(2);

      // Second retry after 2000ms (exponential)
      await vi.advanceTimersByTimeAsync(2000);
      expect(fn).toHaveBeenCalledTimes(3);

      const result = await promise;
      expect(result).toBe('success');
    });

    it('should respect maxDelay', async () => {
      const fn = vi
        .fn()
        .mockRejectedValueOnce({ message: 'Error 1' })
        .mockRejectedValueOnce({ message: 'Error 2' })
        .mockResolvedValue('success');

      const promise = retryWithBackoff(fn, {
        maxAttempts: 3,
        initialDelay: 10000,
        maxDelay: 5000,
        backoffMultiplier: 2,
      });

      // First retry should be capped at maxDelay (5000ms instead of 10000ms)
      await vi.advanceTimersByTimeAsync(5000);
      expect(fn).toHaveBeenCalledTimes(2);

      await vi.advanceTimersByTimeAsync(5000);
      const result = await promise;
      expect(result).toBe('success');
    });

    it('should call onRetry callback with attempt and error', async () => {
      const error = { message: 'Test error' };
      const fn = vi.fn().mockRejectedValueOnce(error).mockResolvedValue('success');

      const onRetry = vi.fn();

      const promise = retryWithBackoff(fn, { maxAttempts: 2, onRetry });

      await vi.runAllTimersAsync();
      await promise;

      expect(onRetry).toHaveBeenCalledWith(1, error);
    });

    it('should use custom retryable status codes', async () => {
      const fn = vi.fn().mockRejectedValue({ response: { status: 418 } });

      const promise = retryWithBackoff(fn, {
        maxAttempts: 2,
        retryableStatusCodes: [418],
      });

      // Run all timers
      const timerPromise = vi.runAllTimersAsync();

      // Expect the promise to reject
      await expect(promise).rejects.toEqual({ response: { status: 418 } });

      // Complete timer operations
      await timerPromise;

      expect(fn).toHaveBeenCalledTimes(2);
    });
  });

  describe('isOnline', () => {
    it('should return true when navigator.onLine is true', () => {
      vi.stubGlobal('navigator', { onLine: true });
      expect(isOnline()).toBe(true);
    });

    it('should return false when navigator.onLine is false', () => {
      vi.stubGlobal('navigator', { onLine: false });
      expect(isOnline()).toBe(false);
    });
  });

  describe('waitForOnline', () => {
    it('should resolve immediately if already online', async () => {
      vi.stubGlobal('navigator', { onLine: true });

      const promise = waitForOnline();
      await expect(promise).resolves.toBeUndefined();
    });

    it('should wait for online event', async () => {
      vi.stubGlobal('navigator', { onLine: false });

      const promise = waitForOnline();

      // Simulate going online
      vi.stubGlobal('navigator', { onLine: true });
      window.dispatchEvent(new Event('online'));

      await expect(promise).resolves.toBeUndefined();
    });

    it('should reject on timeout', async () => {
      vi.stubGlobal('navigator', { onLine: false });

      const promise = waitForOnline(1000);

      // Fast-forward past timeout and catch rejection
      const timerPromise = vi.advanceTimersByTimeAsync(1000);

      await expect(promise).rejects.toThrow('Timeout waiting for online connection');

      // Complete timer operations
      await timerPromise;
    });

    it('should clear timeout when online event fires', async () => {
      vi.stubGlobal('navigator', { onLine: false });

      const clearTimeoutSpy = vi.spyOn(window, 'clearTimeout');

      const promise = waitForOnline(5000);

      // Go online before timeout
      await vi.advanceTimersByTimeAsync(100);
      vi.stubGlobal('navigator', { onLine: true });
      window.dispatchEvent(new Event('online'));

      await promise;

      expect(clearTimeoutSpy).toHaveBeenCalled();
    });
  });

  describe('OfflineQueue', () => {
    beforeEach(() => {
      OfflineQueue.clear();
    });

    afterEach(() => {
      OfflineQueue.clear();
    });

    describe('enqueue', () => {
      it('should add request to queue', () => {
        OfflineQueue.enqueue({
          endpoint: '/api/test',
          method: 'POST',
          data: { foo: 'bar' },
        });

        const queue = OfflineQueue.getQueue();
        expect(queue).toHaveLength(1);
        expect(queue[0]).toMatchObject({
          endpoint: '/api/test',
          method: 'POST',
          data: { foo: 'bar' },
          retries: 0,
        });
        expect(queue[0].id).toBeDefined();
        expect(queue[0].timestamp).toBeDefined();
      });

      it('should generate unique IDs for each request', () => {
        OfflineQueue.enqueue({
          endpoint: '/api/test1',
          method: 'POST',
          data: {},
        });

        OfflineQueue.enqueue({
          endpoint: '/api/test2',
          method: 'POST',
          data: {},
        });

        const queue = OfflineQueue.getQueue();
        expect(queue[0].id).not.toBe(queue[1].id);
      });
    });

    describe('getQueue', () => {
      it('should return empty array when no queue exists', () => {
        expect(OfflineQueue.getQueue()).toEqual([]);
      });

      it('should return all queued requests', () => {
        OfflineQueue.enqueue({ endpoint: '/api/1', method: 'POST', data: {} });
        OfflineQueue.enqueue({ endpoint: '/api/2', method: 'POST', data: {} });

        const queue = OfflineQueue.getQueue();
        expect(queue).toHaveLength(2);
      });

      it('should handle corrupted localStorage data', () => {
        localStorage.setItem('charlee_offline_queue', 'invalid json');

        expect(OfflineQueue.getQueue()).toEqual([]);
      });
    });

    describe('dequeue', () => {
      it('should remove request by ID', () => {
        OfflineQueue.enqueue({ endpoint: '/api/1', method: 'POST', data: {} });
        OfflineQueue.enqueue({ endpoint: '/api/2', method: 'POST', data: {} });

        const queue = OfflineQueue.getQueue();
        const idToRemove = queue[0].id;

        OfflineQueue.dequeue(idToRemove);

        const updatedQueue = OfflineQueue.getQueue();
        expect(updatedQueue).toHaveLength(1);
        expect(updatedQueue[0].endpoint).toBe('/api/2');
      });

      it('should handle removing non-existent ID', () => {
        OfflineQueue.enqueue({ endpoint: '/api/1', method: 'POST', data: {} });

        OfflineQueue.dequeue('non-existent-id');

        expect(OfflineQueue.getQueue()).toHaveLength(1);
      });
    });

    describe('clear', () => {
      it('should remove all queued requests', () => {
        OfflineQueue.enqueue({ endpoint: '/api/1', method: 'POST', data: {} });
        OfflineQueue.enqueue({ endpoint: '/api/2', method: 'POST', data: {} });

        OfflineQueue.clear();

        expect(OfflineQueue.getQueue()).toEqual([]);
      });
    });

    describe('size', () => {
      it('should return 0 for empty queue', () => {
        expect(OfflineQueue.size()).toBe(0);
      });

      it('should return correct count of queued requests', () => {
        OfflineQueue.enqueue({ endpoint: '/api/1', method: 'POST', data: {} });
        expect(OfflineQueue.size()).toBe(1);

        OfflineQueue.enqueue({ endpoint: '/api/2', method: 'POST', data: {} });
        expect(OfflineQueue.size()).toBe(2);
      });
    });

    describe('incrementRetries', () => {
      it('should increment retry count for specific request', () => {
        OfflineQueue.enqueue({ endpoint: '/api/test', method: 'POST', data: {} });

        const queue = OfflineQueue.getQueue();
        const requestId = queue[0].id;

        expect(queue[0].retries).toBe(0);

        OfflineQueue.incrementRetries(requestId);

        const updatedQueue = OfflineQueue.getQueue();
        expect(updatedQueue[0].retries).toBe(1);
      });

      it('should handle incrementing non-existent request', () => {
        OfflineQueue.enqueue({ endpoint: '/api/test', method: 'POST', data: {} });

        OfflineQueue.incrementRetries('non-existent-id');

        const queue = OfflineQueue.getQueue();
        expect(queue[0].retries).toBe(0);
      });

      it('should increment retries multiple times', () => {
        OfflineQueue.enqueue({ endpoint: '/api/test', method: 'POST', data: {} });

        const queue = OfflineQueue.getQueue();
        const requestId = queue[0].id;

        OfflineQueue.incrementRetries(requestId);
        OfflineQueue.incrementRetries(requestId);
        OfflineQueue.incrementRetries(requestId);

        const updatedQueue = OfflineQueue.getQueue();
        expect(updatedQueue[0].retries).toBe(3);
      });
    });
  });
});
