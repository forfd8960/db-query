import { Button, Card, Input, message, Space, Spin, Tabs, Tag } from 'antd';
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { SiMysql, SiPostgresql } from 'react-icons/si';

import { QueryResults } from '../components/QueryResults';
import { SqlEditor } from '../components/SqlEditor';
import { databaseApi, queryApi } from '../services/api';
import type { DatabaseConnection } from '../types/database';
import type { QueryResult } from '../types/query';

const { TextArea } = Input;

export const QueryTool: React.FC = () => {
  const { dbName } = useParams<{ dbName: string }>();
  const [database, setDatabase] = useState<DatabaseConnection | null>(null);
  const [sql, setSql] = useState('SELECT * FROM ');
  const [naturalLanguage, setNaturalLanguage] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatingSQL, setGeneratingSQL] = useState(false);
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [activeTab, setActiveTab] = useState<string>('sql');

  useEffect(() => {
    loadDatabase();
  }, [dbName]);

  const loadDatabase = async () => {
    if (!dbName) return;
    
    try {
      const databases = await databaseApi.list();
      const db = databases.find((d: DatabaseConnection) => d.name === dbName);
      if (db) {
        setDatabase(db);
      }
    } catch (error) {
      console.error('Failed to load database info:', error);
    }
  };

  const handleExecuteQuery = async () => {
    if (!dbName) {
      message.error('Database name is required');
      return;
    }

    if (!sql.trim()) {
      message.error('SQL query is required');
      return;
    }

    setLoading(true);
    setQueryResult(null);

    try {
      const result = await queryApi.execute(dbName, { sql });
      setQueryResult(result);
      message.success('Query executed successfully');
    } catch (error: any) {
      message.error(error.response?.data?.message || 'Failed to execute query');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSQL = async () => {
    if (!dbName) {
      message.error('Database name is required');
      return;
    }

    if (!naturalLanguage.trim()) {
      message.error('Natural language prompt is required');
      return;
    }

    setGeneratingSQL(true);

    try {
      const result = await queryApi.generateFromNaturalLanguage(dbName, { prompt: naturalLanguage });
      setSql(result.sql);
      message.success(result.explanation);
      setActiveTab('sql'); // Switch to SQL tab to show generated SQL
    } catch (error: any) {
      message.error(error.response?.data?.message || 'Failed to generate SQL');
    } finally {
      setGeneratingSQL(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    // Ctrl/Cmd + Enter to execute
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleExecuteQuery();
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <h1 style={{ margin: 0 }}>Query Tool - {dbName}</h1>
        {database && (
          <Tag 
            icon={database.databaseType === 'mysql' ? 
              <SiMysql style={{ color: '#00758F' }} /> : 
              <SiPostgresql style={{ color: '#336791' }} />
            }
            color={database.databaseType === 'mysql' ? 'blue' : 'purple'}
            style={{ fontSize: 14 }}
          >
            {database.databaseType === 'mysql' ? 'MySQL' : 'PostgreSQL'}
          </Tag>
        )}
      </div>

      <Card style={{ marginBottom: 24 }}>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'sql',
              label: 'SQL Query',
              children: (
                <div>
                  <div onKeyDown={handleKeyPress}>
                    <SqlEditor value={sql} onChange={setSql} height="300px" />
                  </div>
                  <div style={{ marginTop: 12 }}>
                    <Button type="primary" onClick={handleExecuteQuery} loading={loading}>
                      Execute Query (Ctrl+Enter)
                    </Button>
                  </div>
                </div>
              ),
            },
            {
              key: 'nl',
              label: 'Natural Language',
              children: (
                <div>
                  <TextArea
                    value={naturalLanguage}
                    onChange={(e) => setNaturalLanguage(e.target.value)}
                    placeholder="Describe what you want to query in plain English..."
                    rows={6}
                    style={{ marginBottom: 12 }}
                  />
                  <Space>
                    <Button
                      type="primary"
                      onClick={handleGenerateSQL}
                      loading={generatingSQL}
                    >
                      Generate SQL
                    </Button>
                    <span style={{ color: '#666', fontSize: 12 }}>
                      Powered by OpenAI
                    </span>
                  </Space>
                </div>
              ),
            },
          ]}
        />
      </Card>

      {loading && (
        <Card>
          <div style={{ textAlign: 'center', padding: 48 }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>Executing query...</div>
          </div>
        </Card>
      )}

      {!loading && queryResult && (
        <Card title="Query Results">
          <QueryResults result={queryResult} dbName={dbName} />
        </Card>
      )}
    </div>
  );
};
