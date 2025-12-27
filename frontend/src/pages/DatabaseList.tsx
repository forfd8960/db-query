import { useEffect, useState } from 'react';
import {
  DatabaseOutlined,
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { SiMysql, SiPostgresql } from 'react-icons/si';
import { Button, Card, Col, Form, Input, message, Modal, Popconfirm, Row, Space, Table } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useNavigate } from 'react-router-dom';

import { ColumnDetails } from '../components/ColumnDetails';
import { SchemaTree } from '../components/SchemaTree';
import { databaseApi } from '../services/api';
import type { DatabaseConnection, DatabaseConnectionCreate, TableMetadata } from '../types/database';

export const DatabaseList = () => {
  const navigate = useNavigate();
  const [databases, setDatabases] = useState<DatabaseConnection[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingDb, setEditingDb] = useState<string | null>(null);
  const [selectedDb, setSelectedDb] = useState<string | null>(null);
  const [selectedTable, setSelectedTable] = useState<TableMetadata | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadDatabases();
  }, []);

  const loadDatabases = async () => {
    setLoading(true);
    try {
      const data = await databaseApi.list();
      setDatabases(Array.isArray(data) ? data : []);
    } catch (error) {
      message.error('Failed to load databases');
      setDatabases([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (values: DatabaseConnectionCreate) => {
    try {
      await databaseApi.create(values);
      message.success('Database connection created');
      setIsModalOpen(false);
      form.resetFields();
      loadDatabases();
    } catch (error: any) {
      message.error(error.response?.data?.message || 'Failed to create connection');
    }
  };

  const handleUpdate = async (dbName: string, values: { url: string }) => {
    try {
      await databaseApi.update(dbName, values);
      message.success('Database connection updated');
      setIsModalOpen(false);
      setEditingDb(null);
      form.resetFields();
      loadDatabases();
    } catch (error: any) {
      message.error(error.response?.data?.message || 'Failed to update connection');
    }
  };

  const handleDelete = async (dbName: string) => {
    try {
      await databaseApi.delete(dbName);
      message.success('Database connection deleted');
      loadDatabases();
    } catch (error: any) {
      message.error(error.response?.data?.message || 'Failed to delete connection');
    }
  };

  const columns: ColumnsType<DatabaseConnection> = [
    {
      title: 'Type',
      dataIndex: 'databaseType',
      key: 'databaseType',
      width: 80,
      render: (type: string) => (
        <span style={{ fontSize: '20px', display: 'flex', alignItems: 'center' }}>
          {type === 'mysql' ? (
            <SiMysql style={{ color: '#00758F' }} title="MySQL" />
          ) : (
            <SiPostgresql style={{ color: '#336791' }} title="PostgreSQL" />
          )}
        </span>
      ),
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => (
        <Button type="link" onClick={() => setSelectedDb(name)}>
          {name}
        </Button>
      ),
    },
    {
      title: 'URL',
      dataIndex: 'url',
      key: 'url',
      ellipsis: true,
    },
    {
      title: 'Created',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: 'Last Connected',
      dataIndex: 'lastConnectedAt',
      key: 'lastConnectedAt',
      render: (date: string | undefined) => (date ? new Date(date).toLocaleString() : 'Never'),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            icon={<DatabaseOutlined />}
            onClick={() => navigate(`/databases/${record.name}/query`)}
          >
            Query
          </Button>
          <Button
            icon={<EditOutlined />}
            onClick={() => {
              setEditingDb(record.name);
              form.setFieldsValue({ url: record.url });
              setIsModalOpen(true);
            }}
          />
          <Popconfirm
            title="Delete database connection?"
            description="This will also delete cached metadata."
            onConfirm={() => handleDelete(record.name)}
            okText="Yes"
            cancelText="No"
          >
            <Button icon={<DeleteOutlined />} danger />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="p-6">
      <Row gutter={16}>
        <Col span={12}>
          <Card
            title="Database Connections"
            extra={
              <Space>
                <Button icon={<ReloadOutlined />} onClick={loadDatabases}>
                  Refresh
                </Button>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => {
                    setEditingDb(null);
                    form.resetFields();
                    setIsModalOpen(true);
                  }}
                >
                  New Connection
                </Button>
              </Space>
            }
          >
            <Table
              columns={columns}
              dataSource={databases}
              rowKey="id"
              loading={loading}
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </Col>
        <Col span={6}>
          {selectedDb && (
            <Card>
              <SchemaTree dbName={selectedDb} onTableSelect={setSelectedTable} />
            </Card>
          )}
        </Col>
        <Col span={6}>
          {selectedDb && (
            <Card>
              <ColumnDetails table={selectedTable} />
            </Card>
          )}
        </Col>
      </Row>

      <Modal
        title={editingDb ? 'Edit Database Connection' : 'New Database Connection'}
        open={isModalOpen}
        onCancel={() => {
          setIsModalOpen(false);
          setEditingDb(null);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        okText={editingDb ? 'Update' : 'Create'}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={(values) => {
            if (editingDb) {
              handleUpdate(editingDb, values);
            } else {
              handleCreate(values);
            }
          }}
        >
          <Form.Item
            label="Database Connection URL"
            name="url"
            rules={[
              { required: true, message: 'Please enter connection URL' },
              {
                pattern: /^(postgres(ql)?|mysql):\/\/.+/,
                message: 'URL must start with postgresql://, postgres://, or mysql://',
              },
            ]}
            help="PostgreSQL: postgresql://user:password@host:port/database | MySQL: mysql://user:password@host:port/database"
          >
            <Input.TextArea 
              placeholder="postgresql://user:password@host:port/database&#10;mysql://user:password@host:port/database" 
              rows={2}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};
