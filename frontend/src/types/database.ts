/**
 * TypeScript types for database connections and metadata.
 */

export type DatabaseType = 'postgresql' | 'mysql';

export interface DatabaseConnection {
  id: number;
  name: string;
  url: string;
  databaseType: DatabaseType;
  createdAt: string; // ISO 8601
  lastConnectedAt?: string; // ISO 8601, optional
}

export interface DatabaseConnectionCreate {
  url: string;
}

export interface DatabaseConnectionUpdate {
  url: string;
}

export interface ColumnMetadata {
  name: string;
  dataType: string;
  isNullable: boolean;
  columnDefault: string | null;
  isPrimaryKey: boolean;
}

export interface TableMetadata {
  name: string;
  schema: string;
  tableType: 'table' | 'view';
  columns: ColumnMetadata[];
  rowCount: number | null;
}

export interface DatabaseMetadata {
  databaseName: string;
  tables: TableMetadata[];
  extractedAt: string; // ISO 8601
  tableCount: number;
  viewCount: number;
}
