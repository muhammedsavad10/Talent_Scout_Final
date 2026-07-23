import React from 'react';
import { PageLayout, Card, Heading, Text } from '@/shared/ui';

export const SettingsPage: React.FC = () => {
  return (
    <PageLayout
      title="Settings"
      subtitle="Recruiter policies thresholds, weights parameters, and third-party API configurations."
    >
      <Card>
        <Heading level={3}>Configuration Interface</Heading>
        <Text variant="muted">Manage Jaccard/weighted thresholds and mandatory gate policies.</Text>
      </Card>
    </PageLayout>
  );
};
export default SettingsPage;
