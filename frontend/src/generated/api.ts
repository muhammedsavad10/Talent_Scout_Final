/**
 * Clean TypeScript API contracts for TalentScout Enterprise REST endpoints.
 */

export interface paths {
  '/api/v1/evaluate/batch': {
    post: {
      responses: {
        200: {
          content: {
            'application/json': {
              batch_id: string;
              status: string;
            };
          };
        };
      };
    };
  };
  '/api/v1/evaluate/batch/{batch_id}': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': {
              batch_id: string;
              status: string;
              total: number;
              completed: number;
              failed: number;
              results?: {
                ranked_candidates?: any[];
              };
            };
          };
        };
      };
    };
  };
  '/api/v1/evaluation/status/{id}': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': {
              evaluation_id: string;
              status: string;
              result: any;
            };
          };
        };
      };
    };
  };
  '/api/v1/evaluation/status/{evaluation_id}': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': {
              evaluation_id: string;
              status: string;
              result: any;
            };
          };
        };
      };
    };
  };
  '/api/v1/evaluation/evaluate': {
    post: {
      responses: {
        200: {
          content: {
            'application/json': any;
          };
        };
      };
    };
  };
  '/api/v1/evaluation/assistant/ask': {
    post: {
      responses: {
        200: {
          content: {
            'application/json': {
              answer: string;
              citations?: string[];
            };
          };
        };
      };
    };
  };
  '/api/v1/evaluation/email/generate': {
    post: {
      responses: {
        200: {
          content: {
            'application/json': {
              subject: string;
              body: string;
            };
          };
        };
      };
    };
  };
  '/api/v1/copilot/ask': {
    post: {
      responses: {
        200: {
          content: {
            'application/json': {
              answer: string;
              citations?: string[];
            };
          };
        };
      };
    };
  };
}
