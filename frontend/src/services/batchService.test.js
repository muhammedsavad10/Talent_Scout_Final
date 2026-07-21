import { vi, describe, it, expect, beforeEach } from 'vitest';
import { batchService } from './batchService';
import { request } from './request';

vi.mock('./request', () => ({
  request: vi.fn()
}));

describe('batchService.js', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('calls batchEvaluate with correct endpoint and headers', async () => {
    const mockFormData = new FormData();
    vi.mocked(request).mockResolvedValue({ batch_id: 'batch_123' });

    const result = await batchService.batchEvaluate(mockFormData);

    expect(request).toHaveBeenCalledWith({
      method: 'POST',
      url: '/api/v1/evaluate/batch',
      data: mockFormData,
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
    expect(result).toEqual({ batch_id: 'batch_123' });
  });

  it('calls getBatchStatus with correct batch endpoint', async () => {
    vi.mocked(request).mockResolvedValue({ status: 'PROCESSING' });

    const result = await batchService.getBatchStatus('batch_123');

    expect(request).toHaveBeenCalledWith({
      method: 'GET',
      url: '/api/v1/evaluate/batch/status/batch_123'
    });
    expect(result).toEqual({ status: 'PROCESSING' });
  });
});
