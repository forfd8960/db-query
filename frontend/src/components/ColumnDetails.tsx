import { CheckCircleOutlined, CloseCircleOutlined, KeyOutlined } from '@ant-design/icons';
import { Descriptions, Tag } from 'antd';
import React from 'react';

import type { TableMetadata } from '../types/database';

interface ColumnDetailsProps {
  table: TableMetadata | null;
}

export const ColumnDetails: React.FC<ColumnDetailsProps> = ({ table }) => {
  if (!table) {
    return (
      <div style={{ padding: 16, color: '#999', textAlign: 'center' }}>
        Select a table to view column details
      </div>
    );
  }

  return (
    <div>
      <h3>
        {table.schema}.{table.name}
      </h3>
      <p style={{ color: '#666', marginBottom: 16 }}>
        {table.tableType} • {table.rowCount ?? '?'} rows
      </p>

      <div>
        {table.columns.map((column) => (
          <Descriptions
            key={column.name}
            bordered
            size="small"
            column={1}
            style={{ marginBottom: 16 }}
            title={
              <span>
                {column.name}
                {column.isPrimaryKey && (
                  <Tag icon={<KeyOutlined />} color="gold" style={{ marginLeft: 8 }}>
                    PRIMARY KEY
                  </Tag>
                )}
              </span>
            }
          >
            <Descriptions.Item label="Data Type">
              <code>{column.dataType}</code>
            </Descriptions.Item>
            <Descriptions.Item label="Nullable">
              {column.isNullable ? (
                <Tag icon={<CheckCircleOutlined />} color="success">
                  YES
                </Tag>
              ) : (
                <Tag icon={<CloseCircleOutlined />} color="error">
                  NO
                </Tag>
              )}
            </Descriptions.Item>
            {column.columnDefault && (
              <Descriptions.Item label="Default Value">
                <code>{column.columnDefault}</code>
              </Descriptions.Item>
            )}
          </Descriptions>
        ))}
      </div>
    </div>
  );
};
