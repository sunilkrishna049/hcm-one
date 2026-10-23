import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Button } from '../design-system/components/Button';
import { Textarea } from '../design-system/components/Input';
import { getAIMessage } from '../design-system/ai_messages';
import { CheckCircle2, FileText, ArrowLeft } from 'lucide-react';

interface ReviewQueryProps {
  currentUser: string;
  onBackToProposals?: () => void;
}

export const ReviewQuery: React.FC<ReviewQueryProps> = ({
  currentUser,
  onBackToProposals,
}) => {
  const [queries, setQueries] = useState<any[]>([]);
  const [selectedQueryId, setSelectedQueryId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [replyText, setReplyText] = useState("");
  const [actionLoading, setActionLoading] = useState(false);

  const loadQueries = async () => {
    setLoading(true);
    try {
      const list = await api.listQueries();
      setQueries(list);
      if (list.length > 0 && !selectedQueryId) {
        setSelectedQueryId(list[0].query_id);
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueries();
  }, [currentUser]);

  const selectedQuery = queries.find(q => q.query_id === selectedQueryId);

  const handleTakeIntoReview = async () => {
    if (!selectedQueryId) return;
    setActionLoading(true);
    try {
      await api.takeIntoReview(selectedQueryId);
      loadQueries();
    } catch (e: any) {
      alert("Error: " + e.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReply = async () => {
    if (!selectedQueryId || !replyText.trim()) return;
    setActionLoading(true);
    try {
      await api.replyQuery(selectedQueryId, replyText);
      setReplyText("");
      loadQueries();
    } catch (e: any) {
      alert("Error: " + e.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleResolve = async () => {
    if (!selectedQueryId) return;
    setActionLoading(true);
    try {
      await api.resolveQuery(selectedQueryId, replyText.trim() ? replyText : undefined);
      setReplyText("");
      loadQueries();
      alert("Query marked as Resolved! " + getAIMessage('C23'));
    } catch (e: any) {
      alert("Error: " + e.message);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <div style={{ padding: 'var(--space-8)', textAlign: 'center' }}>Loading employee queries...</div>;
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: 700, margin: 0, color: 'var(--color-text-primary)', letterSpacing: '-0.02em' }}>
            Review queries
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--space-1)', fontSize: '15px' }}>
            HR resolution desk for employee payroll and tax queries.
          </p>
        </div>
        {onBackToProposals && (
          <Button variant="secondary" onClick={onBackToProposals}>
            <ArrowLeft size={16} /> Back to Proposals
          </Button>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 'var(--space-6)', minHeight: '600px' }}>
        {/* Left: Queries List */}
        <div style={{
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-divider)',
          borderRadius: 'var(--radius-card)',
          padding: 'var(--space-4)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-3)'
        }}>
          <div style={{ fontWeight: 'var(--font-weight-semibold)', fontSize: 'var(--font-size-label)' }}>
            Open / Tracked Queries ({queries.length})
          </div>

          {queries.length === 0 ? (
            <div style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-small)' }}>
              No employee queries recorded yet.
            </div>
          ) : (
            queries.map(q => {
              const isSelected = q.query_id === selectedQueryId;
              let statusBadgeColor = '#64748B';
              if (q.status === 'Sent') statusBadgeColor = '#0F766E';
              if (q.status === 'In review') statusBadgeColor = '#D97706';
              if (q.status === 'Resolved') statusBadgeColor = '#16A34A';
              if (q.status === 'Closed') statusBadgeColor = '#64748B';

              return (
                <div
                  key={q.query_id}
                  onClick={() => setSelectedQueryId(q.query_id)}
                  style={{
                    padding: 'var(--space-3)',
                    borderRadius: 'var(--radius-input)',
                    backgroundColor: isSelected ? 'var(--color-background)' : 'transparent',
                    border: `1px solid ${isSelected ? 'var(--color-brand-accent)' : 'var(--color-divider)'}`,
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 'var(--space-1)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong style={{ fontSize: 'var(--font-size-table)' }}>{q.query_id}</strong>
                    <span style={{
                      fontSize: '11px',
                      fontWeight: 600,
                      color: statusBadgeColor,
                      padding: '1px 6px',
                      backgroundColor: 'rgba(0,0,0,0.04)',
                      borderRadius: 'var(--radius-pill)'
                    }}>
                      {q.status}
                    </span>
                  </div>
                  <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-secondary)' }}>
                    Emp: {q.employee_id} &bull; {q.topic || q.category}
                  </div>
                  <div style={{
                    fontSize: 'var(--font-size-small)',
                    color: 'var(--color-text-primary)',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    {q.description}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right: Selected Query Detail */}
        {selectedQuery ? (
          <div style={{
            backgroundColor: 'var(--color-background)',
            border: '1px solid var(--color-divider)',
            borderRadius: 'var(--radius-card)',
            padding: 'var(--space-6)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-4)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                  <h2 style={{ fontSize: 'var(--font-size-subtitle)', fontWeight: 'var(--font-weight-semibold)', margin: 0 }}>
                    {selectedQuery.query_id} &mdash; {selectedQuery.topic || selectedQuery.category}
                  </h2>
                  <span style={{
                    fontSize: '12px',
                    fontWeight: 600,
                    padding: '2px 8px',
                    backgroundColor: 'var(--color-surface)',
                    border: '1px solid var(--color-divider)',
                    borderRadius: 'var(--radius-pill)'
                  }}>
                    Status: {selectedQuery.status}
                  </span>
                </div>
                <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                  Submitted by Employee: <strong>{selectedQuery.employee_id}</strong> &bull; Periods: <strong>{(selectedQuery.months || []).join(', ') || 'Current cycle'}</strong>
                </div>
              </div>

              {selectedQuery.status === 'Sent' && (
                <Button variant="primary" onClick={handleTakeIntoReview} disabled={actionLoading}>
                  Take into Review
                </Button>
              )}
            </div>


            {/* Description */}
            <div style={{
              backgroundColor: 'var(--color-surface)',
              padding: 'var(--space-4)',
              borderRadius: 'var(--radius-input)',
              border: '1px solid var(--color-divider)'
            }}>
              <div style={{ fontSize: 'var(--font-size-label)', fontWeight: 'var(--font-weight-medium)', color: 'var(--color-text-secondary)' }}>
                Employee Inquiry
              </div>
              <p style={{ marginTop: 'var(--space-2)', fontSize: 'var(--font-size-body)', lineHeight: '1.5' }}>
                {selectedQuery.description}
              </p>
            </div>

            {/* Attached Evidence Items */}
            <div>
              <div style={{ fontSize: 'var(--font-size-label)', fontWeight: 'var(--font-weight-semibold)', marginBottom: 'var(--space-2)' }}>
                Attached Evidence Items ({selectedQuery.evidence?.length || 0})
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
                {(selectedQuery.evidence || []).map((ev: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 'var(--space-2)',
                      padding: 'var(--space-2) var(--space-3)',
                      backgroundColor: 'var(--color-surface)',
                      border: '1px solid var(--color-border-subtle)',
                      borderRadius: 'var(--radius-pill)',
                      fontSize: 'var(--font-size-small)',
                    }}
                  >
                    <FileText size={14} color="var(--color-brand-accent)" />
                    <span>{ev.item || ev.type || ev.description || JSON.stringify(ev)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Existing HR Replies */}
            {selectedQuery.replies && selectedQuery.replies.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                <div style={{ fontSize: 'var(--font-size-label)', fontWeight: 'var(--font-weight-semibold)' }}>
                  Recorded HR Responses
                </div>
                {selectedQuery.replies.map((r: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      padding: 'var(--space-3)',
                      backgroundColor: 'var(--color-surface)',
                      borderRadius: 'var(--radius-input)',
                      borderLeft: '4px solid var(--color-brand-accent)',
                      fontSize: 'var(--font-size-body)'
                    }}
                  >
                    <div>{r.reply_text}</div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                      By {r.author} at {r.timestamp}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* HR Reply & Resolve Form (only if not closed) */}
            {selectedQuery.status !== 'Closed' && (
              <div style={{ marginTop: 'auto', paddingTop: 'var(--space-4)', borderTop: '1px solid var(--color-divider)' }}>
                <label className="hcm-form-label" htmlFor="hr-reply">
                  Record HR Response / Resolution
                </label>
                <Textarea
                  id="hr-reply"
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  placeholder="Enter clarification or policy explanation for employee..."
                  rows={3}
                />
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)', marginTop: 'var(--space-3)' }}>
                  <Button
                    variant="secondary"
                    onClick={handleReply}
                    disabled={!replyText.trim() || actionLoading}
                  >
                    Add Reply Only
                  </Button>
                  <Button
                    variant="primary"
                    onClick={handleResolve}
                    disabled={actionLoading}
                  >
                    <CheckCircle2 size={16} /> Resolve Query (C23)
                  </Button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-secondary)' }}>
            Select a query from the left to view details.
          </div>
        )}
      </div>
    </div>
  );
};
