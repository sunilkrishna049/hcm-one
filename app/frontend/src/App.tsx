import { useState } from 'react';
import { TopDemoBar, DEMO_USERS } from './design-system/components/TopDemoBar';
import { Footer } from './design-system/components/Footer';
import { ChatHR } from './design-system/components/chat/ChatHR';
import { ChatEMP } from './design-system/components/chat/ChatEMP';
import { api, setCurrentUserId } from './services/api';

export const SCENARIO_OPENING_MESSAGES: Record<number, string> = {
  1: "Prepare Priya Sharma's pending back-dated hike.",
  2: "Prepare Arjun Rao's pending back-dated hike.",
  3: "Prepare Kavya Iyer's pending back-dated hike.",
  4: "Prepare bonus proposal for Engineering and Sales.",
  5: "Prepare bonus proposal for Meera Nair.",
  6: "Prepare settlement proposal for Rahul Verma.",
  7: "Prepare settlement proposal for Lakshmi Reddy.",
  8: "Prepare settlement proposal for Imran Khan.",
  9: "Why is my September salary lower than August?",
  10: "Why did my TDS increase in September?",
  11: "Why did my take-home pay decrease in September when my gross did not change?",
  12: "Show me Priya Sharma's salary breakdown.",
  13: "Review settlement calculation for Imran Khan.",
};

export function App() {
  const [currentUser, setCurrentUser] = useState<string>('HR01');
  const [prefilledText, setPrefilledText] = useState<string>('');
  const [chatKey, setChatKey] = useState<number>(0);
  const [isResetting, setIsResetting] = useState(false);

  const currentUserObj = DEMO_USERS.find((u) => u.id === currentUser);
  const isHR = currentUserObj?.role === 'HR';

  const handleUserChange = (userId: string) => {
    setCurrentUser(userId);
    setCurrentUserId(userId);
    setPrefilledText('');
    setChatKey((k) => k + 1);
  };

  const handleResetDemo = async () => {
    setIsResetting(true);
    try {
      await api.resetDemo();
      setCurrentUser('HR01');
      setCurrentUserId('HR01');
      setPrefilledText('');
      setChatKey((k) => k + 1);
    } catch (e: any) {
      console.error('Reset error:', e);
    } finally {
      setIsResetting(false);
    }
  };

  const handleNewChat = () => {
    setPrefilledText('');
    setChatKey((k) => k + 1);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: 'var(--color-background)' }}>
      {/* Top Demo Bar */}
      <TopDemoBar
        currentUser={currentUser}
        onUserChange={handleUserChange}
        onResetDemo={handleResetDemo}
        isResetting={isResetting}
      />

      {/* Main Chat Workspace */}
      <main style={{ flex: 1 }}>
        {isHR ? (
          <ChatHR
            key={chatKey}
            currentUser={currentUser}
            prefilledText={prefilledText}
            onClearPrefill={() => setPrefilledText('')}
            onNewChat={handleNewChat}
          />
        ) : (
          <ChatEMP
            key={chatKey}
            currentUser={currentUser}
            prefilledText={prefilledText}
            onClearPrefill={() => setPrefilledText('')}
            onNewChat={handleNewChat}
          />
        )}
      </main>

      {/* Disclaimer Demo Footer */}
      <Footer />
    </div>
  );
}

export default App;

