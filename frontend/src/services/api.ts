import axios from 'axios';
import type { DatabaseConnection, DatabaseConnectionCreate, DatabaseConnectionUpdate, DatabaseMetadata } from '../types/database';
import type { QueryRequest, QueryResult, NaturalLanguageQueryRequest, NaturalLanguageQueryResponse } from '../types/query';
import type { ExportFormat } from '../types/export';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      // Error in request setup
      console.error('Request Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Database Connection API
export const databaseApi = {
  list: async (): Promise<DatabaseConnection[]> => {
    const response = await apiClient.get<DatabaseConnection[]>('/databases');
    return response.data;
  },

  create: async (data: DatabaseConnectionCreate): Promise<DatabaseConnection> => {
    const response = await apiClient.post<DatabaseConnection>('/databases', data);
    return response.data;
  },

  update: async (dbName: string, data: DatabaseConnectionUpdate): Promise<DatabaseConnection> => {
    const response = await apiClient.put<DatabaseConnection>(`/databases/${dbName}`, data);
    return response.data;
  },

  delete: async (dbName: string): Promise<void> => {
    await apiClient.delete(`/databases/${dbName}`);
  },

  getMetadata: async (dbName: string, refresh = false): Promise<DatabaseMetadata> => {
    const response = await apiClient.get<DatabaseMetadata>(`/databases/${dbName}/metadata`, {
      params: { refresh },
    });
    return response.data;
  },
};

// Query API
export const queryApi = {
  execute: async (dbName: string, data: QueryRequest): Promise<QueryResult> => {
    const response = await apiClient.post<QueryResult>(`/databases/${dbName}/query`, data);
    return response.data;
  },

  generateFromNaturalLanguage: async (
    dbName: string,
    data: NaturalLanguageQueryRequest
  ): Promise<NaturalLanguageQueryResponse> => {
    const response = await apiClient.post<NaturalLanguageQueryResponse>(
      `/databases/${dbName}/nl-query`,
      data
    );
    return response.data;
  },
};

/**
 * Export query results to file.
 * 
 * @param dbName - Database name (used for filename generation)
 * @param format - Export format (csv, json, excel)
 * @param queryResults - Query results to export
 * 
 * @throws Error if export fails or server returns error
 * 
 * Features:
 * - Handles blob response
 * - Extracts filename from Content-Disposition header
 * - Triggers browser download
 * - Automatic cleanup of temporary download link
 */
export async function exportQueryResults(
  dbName: string,
  format: ExportFormat,
  queryResults: {
    columns: string[];
    rows: Record<string, any>[];
    rowCount: number;
  }
): Promise<void> {
  try {
    // Make POST request with blob response type
    const response = await fetch(`${API_BASE_URL}/databases/${dbName}/export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        format,
        queryResults,
      }),
    });

    // Check for error responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || `Export failed with status ${response.status}`;
      throw new Error(errorMessage);
    }

    // Get blob from response
    const blob = await response.blob();

    // Extract filename from Content-Disposition header
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = `export.${format}`;
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+?)"?$/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }

    // Create download link and trigger download
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();

    // Cleanup
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    // Re-throw with better error message if needed
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Export failed. Please try again.');
  }
}

export default apiClient;
