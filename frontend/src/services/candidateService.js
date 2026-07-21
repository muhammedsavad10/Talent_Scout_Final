import { request } from './request';

/**
 * Service for candidate-specific screening decisions and communications.
 */
export const candidateService = {
  /**
   * Generates a communication email template (invite/rejection) for a candidate.
   * Preserves raw POST /api/v1/evaluation/email/generate payload contract.
   */
  async generateCommunicationEmail(payload) {
    return request({
      method: 'POST',
      url: '/api/v1/evaluation/email/generate',
      data: payload
    });
  }
};
