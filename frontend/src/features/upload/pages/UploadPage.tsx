import React, { useState } from 'react';
import { PageLayout, Card, Button, Heading } from '@/shared/ui';
import { UploadDropzone } from '../components/UploadDropzone';
import { SelectedFiles } from '../components/SelectedFiles';
import { JobDescriptionInput } from '../components/JobDescriptionInput';
import { SkillsTagInput } from '../components/SkillsTagInput';
import { useFileValidation } from '../hooks/useFileValidation';
import { useUpload } from '../hooks/useUpload';
import { AppError } from '@/shared/api/interceptors';

export const UploadPage: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [jobDescription, setJobDescription] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  
  // Field errors
  const [jdError, setJdError] = useState<string>();
  const [skillsError, setSkillsError] = useState<string>();
  const [submitError, setSubmitError] = useState<string>();

  const { validateFiles, validationErrors, clearErrors } = useFileValidation();
  const uploadMutation = useUpload();

  const handleFilesSelected = (newFiles: File[]) => {
    clearErrors();
    setSubmitError(undefined);
    const validated = validateFiles(newFiles);
    // Append unique files
    setFiles((prev) => {
      const existingNames = prev.map(f => f.name);
      const uniqueNew = validated.filter(f => !existingNames.includes(f.name));
      return [...prev, ...uniqueNew];
    });
  };

  const handleRemoveFile = (index: number) => {
    setFiles((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setJdError(undefined);
    setSkillsError(undefined);
    setSubmitError(undefined);

    let hasError = false;

    if (files.length === 0) {
      setSubmitError('Please select at least one candidate resume PDF file to evaluate.');
      hasError = true;
    }

    if (!jobDescription.trim()) {
      setJdError('Job description details are required.');
      hasError = true;
    } else if (jobDescription.trim().length < 20) {
      setJdError('Job description details must contain at least 20 characters.');
      hasError = true;
    }

    if (hasError) return;

    uploadMutation.mutate(
      {
        files,
        jobDescription,
        jdSkills: tags,
      },
      {
        onError: (error) => {
          if (error instanceof AppError) {
            setSubmitError(error.message);
          } else {
            setSubmitError('Failed to upload files. Internal gateway failure.');
          }
        },
      }
    );
  };

  return (
    <PageLayout
      title="Evaluate Candidates"
      subtitle="Submit candidate resume PDFs for multi-agent validation against JD requirements."
    >
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px', width: '100%' }}>
        
        {/* Upload Zone Card */}
        <Card>
          <Heading level={3} style={{ fontSize: '18px', margin: 0 }}>Step 1: Upload Resume PDFs</Heading>
          <UploadDropzone onFilesSelected={handleFilesSelected} />
          
          {/* File validation errors */}
          {validationErrors.length > 0 && (
            <div style={{ padding: '12px', background: 'hsla(var(--destructive), 0.08)', border: '1px solid hsl(var(--destructive))', borderRadius: 'var(--radius)' }}>
              <span style={{ fontSize: '13px', fontWeight: 600, color: 'hsl(var(--destructive))' }}>File Verification Warnings:</span>
              <ul style={{ paddingLeft: '20px', marginTop: '6px', fontSize: '12px', color: 'hsl(var(--destructive))' }}>
                {validationErrors.map((err, idx) => (
                  <li key={idx}>{err.filename}: {err.reason}</li>
                ))}
              </ul>
            </div>
          )}

          <SelectedFiles files={files} onRemove={handleRemoveFile} />
        </Card>

        {/* Configurations Card */}
        <Card style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <Heading level={3} style={{ fontSize: '18px', margin: 0 }}>Step 2: Job Requirements</Heading>
          <JobDescriptionInput value={jobDescription} onChange={setJobDescription} error={jdError} />
          <SkillsTagInput tags={tags} onChange={setTags} error={skillsError} />
        </Card>

        {/* Global Submit Errors */}
        {submitError && (
          <div style={{ padding: '12px 16px', background: 'hsla(var(--destructive), 0.08)', border: '1px solid hsl(var(--destructive))', borderRadius: 'var(--radius)', color: 'hsl(var(--destructive))', fontSize: '13px', fontWeight: 500 }}>
            {submitError}
          </div>
        )}

        {/* Submit Actions */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
          <Button
            type="submit"
            variant="primary"
            size="lg"
            loading={uploadMutation.isPending}
            style={{ width: '200px' }}
          >
            Start Evaluation
          </Button>
        </div>

      </form>
    </PageLayout>
  );
};
export default UploadPage;
