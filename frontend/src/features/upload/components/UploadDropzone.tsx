import React, { useRef, useState } from 'react';
import { UploadCloud } from 'lucide-react';
import { Heading, Text } from '@/shared/ui';

interface UploadDropzoneProps {
  onFilesSelected: (files: File[]) => void;
}

export const UploadDropzone: React.FC<UploadDropzoneProps> = ({ onFilesSelected }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragActive, setIsDragActive] = useState(false);

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList) return;
    const files = Array.from(fileList);
    onFilesSelected(files);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const onButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div
      onDragEnter={handleDrag}
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onDrop={handleDrop}
      style={{
        width: '100%',
        padding: '48px 24px',
        border: '2px dashed',
        borderColor: isDragActive ? 'hsl(var(--ring))' : 'hsl(var(--border))',
        borderRadius: 'var(--radius)',
        background: isDragActive ? 'hsla(var(--primary), 0.05)' : 'hsla(var(--foreground), 0.01)',
        textAlign: 'center',
        cursor: 'pointer',
        transition: 'var(--transition)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '12px',
      }}
      onClick={onButtonClick}
    >
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="application/pdf"
        style={{ display: 'none' }}
        onChange={handleChange}
      />
      <div style={{
        width: '56px',
        height: '56px',
        borderRadius: '50%',
        background: 'hsla(var(--foreground), 0.03)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: isDragActive ? 'hsl(var(--ring))' : 'hsl(var(--muted-foreground))',
        transition: 'var(--transition)',
      }}>
        <UploadCloud size={28} />
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <Heading level={3} style={{ fontSize: '16px', margin: 0 }}>Drag and drop resumes here</Heading>
        <Text variant="muted" style={{ fontSize: '13px' }}>Support PDF format up to 5MB.</Text>
      </div>
    </div>
  );
};
export default UploadDropzone;
