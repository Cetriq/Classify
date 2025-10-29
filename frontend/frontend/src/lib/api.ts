/**
 * API client for Klassa backend.
 */

import axios from 'axios';
import { ClassificationInput, ClassificationOutput } from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const klassaApi = {
  /**
   * Classify a single object.
   */
  classify: async (input: ClassificationInput): Promise<ClassificationOutput> => {
    const response = await apiClient.post<ClassificationOutput>('/classify', input);
    return response.data;
  },

  /**
   * Classify multiple objects in batch.
   */
  classifyBatch: async (inputs: ClassificationInput[]): Promise<ClassificationOutput[]> => {
    const response = await apiClient.post<ClassificationOutput[]>('/classify/batch', inputs);
    return response.data;
  },

  /**
   * Health check.
   */
  health: async (): Promise<{ status: string; classifier: string }> => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};
