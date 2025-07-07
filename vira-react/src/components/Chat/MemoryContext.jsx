import React, { useState } from 'react';

const MemoryContext = ({ memoryContext }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!memoryContext) {
    return null;
  }

  const toggleExpansion = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="memory-context">
      <h3 onClick={toggleExpansion} style={{ cursor: 'pointer', userSelect: 'none' }}>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
          <path d="M6.5 6a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3z"/>
          <path d="M5.5.5a.5.5 0 0 0-1 0V2A2.5 2.5 0 0 0 2 4.5H.5a.5.5 0 0 0 0 1H2v1H.5a.5.5 0 0 0 0 1H2v1H.5a.5.5 0 0 0 0 1H2v1H.5a.5.5 0 0 0 0 1H2A2.5 2.5 0 0 0 4.5 14v1.5a.5.5 0 0 0 1 0V14h1v1.5a.5.5 0 0 0 1 0V14h1v1.5a.5.5 0 0 0 1 0V14h1v1.5a.5.5 0 0 0 1 0V14a2.5 2.5 0 0 0 2.5-2.5h1.5a.5.5 0 0 0 0-1H14v-1h1.5a.5.5 0 0 0 0-1H14v-1h1.5a.5.5 0 0 0 0-1H14v-1h1.5a.5.5 0 0 0 0-1H14A2.5 2.5 0 0 0 11.5 2V.5a.5.5 0 0 0-1 0V2h-1V.5a.5.5 0 0 0-1 0V2h-1V.5a.5.5 0 0 0-1 0V2h-1V.5zm1 4.5A1.5 1.5 0 0 1 6.5 6h3A1.5 1.5 0 0 1 11 7.5v3A1.5 1.5 0 0 1 9.5 12h-3A1.5 1.5 0 0 1 5 10.5v-3z"/>
        </svg>
        Hafıza Bağlamı
        <span className="expansion-indicator">{isExpanded ? '[-]' : '[+]'}</span>
      </h3>
      {isExpanded && (
        <div className="memory-formatted" dangerouslySetInnerHTML={{ __html: formatMemoryContext(memoryContext) }} />
      )}
    </div>
  );
};

// Hafıza metnini HTML formatına dönüştür
const formatMemoryContext = (memoryText) => {
  if (!memoryText) return '';
  
  let html = '';
  
  // Satırları işle
  const lines = memoryText.split('\n');
  for (const line of lines) {
    if (line.trim()) {
      html += `<p>${line}</p>`;
    }
  }
  
  return html;
};

export default MemoryContext;