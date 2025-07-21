import React from 'react';
import { marked } from 'marked'; // ⚠️ Bu import eksikti
import DOMPurify from 'dompurify'; // ⚠️ HTML güvenliği için bu da gerekli
import { Line, Bar, Pie } from 'react-chartjs-2';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import { MathJax } from 'better-react-mathjax';
import { LATEX_REGEX } from './messageUtils';

// Araç çağrılarını render et
export const ToolCallsRenderer = ({ toolCalls }) => {
  if (!toolCalls) return null;

  return (
    <div className="tool-calls">
      {toolCalls.map((tool, index) => (
        <div key={index} className="tool-call">
          <div className="tool-header">
            <span className="tool-emoji">🔧</span>
            <span className="tool-name">{tool.name || "Araç Çağrısı"}</span>
          </div>
          <div className="tool-arguments">
            {Object.entries(tool.arguments || {}).map(([key, value], i) => (
              <div key={i} className="tool-argument">
                <span className="argument-name">{key}:</span>
                <span className="argument-value">{typeof value === 'object' ? JSON.stringify(value) : value}</span>
              </div>
            ))}
          </div>
          {tool.result && (
            <div className="tool-result">
              <div className="result-header">Sonuç:</div>
              <div className="result-content">
                {typeof tool.result === "object"
                  ? <pre>{JSON.stringify(tool.result, null, 2)}</pre>
                  : tool.result}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

// Kod bloklarını render et
export const CodeBlocksRenderer = ({ codeBlocks }) => {
  if (!codeBlocks || codeBlocks.length === 0) return null;

  return codeBlocks.map(block => (
    <div key={block.id} className="syntax-highlighter-container">
      <div className="code-header">
        <span className="code-language">{block.language}</span>
        <button
          className="copy-code-button"
          onClick={() => {
            navigator.clipboard.writeText(block.code);
            alert('Kod kopyalandı!');
          }}
        >
          📋 Kopyala
        </button>
      </div>
      <SyntaxHighlighter language={block.language} style={docco}>
        {block.code}
      </SyntaxHighlighter>
    </div>
  ));
};

// Grafikleri render et
export const ChartsRenderer = ({ charts }) => {
  if (!charts || charts.length === 0) return null;

  return charts.map(chart => {
    const chartData = {
      labels: chart.data.labels,
      datasets: chart.data.datasets
    };

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: chart.data.title || 'Grafik'
        }
      }
    };

    switch (chart.type.toLowerCase()) {
      case 'line':
        return <Line key={chart.id} data={chartData} options={chartOptions} />;
      case 'bar':
        return <Bar key={chart.id} data={chartData} options={chartOptions} />;
      case 'pie':
        return <Pie key={chart.id} data={chartData} options={chartOptions} />;
      default:
        return <div key={chart.id}>Desteklenmeyen grafik türü: {chart.type}</div>;
    }
  });
};

// Haritaları render et
export const MapsRenderer = ({ maps }) => {
  if (!maps || maps.length === 0) return null;

  return maps.map(map => (
    <div key={map.id} className="map-container">
      <MapContainer center={[map.lat, map.lng]} zoom={13} style={{ height: '300px', width: '100%' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <Marker position={[map.lat, map.lng]}>
          <Popup>{map.title}</Popup>
        </Marker>
      </MapContainer>
    </div>
  ));
};

// LaTeX formüllerini render et
export const LatexRenderer = ({ content }) => {
  if (!content || !content.match(LATEX_REGEX)) return null;

  return (
    <MathJax>
      {content.match(LATEX_REGEX).map((formula, index) => (
        <div key={index} className="math-formula">{formula}</div>
      ))}
    </MathJax>
  );
};

// Mesaj versiyonlarını render et
export const VersionsRenderer = ({ versions, isExpanded, setIsExpanded }) => {
  if (!versions || versions.length === 0) return null;

  return (
    <div className="message-versions">
      <div
        className="versions-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="versions-icon">🔄</span>
        <span className="versions-title">Yanıt Versiyonları ({versions.length})</span>
        <span className="expansion-indicator">{isExpanded ? '▼' : '▶'}</span>
      </div>

      {isExpanded && (
        <div className="versions-content">
          {versions.map((version, index) => (
            <div key={index} className="version-item">
              <div className="version-header">
                <span className="version-number">V{index + 1}</span>
                <span className="version-type">{version.type || "Düzenleme"}</span>
              </div>
              <div
                className="version-content"
                dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked(version.content)) }}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};