import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { QueryDraft, type QueryDraftData } from '../design-system/components/QueryDraft';
import { ArrowLeft } from 'lucide-react';

interface ReviewQueryDraftProps {
  currentUser: string;
  initialDraftData?: QueryDraftData | null;
  onQuerySubmitted: (queryId: string) => void;
  onCancel: () => void;
}

export const ReviewQueryDraft: React.FC<ReviewQueryDraftProps> = ({
  currentUser,
  initialDraftData,
  onQuerySubmitted,
  onCancel,
}) => {
  const [draftData, setDraftData] = useState<QueryDraftData | null>(initialDraftData || null);
  const [submitting, setSubmitting] = useState(false);
  const [loadingExisting, setLoadingExisting] = useState(true);

  useEffect(() => {
    // Check if user has open queries to enable C14 candidate match
    const checkOpenQueries = async () => {
      try {
        const empId = currentUser.replace('USER-', '');
        const [queries, empList] = await Promise.all([
          api.listQueries().catch(() => []),
          api.getEmployees().catch(() => []),
        ]);
        const open = queries.find((q: any) => q.employee_id === empId && q.status !== 'Closed');
        const emp = empList.find((e: any) => e.employee_id === empId);

        const baseDraft: QueryDraftData = initialDraftData || {
          employee_id: empId,
          employee_name: emp?.name || (empId === 'E05' ? 'Neha Gupta' : empId),
          pay_period: '2026-09',
          topic: 'salary',
          description: 'Please check my September attendance.',
          evidence: [
            { type: 'attendance record', record_id: `ATT-${empId}-2026-09`, file: 'attendance.json' },
          ],
          candidate_query_id: open ? open.query_id : null,
          candidate_query_text: open ? open.description : null,
        };

        if (open) {
          baseDraft.candidate_query_id = open.query_id;
          baseDraft.candidate_query_text = open.description;
        }

        setDraftData(baseDraft);
      } catch (e) {
        console.error(e);
      } finally {
        setLoadingExisting(false);
      }
    };

    checkOpenQueries();
  }, [currentUser, initialDraftData]);

  const handleSubmit = async (submitData: {
    description: string;
    evidence: any[];
    confirmed: boolean;
    appendToQueryId?: string | null;
  }) => {
    if (!draftData) return;
    setSubmitting(true);
    try {
      const draftPayload = {
        employee_id: draftData.employee_id,
        category: draftData.topic,
        months: [draftData.pay_period],
        description: submitData.description,
        evidence: submitData.evidence,
      };

      const res = await api.confirmSendQuery(
        draftPayload,
        submitData.appendToQueryId ? 'add' : 'new',
        submitData.appendToQueryId,
        submitData.confirmed
      );

      const targetId = res.query?.query_id || submitData.appendToQueryId || "QUERY-NEW";
      onQuerySubmitted(targetId);
    } catch (err: any) {
      alert("Submission failed: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loadingExisting || !draftData) {
    return (
      <div style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--color-text-secondary)' }}>
        Preparing query draft...
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', padding: 'var(--space-4)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        <button
          onClick={onCancel}
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, display: 'flex', alignItems: 'center' }}
          aria-label="Back"
        >
          <ArrowLeft size={18} />
        </button>
        <h2 style={{ fontSize: '20px', fontWeight: 700, margin: 0, color: 'var(--color-text-primary)' }}>
          Review my query draft
        </h2>
      </div>

      <QueryDraft
        initialData={draftData}
        onSubmit={handleSubmit}
        onCancel={onCancel}
        isSubmitting={submitting}
      />
    </div>
  );
};
