import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { MessageBubble } from '../design-system/components/MessageBubble';
import { Button } from '../design-system/components/Button';
import { getAIMessage } from '../design-system/ai_messages';
import { CheckCircle2, FileText, ArrowLeft, RefreshCw } from 'lucide-react';

interface TrackQueryProps {
  currentUser: string;
  initialQueryId?: string | null;
  onBackToUnderstand?: () => void;
}

export const TrackQuery: React.FC<TrackQueryProps> = ({
  currentUser,
  initialQueryId,
  onBackToUnderstand,
}) => {
  const [queries, setQueries] = useState<any[]>([]);
  const [selectedQueryId, setSelectedQueryId] = useState<string | null>(initialQueryId || null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const loadQueries = async () => {
    setLoading(true);
    try {
      const list = await api.listQueries();
      setQueries(list);
      if (!selectedQueryId && list.length > 0) {
        setSelectedQueryId(list[0].query_id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueries();
  }, [currentUser, initialQueryId]);

  const selectedQuery = queries.find(q => q.query_id === selectedQueryId);

  const handleDispute = async () => {
    if (!selectedQueryId) return;
    const reason = prompt("Enter the reason you are disputing this resolution:", "The medical leave was approved by manager on Sep 14.");
    if (!reason) return;
    setActionLoading(true);
    try {
      await api.disputeQuery(selectedQueryId, reason);
      alert("Dispute recorded. Query is back In review with HR.");
      loadQueries();
    } catch (err: any) {
      alert("Dispute failed: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleClose = async () => {
    if (!selectedQueryId) return;
    setActionLoading(true);
    try {
      await api.closeQuery(selectedQueryId);
      alert(getAIMessage('C24'));
      loadQueries();
    } catch (err: any) {
      alert("Failed to close query: " + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <div style={{ padding: 'var(--space-8)', textAlign: 'center' }}>Loading queries...</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', padding: 'var(--space-4)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          {onBackToUnderstand && (
            <button
              onClick={onBackToUnderstand}
              style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, display: 'flex', alignItems: 'center' }}
            >
              <ArrowLeft size={18} />
            </button>
          )}
          <h2 style={{ fontSize: '20px', fontWeight: 700, margin: 0, color: 'var(--color-text-primary)' }}>
            Track my query
          </h2>
        </div>
        <button
          onClick={loadQueries}
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', color: 'var(--color-text-secondary)' }}
          title="Refresh"
        >
          <RefreshCw size={14} />
        </button>
      </div>

      {/* Query Selector Tabs if multiple */}
      {queries.length > 1 && (
        <div style={{ display: 'flex', gap: 'var(--space-2)', overflowX: 'auto', paddingBottom: 'var(--space-1)' }}>
          {queries.map(q => (
            <button
              key={q.query_id}
              onClick={() => setSelectedQueryId(q.query_id)}
              style={{
                padding: 'var(--space-1) var(--space-3)',
                borderRadius: 'var(--radius-pill)',
                border: `1px solid ${selectedQueryId === q.query_id ? 'var(--color-brand-accent)' : 'var(--color-divider)'}`,
                backgroundColor: selectedQueryId === q.query_id ? 'var(--color-brand-tint)' : 'var(--color-surface)',
                color: selectedQueryId === q.query_id ? 'var(--color-brand-accent)' : 'var(--color-text-secondary)',
                fontSize: '12px',
                cursor: 'pointer',
                whiteSpace: 'nowrap'
              }}
            >
              {q.query_id} ({q.status})
            </button>
          ))}
        </div>
      )}

      {selectedQuery ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {/* Status Lifecycle Header */}
          <div style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-divider)',
            borderRadius: 'var(--radius-card)',
            padding: 'var(--space-4)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>
                  Query Identifier
                </div>
                <strong style={{ fontSize: 'var(--font-size-body)' }}>{selectedQuery.query_id}</strong>
              </div>
              <span style={{
                fontSize: '12px',
                fontWeight: 600,
                padding: '4px 10px',
                borderRadius: 'var(--radius-pill)',
                backgroundColor: selectedQuery.status === 'Resolved' ? 'var(--color-status-success-surface)' : 'var(--color-brand-tint)',
                color: selectedQuery.status === 'Resolved' ? 'var(--color-status-success-text)' : 'var(--color-brand-accent)',
                border: `1px solid ${selectedQuery.status === 'Resolved' ? 'var(--color-status-success-border)' : 'var(--color-brand-accent)'}`
              }}>
                {selectedQuery.status}
              </span>
            </div>

            <div style={{ marginTop: 'var(--space-3)', fontSize: '12px', color: 'var(--color-text-secondary)' }}>
              Topic: <strong>{selectedQuery.topic || selectedQuery.category}</strong> &bull; Period: <strong>{(selectedQuery.months || []).join(', ') || 'September 2026'}</strong>
            </div>
          </div>

          {/* Assistant Status Sentence (Verbatim C15, C16, C23, or C24) */}
          <MessageBubble
            author="HCM One Assistant"
            text={
              selectedQuery.status === 'Sent'
                ? getAIMessage('C15')
                : selectedQuery.status === 'In review'
                ? getAIMessage('C16')
                : selectedQuery.status === 'Resolved'
                ? getAIMessage('C23')
                : getAIMessage('C24')
            }
          />

          {/* Original Inquiry Content */}
          <div style={{
            backgroundColor: 'var(--color-background)',
            border: '1px solid var(--color-divider)',
            borderRadius: 'var(--radius-card)',
            padding: 'var(--space-4)'
          }}>
            <div style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-1)' }}>
              Your Submitted Query
            </div>
            <p style={{ margin: 0, fontSize: 'var(--font-size-body)', lineHeight: '1.4' }}>
              {selectedQuery.description}
            </p>

            {/* Attached Evidence */}
            {selectedQuery.evidence && selectedQuery.evidence.length > 0 && (
              <div style={{ marginTop: 'var(--space-3)', display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
                {selectedQuery.evidence.map((ev: any, idx: number) => (
                  <span
                    key={idx}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '2px 8px',
                      borderRadius: 'var(--radius-pill)',
                      backgroundColor: 'var(--color-surface)',
                      border: '1px solid var(--color-divider)',
                      fontSize: '11px',
                    }}
                  >
                    <FileText size={12} color="var(--color-brand-accent)" />
                    {ev.item || ev.type || ev.description}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* HR Replies / Resolution */}
          {selectedQuery.replies && selectedQuery.replies.length > 0 && (
            <div style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-divider)',
              borderRadius: 'var(--radius-card)',
              padding: 'var(--space-4)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-3)'
            }}>
              <div style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--color-text-primary)' }}>
                Recorded HR Responses
              </div>
              {selectedQuery.replies.map((r: any, idx: number) => (
                <div
                  key={idx}
                  style={{
                    padding: 'var(--space-3)',
                    backgroundColor: 'var(--color-background)',
                    borderRadius: 'var(--radius-input)',
                    borderLeft: '4px solid var(--color-brand-accent)',
                    fontSize: '13px',
                    lineHeight: '1.4'
                  }}
                >
                  <div>{r.reply_text}</div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                    By {r.author} &bull; {r.timestamp}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Actions on Resolution (Dispute or Close) */}
          {selectedQuery.status === 'Resolved' && (
            <div style={{
              padding: 'var(--space-4)',
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-divider)',
              borderRadius: 'var(--radius-card)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-3)'
            }}>
              <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                Does this resolution address your inquiry?
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
                <Button
                  variant="outline"
                  onClick={handleDispute}
                  disabled={actionLoading}
                >
                  Dispute Resolution
                </Button>
                <Button
                  variant="primary"
                  onClick={handleClose}
                  disabled={actionLoading}
                >
                  <CheckCircle2 size={16} /> Acknowledge & Close
                </Button>
              </div>
            </div>
          )}

          {selectedQuery.status === 'Closed' && (
            <div style={{
              padding: 'var(--space-3)',
              backgroundColor: 'var(--color-surface)',
              borderRadius: 'var(--radius-card)',
              textAlign: 'center',
              fontSize: '12px',
              color: 'var(--color-text-secondary)'
            }}>
              {getAIMessage('C24')}
            </div>
          )}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: 'var(--space-8)', color: 'var(--color-text-secondary)' }}>
          No queries found for this employee account.
        </div>
      )}
    </div>
  );
};
