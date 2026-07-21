import { vi, describe, it, expect, beforeEach } from 'vitest';
import { chatService } from './chatService';
import { request } from './request';

vi.mock('./request', () => ({
  request: vi.fn()
}));

describe('chatService.js', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('calls askAssistant with correct endpoint and message payload', async () => {
    const mockPayload = {
      filename: 'resume.pdf',
      question: 'Does the candidate have Python experience?',
      history: [],
      skills_evidence: []
    };
    vi.mocked(request).mockResolvedValue({ answer: 'Yes, 3 years.' });

    const result = await chatService.askAssistant(mockPayload);

    expect(request).toHaveBeenCalledWith({
      method: 'POST',
      url: '/api/v1/evaluation/assistant/ask',
      data: mockPayload
    });
    expect(result).toEqual({ answer: 'Yes, 3 years.' });
  });
});
