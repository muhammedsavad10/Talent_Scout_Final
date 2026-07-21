import { request } from './request';

/**
 * Service for interaction with the RAG QA evaluation assistant.
 */
export const chatService = {
  /**
   * Submits a question about a candidate resume to the assistant swarm.
   * Preserves raw POST /api/v1/evaluation/assistant/ask payload contract.
   */
  async askAssistant(payload) {
    return request({
      method: 'POST',
      url: '/api/v1/evaluation/assistant/ask',
      data: payload
    });
  }
};
