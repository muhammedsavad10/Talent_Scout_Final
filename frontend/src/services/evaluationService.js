import { request } from './request';

/**
 * Service for single-candidate evaluation workflows.
 */
export const evaluationService = {
  /**
   * Submits a single candidate resume for evaluation.
   */
  async evaluate(formData) {
    return request({
      method: 'POST',
      url: '/api/v1/evaluate',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * Retrieves status/result of a specific evaluation.
   */
  async getEvaluationStatus(evaluationId) {
    return request({
      method: 'GET',
      url: `/api/v1/evaluation/status/${evaluationId}`,
    });
  },

  /**
   * Checks database connectivity & server health.
   */
  async checkHealth() {
    return request({
      method: 'GET',
      url: '/health/databases',
    });
  },

  /**
   * Verifies Developer Mode password.
   */
  async verifyDevMode(password) {
    return request({
      method: 'POST',
      url: '/api/v1/evaluation/dev-mode/verify',
      data: { password }
    });
  }
};
