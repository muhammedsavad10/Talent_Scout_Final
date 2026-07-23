import React from 'react';
import { FileText, Trash2 } from 'lucide-react';
import { Text } from '@/shared/ui';

interface SelectedFilesProps {
  files: File[];
  onRemove: (index: number) => void;
}

export const SelectedFiles: React.FC<SelectedFilesProps> = ({ files, onRemove }) => {
  if (files.length === 0) return null;

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%', marginTop: '12px' }}>
      <Text style={{ fontWeight: 600, fontSize: '13px' }}>Selected Resumes ({files.length})</Text>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {files.map((file, idx) => (
          <div
            key={`${file.name}-${idx}`}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '10px 14px',
              background: 'hsla(var(--foreground), 0.02)',
              border: '1px solid hsl(var(--border))',
              borderRadius: 'var(--radius)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
              <FileText size={18} style={{ color: 'hsl(var(--muted-foreground))', flexShrink: 0 }} />
              <div style={{ display: 'flex', flexDirection: 'column', minWidth: 0 }}>
                <span style={{ fontSize: '13px', fontWeight: 500, color: '#ffffff', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                  {file.name}
                </span>
                <span style={{ fontSize: '11px', color: 'hsl(var(--muted-foreground))' }}>
                  {formatSize(file.size)}
                </span>
              </div>
            </div>
            
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRemove(idx);
              }}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'hsl(var(--destructive))',
                cursor: 'pointer',
                padding: '4px',
                borderRadius: '4px',
                transition: 'var(--transition)',
              }}
              aria-label={`Remove file ${file.name}`}
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
export default SelectedFiles;
