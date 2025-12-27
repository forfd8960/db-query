import { Table } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import React from 'react';

import type { QueryResult } from '../types/query';
import { ExportButton } from './ExportButton';

interface QueryResultsProps {
  result: QueryResult | null;
  loading?: boolean;
  dbName?: string;
}

export const QueryResults: React.FC<QueryResultsProps> = ({ result, loading = false, dbName }) => {
  if (!result) {
    return null;
  }

  // Build table columns from result columns
  const columns: ColumnsType<Record<string, any>> = result.columns.map((col) => ({
    title: col,
    dataIndex: col,
    key: col,
    ellipsis: true,
    render: (value: any) => {
      if (value === null) {
        return <span style={{ color: '#999', fontStyle: 'italic' }}>NULL</span>;
      }
      if (typeof value === 'object') {
        return JSON.stringify(value);
      }
      return String(value);
    },
  }));

  // Add row keys
  const dataSource = result.rows.map((row, index) => ({
    ...row,
    key: index,
  }));

  return (
    <div>
      <div style={{ 
        marginBottom: 12, 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center' 
      }}>
        <span style={{ color: '#666' }}>
          {result.rowCount} {result.rowCount === 1 ? 'row' : 'rows'} returned in{' '}
          {result.executionTime}ms
        </span>
        {dbName && (
          <ExportButton
            dbName={dbName}
            queryResults={{
              columns: result.columns,
              rows: result.rows,
              rowCount: result.rowCount,
            }}
            disabled={loading}
          />
        )}
      </div>
      <Table
        columns={columns}
        dataSource={dataSource}
        loading={loading}
        pagination={{
          pageSize: 50,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} rows`,
        }}
        scroll={{ x: 'max-content', y: 500 }}
        bordered
        size="small"
      />
    </div>
  );
};
