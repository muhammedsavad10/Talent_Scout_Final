import { vi, describe, it, expect, beforeEach } from 'vitest';
import { evaluationService } from './evaluationService';
import { request } from './request';

vi.mock('./request', () => ({
  request: vi.fn()
}));

describe('evaluationService.js', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('calls evaluate with correct endpoint and headers', async () => {
    const mockFormData = new FormData();
    vi.mocked(request).mockResolvedValue({ status: 'SUCCESS' });

    const result = await evaluationService.evaluate(mockFormData);

    expect(request).toHaveBeenCalledWith({
      method: 'POST',
      url: '/api/v1/evaluate',
      data: mockFormData,
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
    expect(result).toEqual({ status: 'SUCCESS' });
  });

  it('calls getEvaluationStatus with correct endpoint', async () => {
    vi.mocked(request).mockResolvedValue({ status: 'COMPLETED' });

    const result = await evaluationService.getEvaluationStatus('eval_123');

    expect(request).toHaveBeenCalledWith({
      method: 'GET',
      url: '/api/v1/evaluation/status/eval_123'
    });
    expect(result).toEqual({ status: 'COMPLETED' });
  });

  it('calls checkHealth with correct health check endpoint', async () => {
    vi.mocked(request).mockResolvedValue({ status: 'healthy' });

    const result = await evaluationService.checkHealth();

    expect(request).toHaveBeenCalledWith({
      method: 'GET',
      url: '/health/databases'
    });
    expect(result).toEqual({ status: 'healthy' });
  });

  it('calls verifyDevMode with correct endpoint and credentials', async () => {
    vi.mocked(request).mockResolvedValue({ success: true });

    const result = await evaluationService.verifyDevMode('password123');

    expect(request).toHaveBeenCalledWith({
      method: 'POST',
      url: '/api/v1/evaluation/dev-mode/verify',
      data: { password: 'password123' }
    });
    expect(result).toEqual({ success: true });
  });
});
