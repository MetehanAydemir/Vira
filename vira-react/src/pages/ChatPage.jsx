import React, { useContext } from 'react';
import { ChatProvider } from '../contexts/ChatContext';
import ChatHeader from '../components/Chat/ChatHeader';
import ChatArea from '../components/Chat/ChatArea';
import ChatInput from '../components/Chat/ChatInput';
import MemoryContext from '../components/Chat/MemoryContext';
import Sidebar from '../components/UI/Sidebar';
import { AuthContext } from '../contexts/AuthContext';
import '../styles/chat.css';

const ChatPage = () => {
  const { user, logout } = useContext(AuthContext);
  
  return (
    <ChatProvider>
      <div className="chat-page">
        <ChatHeader username={user?.username} onLogout={logout} />
        
        <div className="chat-layout">
          <div className="chat-main">
            <ChatArea />
            <MemoryContext />
            <ChatInput />
          </div>
          <Sidebar />
        </div>
      </div>
    </ChatProvider>
  );
};

export default ChatPage;