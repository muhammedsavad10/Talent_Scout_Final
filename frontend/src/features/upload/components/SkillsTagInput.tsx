import React, { useState } from 'react';
import { X } from 'lucide-react';
import { Text } from '@/shared/ui';

interface SkillsTagInputProps {
  tags: string[];
  onChange: (tags: string[]) => void;
  error?: string | undefined;
}

export const SkillsTagInput: React.FC<SkillsTagInputProps> = ({
  tags,
  onChange,
  error,
}) => {
  const [inputValue, setInputValue] = useState('');

  const commitInput = (value: string) => {
    const cleaned = value.trim().replace(/,$/, '');
    if (cleaned && !tags.includes(cleaned)) {
      onChange([...tags, cleaned]);
      setInputValue('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      commitInput(inputValue);
    } else if (e.key === 'Backspace' && !inputValue && tags.length > 0) {
      onChange(tags.slice(0, -1));
    }
  };

  const handleBlur = () => {
    commitInput(inputValue);
  };

  const removeTag = (tagToRemove: string) => {
    onChange(tags.filter((tag) => tag !== tagToRemove));
  };

  return (
    <div className="form-group" style={{ width: '100%' }}>
      <label className="form-label" htmlFor="skills-chip-input">Tracked Mandatory Skills</label>
      
      {/* Tags Wrapper */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '8px',
          padding: '8px 12px',
          background: 'hsl(var(--secondary))',
          border: '1px solid',
          borderColor: error ? 'hsl(var(--destructive))' : 'hsl(var(--border))',
          borderRadius: 'var(--radius)',
          minHeight: '44px',
          alignItems: 'center',
        }}
      >
        {tags.map((tag) => (
          <span
            key={tag}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 10px',
              borderRadius: '16px',
              background: 'hsla(var(--primary), 0.12)',
              border: '1px solid hsla(var(--primary), 0.3)',
              color: 'hsl(var(--foreground))',
              fontSize: '12px',
              fontWeight: 500,
            }}
          >
            {tag}
            <button
              type="button"
              onClick={() => removeTag(tag)}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'hsl(var(--muted-foreground))',
                cursor: 'pointer',
                display: 'flex',
                padding: '1px',
                borderRadius: '50%',
              }}
              aria-label={`Remove skill tag ${tag}`}
            >
              <X size={12} />
            </button>
          </span>
        ))}
        
        <input
          id="skills-chip-input"
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          placeholder={tags.length === 0 ? "Type skill and press Enter (e.g. Python, FastAPI)..." : ""}
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: '#ffffff',
            fontSize: '14px',
            minWidth: '150px',
            padding: '4px 0',
          }}
        />
      </div>
      
      {error && <span style={{ color: 'hsl(var(--destructive))', fontSize: '12px', marginTop: '4px' }}>{error}</span>}
      <Text variant="muted" style={{ fontSize: '11px', marginTop: '2px' }}>
        Press Enter, comma (,), or click away to add chip tags.
      </Text>
    </div>
  );
};
export default SkillsTagInput;
