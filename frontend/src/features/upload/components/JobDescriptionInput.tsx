import React from 'react';
import { Textarea } from '@/shared/ui';

interface JobDescriptionInputProps {
  value: string;
  onChange: (value: string) => void;
  error?: string | undefined;
}

export const JobDescriptionInput: React.FC<JobDescriptionInputProps> = ({
  value,
  onChange,
  error,
}) => {
  const maxLength = 2000;

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    if (text.length <= maxLength) {
      onChange(text);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', width: '100%' }}>
      <Textarea
        label="Target Job Description"
        placeholder="Provide the raw target job description details (e.g., Looking for a Backend Developer proficient in Python, FastAPI, and Qdrant...)"
        value={value}
        onChange={handleChange}
        error={error}
        id="job-description-textarea"
        style={{ minHeight: '140px' }}
      />
      <div style={{ display: 'flex', justifyContent: 'flex-end', fontSize: '11px', color: 'hsl(var(--muted-foreground))', marginTop: '-4px' }}>
        <span>{value.length} / {maxLength} characters</span>
      </div>
    </div>
  );
};
export default JobDescriptionInput;
