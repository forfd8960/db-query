/**
 * TypeScript types for query execution.
 */

export interface QueryRequest {
  sql: string;
}

export interface QueryResult {
  columns: string[];
  rows: Record<string, any>[];
  rowCount: number;
  executionTime: number; // milliseconds
}

export interface NaturalLanguageQueryRequest {
  prompt: string;
}

export interface NaturalLanguageQueryResponse {
  sql: string;
  explanation: string;
}
