import React, { useState } from 'react';
import { Button, Dropdown, message } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import type { ExportFormat } from '../types/export';
import { exportQueryResults } from '../services/api';

interface ExportButtonProps {
  /** Database name for filename generation */
  dbName: string;
  /** Query results to export */
  queryResults: {
    columns: string[];
    rows: Record<string, any>[];
    rowCount: number;
  } | null;
  /** Whether the button should be disabled */
  disabled?: boolean;
}

/**
 * Export button with dropdown menu for format selection.
 * 
 * Features:
 * - Dropdown menu with CSV, JSON, Excel options
 * - Loading state during export
 * - Success/error notifications
 * - Disabled state when no results available
 */
export const ExportButton: React.FC<ExportButtonProps> = ({
  dbName,
  queryResults,
  disabled = false
}) => {
  const [loading, setLoading] = useState(false);

  const handleExport = async (format: ExportFormat) => {
    if (!queryResults) {
      message.error('No query results to export');
      return;
    }

    setLoading(true);
    try {
      await exportQueryResults(dbName, format, queryResults);
      message.success(`Export successful: ${format.toUpperCase()} file downloaded`);
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : 'Export failed. Please try again.';
      message.error(errorMessage);
      console.error('Export error:', error);
    } finally {
      setLoading(false);
    }
  };

  const menuItems: MenuProps['items'] = [
    {
      key: 'csv',
      label: 'Export as CSV',
      onClick: () => handleExport('csv')
    },
    {
      key: 'json',
      label: 'Export as JSON',
      onClick: () => handleExport('json'),
    },
    {
      key: 'excel',
      label: 'Export as Excel',
      onClick: () => handleExport('excel'),
    }
  ];

  const isDisabled = disabled || !queryResults || queryResults.rowCount === 0;

  return (
    <Dropdown 
      menu={{ items: menuItems }} 
      disabled={isDisabled}
      placement="bottomRight"
    >
      <Button
        type="primary"
        icon={<DownloadOutlined />}
        loading={loading}
        disabled={isDisabled}
      >
        Export
      </Button>
    </Dropdown>
  );
};
