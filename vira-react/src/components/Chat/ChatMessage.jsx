import React, { useState, useEffect, useRef, useLayoutEffect } from 'react';
import { MathJaxContext } from 'better-react-mathjax';
import { Chart, registerables } from 'chart.js';
import 'leaflet/dist/leaflet.css';

// Yerel modüller
import { processContent, LATEX_REGEX } from './messageUtils';
import {
  ToolCallsRenderer,
  CodeBlocksRenderer,
  ChartsRenderer,
  MapsRenderer,
  LatexRenderer,
  VersionsRenderer
} from './messageRenderers';
import MemoryContext from './MemoryContext'; // MemoryContext bileşenini import ediyorum

// Chart.js için gerekli bileşenleri kaydet
Chart.register(...registerables);

const ChatMessage = ({ message, isLastMessage = false, isTyping = false, apiStatus }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showFullContent, setShowFullContent] = useState(false);
  const [copiedToClipboard, setCopiedToClipboard] = useState(false);
  const [contentOverflows, setContentOverflows] = useState(false); // Yeni durum değişkeni
  const contentRef = useRef(null);
  const MAX_HEIGHT = 300; // Otomatik kısaltma için maksimum yükseklik

  // Mesaj içeriğini işle
  const processedContent = message.content ? processContent(message.content) : { html: "İçerik yüklenemedi.", charts: [], maps: [], codeBlocks: [] };

  // İçerik yüksekliğini kontrol et - useLayoutEffect kullanarak DOM ölçümlerini daha erken yap
  useLayoutEffect(() => {
    // İçerik referansı tanımlıysa ve içerik varsa
    if (contentRef.current) {
      const scrollHeight = contentRef.current.scrollHeight;
      // İçerik MAX_HEIGHT'tan yüksekse, taşma durumunu true yap
      setContentOverflows(scrollHeight > MAX_HEIGHT);
      // İçeriği başlangıçta kısalt veya göster
      setShowFullContent(scrollHeight <= MAX_HEIGHT);
    }
  }, [message.content, processedContent.html]);

  // Kopyalama işlevi
  const handleCopy = () => {
    if (message.content) {
      navigator.clipboard.writeText(message.content)
        .then(() => {
          setCopiedToClipboard(true);
          setTimeout(() => setCopiedToClipboard(false), 2000);
        })
        .catch(err => {
          console.error('Kopyalama başarısız oldu:', err);
        });
    }
  };

  return (
    <MathJaxContext>
      <div className={`message ${message.role}`}>
        <div className="message-avatar">
          <div className="emoji-avatar">
            {message.role === 'user' ? '👤' : '🤖'}
          </div>
        </div>

        <div className="message-content">
          {/* Mesaj işleniyor durumu */}
          {message.status === 'processing' && (
            <div className="message-status processing">
              <span className="status-emoji">⚙️</span>
              <span className="status-text">İşleniyor...</span>
            </div>
          )}

          {/* Araç çağrısı durumu */}
          <ToolCallsRenderer toolCalls={message.toolCalls} />

          {/* Ana içerik */}
          <div
            ref={contentRef}
            className={`message-main-content ${!showFullContent ? 'collapsed' : ''}`}
            style={!showFullContent ? { maxHeight: `${MAX_HEIGHT}px` } : {}}
            dangerouslySetInnerHTML={{ __html: processedContent.html }}
          />

          {/* Devamını Oku / Daha Az Göster butonu - contentOverflows durumunu kullan */}
          {contentOverflows && (
            <button
              className="read-more-button"
              onClick={() => setShowFullContent(!showFullContent)}
            >
              {showFullContent ? 'Daha az göster' : 'Devamını oku'}
            </button>
          )}

          {/* Kod blokları */}
          {processedContent.codeBlocks && processedContent.codeBlocks.length > 0 && (
            <div className="code-blocks-container">
              <CodeBlocksRenderer codeBlocks={processedContent.codeBlocks} />
            </div>
          )}

          {/* Grafikler */}
          {processedContent.charts && processedContent.charts.length > 0 && (
            <div className="charts-container">
              <ChartsRenderer charts={processedContent.charts} />
            </div>
          )}

          {/* Haritalar */}
          {processedContent.maps && processedContent.maps.length > 0 && (
            <div className="maps-container">
              <MapsRenderer maps={processedContent.maps} />
            </div>
          )}

          {/* LaTeX formülleri için MathJax desteği */}
          <LatexRenderer content={message.content} />

          {/* Mesaj versiyonları varsa */}
          <VersionsRenderer
            versions={message.versions}
            isExpanded={isExpanded}
            setIsExpanded={setIsExpanded}
          />

          {/* Hafıza bağlamı - MemoryContext bileşeni artık doğru şekilde kullanılıyor */}
          {message.role === 'assistant' && message.memoryContext && (
            <div className="message-memory-context">
              <MemoryContext memoryContext={message.memoryContext} />
            </div>
          )}

          {/* Yazıyor göstergesi */}
          {isTyping && (
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}

          {/* Zaman damgası */}
          <div className="message-timestamp">
            {message.timestamp || new Date().toLocaleTimeString()}
          </div>

          {/* Mesaj aksiyonları */}
          <div className="message-actions">
            <button
              className="action-button copy-button"
              title={copiedToClipboard ? "Kopyalandı!" : "Kopyala"}
              onClick={handleCopy}
            >
              {copiedToClipboard ? "✓" : "📋"}
            </button>
            <button className="action-button like-button" title="Beğen">
              👍
            </button>
            <button className="action-button dislike-button" title="Beğenme">
              👎
            </button>
          </div>
        </div>
      </div>
    </MathJaxContext>
  );
};

export default ChatMessage;