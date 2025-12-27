/**
 * Export-related TypeScript types
 */

/**
 * Supported export file formats
 */
export type ExportFormat = 'csv' | 'json' | 'excel';

/**
 * Export request payload
 */
export interface ExportRequest {
  format: ExportFormat;
  queryResults: {
    columns: string[];
    rows: Record<string, any>[];
    rowCount: number;
    executionTime: number;
  };
}
