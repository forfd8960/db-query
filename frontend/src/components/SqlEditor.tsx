import Editor, { type OnMount } from '@monaco-editor/react';
import React, { useRef } from 'react';

interface SqlEditorProps {
  value: string;
  onChange: (value: string) => void;
  readOnly?: boolean;
  height?: string;
}

export const SqlEditor: React.FC<SqlEditorProps> = ({
  value,
  onChange,
  readOnly = false,
  height = '300px',
}) => {
  const editorRef = useRef<any>(null);

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;

    // Configure editor options
    editor.updateOptions({
      minimap: { enabled: false },
      fontSize: 14,
      lineNumbers: 'on',
      readOnly,
      scrollBeyondLastLine: false,
      automaticLayout: true,
    });

    // Add PostgreSQL keywords
    monaco.languages.setLanguageConfiguration('sql', {
      comments: {
        lineComment: '--',
        blockComment: ['/*', '*/'],
      },
      brackets: [
        ['(', ')'],
        ['[', ']'],
      ],
      autoClosingPairs: [
        { open: '(', close: ')' },
        { open: '[', close: ']' },
        { open: "'", close: "'" },
        { open: '"', close: '"' },
      ],
    });
  };

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      onChange(value);
    }
  };

  return (
    <Editor
      height={height}
      defaultLanguage="sql"
      value={value}
      onChange={handleEditorChange}
      onMount={handleEditorDidMount}
      theme="vs-dark"
      options={{
        readOnly,
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: 'on',
        scrollBeyondLastLine: false,
        automaticLayout: true,
      }}
    />
  );
};
