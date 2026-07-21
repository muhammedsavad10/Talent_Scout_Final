import { request } from './request';

/**
 * Service for multi-candidate batch evaluation workflows.
 */
export const batchService = {
  /**
   * Submits multiple candidate resumes for batch evaluation.
   */
  async batchEvaluate(formData) {
    return request({
      method: 'POST',
      url: '/api/v1/evaluate/batch',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * Retrieves progress/results for a batch evaluation job.
   */
  async getBatchStatus(batchId) {
    return request({
      method: 'GET',
      url: `/api/v1/evaluate/batch/status/${batchId}`,
    });
  }
};
