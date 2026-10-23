import { useState } from 'react';
import { TopDemoBar, SCENARIOS, DEMO_USERS } from './design-system/components/TopDemoBar';
import { Footer } from './design-system/components/Footer';
import { api, setCurrentUserId } from './services/api';

// Screens
import { PrepareProposal } from './screens/PrepareProposal';
import { ReviewProposal } from './screens/ReviewProposal';
import { ReviewQuery } from './screens/ReviewQuery';
import { UnderstandPayroll } from './screens/UnderstandPayroll';
import { ReviewQueryDraft } from './screens/ReviewQueryDraft';
import { TrackQuery } from './screens/TrackQuery';

export type ScreenId =
  | 'prepare-proposal'
  | 'review-proposal'
  | 'review-queries'
  | 'understand-payroll'
  | 'review-query-draft'
  | 'track-query';

export function App() {
  const [currentUser, setCurrentUser] = useState<string>('HR01');
  const [currentScenario, setCurrentScenario] = useState<number>(1);
  const [activeScreen, setActiveScreen] = useState<ScreenId>('review-proposal');
  const [proposalMode, setProposalMode] = useState<'hike' | 'bonus' | 'settlement'>('hike');
  const [selectedEmployee, setSelectedEmployee] = useState<string>('E01');
  const [pendingDraft, setPendingDraft] = useState<any>(null);
  const [trackedQueryId, setTrackedQueryId] = useState<string | null>(null);
  const [isResetting, setIsResetting] = useState(false);

  const currentUserObj = DEMO_USERS.find(u => u.id === currentUser);
  const isHR = currentUserObj?.role === 'HR';

  // Sync API user on user change
  const handleUserChange = (userId: string) => {
    setCurrentUser(userId);
    setCurrentUserId(userId);

    const userObj = DEMO_USERS.find(u => u.id === userId);
    if (userObj?.role === 'Employee') {
      if (['prepare-proposal', 'review-proposal', 'review-queries'].includes(activeScreen)) {
        setActiveScreen('understand-payroll');
      }
    } else {
      if (['understand-payroll', 'review-query-draft', 'track-query'].includes(activeScreen)) {
        setActiveScreen('review-proposal');
      }
    }
  };

  // Sync state on scenario change (Automatic login per scenario)
  const handleScenarioChange = (scenarioNum: number) => {
    setCurrentScenario(scenarioNum);
    const scenarioMeta = SCENARIOS.find(s => s.id === scenarioNum);
    const targetUser = scenarioMeta?.defaultUser || 'HR01';
    setCurrentUser(targetUser);
    setCurrentUserId(targetUser);

    if (scenarioNum === 1) {
      setActiveScreen('review-proposal');
      setProposalMode('hike');
      setSelectedEmployee('E01');
    } else if (scenarioNum === 2) {
      setActiveScreen('review-proposal');
      setProposalMode('hike');
      setSelectedEmployee('E02');
    } else if (scenarioNum === 3) {
      setActiveScreen('review-proposal');
      setProposalMode('hike');
      setSelectedEmployee('E03');
    } else if (scenarioNum === 4) {
      setActiveScreen('review-proposal');
      setProposalMode('bonus');
      setSelectedEmployee('E01');
    } else if (scenarioNum === 5) {
      setActiveScreen('review-proposal');
      setProposalMode('bonus');
      setSelectedEmployee('E09');
    } else if (scenarioNum === 6) {
      setActiveScreen('review-proposal');
      setProposalMode('settlement');
      setSelectedEmployee('E10');
    } else if (scenarioNum === 7) {
      setActiveScreen('review-proposal');
      setProposalMode('settlement');
      setSelectedEmployee('E11');
    } else if (scenarioNum === 8) {
      setActiveScreen('review-proposal');
      setProposalMode('settlement');
      setSelectedEmployee('E12');
    } else if (scenarioNum === 9) {
      setActiveScreen('understand-payroll');
      setSelectedEmployee('E05');
    } else if (scenarioNum === 10) {
      setActiveScreen('understand-payroll');
      setSelectedEmployee('E06');
    } else if (scenarioNum === 11) {
      setActiveScreen('understand-payroll');
      setSelectedEmployee('E16');
    } else if (scenarioNum === 12) {
      setActiveScreen('understand-payroll');
      setSelectedEmployee('E01');
    } else if (scenarioNum === 13) {
      setActiveScreen('review-proposal');
      setProposalMode('settlement');
      setSelectedEmployee('E12');
    }
  };

  const handleResetDemo = async () => {
    setIsResetting(true);
    try {
      await api.resetDemo();
      handleScenarioChange(1);
    } catch (e: any) {
      console.error("Reset error:", e);
    } finally {
      setIsResetting(false);
    }
  };

  const isMobileScreen = ['understand-payroll', 'review-query-draft', 'track-query'].includes(activeScreen);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: '#F8FAFC' }}>
      {/* Top Demo Controller Bar */}
      <TopDemoBar
        currentUser={currentUser}
        onUserChange={handleUserChange}
        currentScenario={currentScenario}
        onScenarioChange={handleScenarioChange}
        onResetDemo={handleResetDemo}
        isResetting={isResetting}
      />

      {/* Screen Navigation Tabs - Role-based navigation */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid var(--color-divider)',
        padding: 'var(--space-2) var(--space-6)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          {isHR ? (
            <>
              {/* HR Only Navigation Tabs */}
              <button
                className={`hcm-nav-tab ${activeScreen === 'prepare-proposal' ? 'active' : ''}`}
                onClick={() => setActiveScreen('prepare-proposal')}
              >
                Prepare a proposal
              </button>
              <button
                className={`hcm-nav-tab ${activeScreen === 'review-proposal' ? 'active' : ''}`}
                onClick={() => setActiveScreen('review-proposal')}
              >
                Review proposal
              </button>
              <button
                className={`hcm-nav-tab ${activeScreen === 'review-queries' ? 'active' : ''}`}
                onClick={() => setActiveScreen('review-queries')}
              >
                Review queries
              </button>
            </>
          ) : (
            <>
              {/* Employee Only Navigation Tabs */}
              <button
                className={`hcm-nav-tab ${activeScreen === 'understand-payroll' ? 'active' : ''}`}
                onClick={() => setActiveScreen('understand-payroll')}
              >
                Understand my payroll
              </button>
              <button
                className={`hcm-nav-tab ${activeScreen === 'review-query-draft' ? 'active' : ''}`}
                onClick={() => setActiveScreen('review-query-draft')}
              >
                Review my query draft
              </button>
              <button
                className={`hcm-nav-tab ${activeScreen === 'track-query' ? 'active' : ''}`}
                onClick={() => setActiveScreen('track-query')}
              >
                Track my query
              </button>
            </>
          )}
        </div>

        <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
          View: <strong>{isMobileScreen ? 'Mobile Frame (390px)' : 'Desktop Workspace (1440px)'}</strong>
        </div>
      </div>

      {/* Main Screen Content */}
      <main style={{ flex: 1 }}>
        {isMobileScreen ? (
          /* Mobile 390px Viewport Frame */
          <div className="mobile-frame-wrapper">
            <div className="mobile-frame">
              <div className="mobile-notch" />
              <div className="mobile-screen-content">
                {activeScreen === 'understand-payroll' && (
                  <UnderstandPayroll
                    currentUser={currentUser}
                    scenarioNum={currentScenario}
                    onNavigateToDraftQuery={(draft) => {
                      setPendingDraft(draft);
                      setActiveScreen('review-query-draft');
                    }}
                    onNavigateToTrackQuery={() => setActiveScreen('track-query')}
                  />
                )}

                {activeScreen === 'review-query-draft' && (
                  <ReviewQueryDraft
                    currentUser={currentUser}
                    initialDraftData={pendingDraft}
                    onQuerySubmitted={(queryId) => {
                      setTrackedQueryId(queryId);
                      setActiveScreen('track-query');
                    }}
                    onCancel={() => setActiveScreen('understand-payroll')}
                  />
                )}

                {activeScreen === 'track-query' && (
                  <TrackQuery
                    currentUser={currentUser}
                    initialQueryId={trackedQueryId}
                    onBackToUnderstand={() => setActiveScreen('understand-payroll')}
                  />
                )}
              </div>
            </div>
          </div>
        ) : (
          /* Desktop 1440px Viewport */
          <div className="desktop-app-container">
            {activeScreen === 'prepare-proposal' && (
              <PrepareProposal
                currentUser={currentUser}
                onProceedToReview={(mode, eid) => {
                  setProposalMode(mode);
                  if (eid) setSelectedEmployee(eid);
                  setActiveScreen('review-proposal');
                }}
              />
            )}

            {activeScreen === 'review-proposal' && (
              <ReviewProposal
                scenarioNum={currentScenario}
                mode={proposalMode}
                employeeId={selectedEmployee}
                currentUser={currentUser}
              />
            )}

            {activeScreen === 'review-queries' && (
              <ReviewQuery
                currentUser={currentUser}
                onBackToProposals={() => setActiveScreen('review-proposal')}
              />
            )}
          </div>
        )}
      </main>

      {/* Mandatory Demo Disclaimer Footer */}
      <Footer />
    </div>
  );
}

export default App;
