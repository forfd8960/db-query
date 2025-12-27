import { DatabaseOutlined, TableOutlined } from '@ant-design/icons';
import { Tree } from 'antd';
import type { DataNode } from 'antd/es/tree';
import React, { useEffect, useState } from 'react';

import { databaseApi } from '../services/api';
import type { DatabaseMetadata, TableMetadata } from '../types/database';

interface SchemaTreeProps {
  dbName: string;
  onTableSelect?: (table: TableMetadata) => void;
}

export const SchemaTree: React.FC<SchemaTreeProps> = ({ dbName, onTableSelect }) => {
  const [metadata, setMetadata] = useState<DatabaseMetadata | null>(null);
  const [selectedKeys, setSelectedKeys] = useState<React.Key[]>([]);

  useEffect(() => {
    loadMetadata();
  }, [dbName]);

  const loadMetadata = async () => {
    try {
      const data = await databaseApi.getMetadata(dbName);
      setMetadata(data);
    } catch (error) {
      console.error('Failed to load metadata:', error);
    }
  };

  const buildTreeData = (): DataNode[] => {
    if (!metadata) return [];

    // Group tables by schema
    const schemaMap = new Map<string, TableMetadata[]>();

    metadata.tables.forEach((table) => {
      const schema = table.schema;
      if (!schemaMap.has(schema)) {
        schemaMap.set(schema, []);
      }
      schemaMap.get(schema)!.push(table);
    });

    // Build tree nodes
    const treeData: DataNode[] = [];

    schemaMap.forEach((tables, schema) => {
      const schemaNode: DataNode = {
        title: schema,
        key: `schema-${schema}`,
        icon: <DatabaseOutlined />,
        children: tables.map((table) => ({
          title: `${table.name} (${table.rowCount ?? '?'} rows)`,
          key: `table-${schema}-${table.name}`,
          icon: <TableOutlined />,
          isLeaf: true,
          data: table, // Store table data for selection
        })),
      };

      treeData.push(schemaNode);
    });

    return treeData;
  };

  const handleSelect = (selectedKeys: React.Key[], info: any) => {
    setSelectedKeys(selectedKeys);

    // Get selected node
    const node = info.node;
    if (node.isLeaf && node.data && onTableSelect) {
      onTableSelect(node.data as TableMetadata);
    }
  };

  return (
    <div>
      <h3>Database Schema</h3>
      <Tree
        showIcon
        defaultExpandAll
        selectedKeys={selectedKeys}
        onSelect={handleSelect}
        treeData={buildTreeData()}
      />
    </div>
  );
};
