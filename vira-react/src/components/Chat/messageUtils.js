import { marked } from 'marked';
import DOMPurify from 'dompurify';

// Regex sabitleri
export const LATEX_REGEX = /\$\$(.*?)\$\$|\$(.*?)\$/g;
export const TOOL_CALL_REGEX = /<tool>(.*?)<\/tool>/gs;
export const CITATION_REGEX = /\[\^(\d+)\]:\s*(.*?)(?=\n\[\^|\n\n|$)/gs;
export const STEPS_REGEX = /<steps>(.*?)<\/steps>/gs;
export const URL_REGEX = /(https?:\/\/[^\s]+)/g;
export const CHART_REGEX = /<chart type="(.*?)">(.*?)<\/chart>/gs;
export const MAP_REGEX = /<map lat="(.*?)" lng="(.*?)">(.*?)<\/map>/g;
export const CODE_BLOCK_REGEX = /```([a-zA-Z]*)\n([\s\S]*?)```/g;

// İçerik işleme fonksiyonu
export const processContent = (content) => {
  if (!content) return { html: "İçerik yüklenemedi. Lütfen tekrar deneyin.", charts: [], maps: [] };

  // LaTeX formüllerini işle
  let processedContent = content.replace(LATEX_REGEX, (match, p1, p2) => {
    const formula = p1 || p2;
    return `<span class="math-formula">${match}</span>`;
  });

  // Araç çağrılarını işle
  processedContent = processedContent.replace(TOOL_CALL_REGEX, (match, toolCall) => {
    return `<div class="tool-call-container">
              <div class="tool-call-header">
                <span class="tool-icon">🔧</span>
                <span class="tool-title">Araç Çağrısı</span>
              </div>
              <div class="tool-call-content">${toolCall}</div>
            </div>`;
  });

  // Adım adım işlemleri işle
  processedContent = processedContent.replace(STEPS_REGEX, (match, steps) => {
    const stepsList = steps.split('\n').filter(step => step.trim()).map((step, index) =>
      `<div class="process-step">
         <div class="step-number">${index + 1}</div>
         <div class="step-content">${step}</div>
       </div>`
    ).join('');

    return `<div class="process-steps-container">
              <div class="steps-header">
                <span class="steps-icon">📋</span>
                <span class="steps-title">İşlem Adımları</span>
              </div>
              <div class="steps-content">${stepsList}</div>
            </div>`;
  });

  // Kaynakları işle
  const citations = [];
  processedContent = processedContent.replace(CITATION_REGEX, (match, num, citation) => {
    citations.push({ num, citation });
    return '';
  });

  // Kod bloklarını işle
  const codeBlocks = [];
  processedContent = processedContent.replace(CODE_BLOCK_REGEX, (match, language, code) => {
    const blockId = `code-${codeBlocks.length}`;
    codeBlocks.push({ id: blockId, language: language || 'text', code });
    return `<div id="${blockId}" class="code-block-placeholder"></div>`;
  });

  // Grafikleri işle
  const charts = [];
  processedContent = processedContent.replace(CHART_REGEX, (match, type, data) => {
    try {
      const chartId = `chart-${charts.length}`;
      charts.push({ id: chartId, type, data: JSON.parse(data) });
      return `<div id="${chartId}" class="chart-placeholder">Grafik yükleniyor...</div>`;
    } catch (error) {
      console.error("Grafik verisi ayrıştırılamadı:", error);
      return '<div class="chart-error">Grafik verisi ayrıştırılamadı</div>';
    }
  });

  // Haritaları işle
  const maps = [];
  processedContent = processedContent.replace(MAP_REGEX, (match, lat, lng, title) => {
    try {
      const mapId = `map-${maps.length}`;
      maps.push({ id: mapId, lat: parseFloat(lat), lng: parseFloat(lng), title });
      return `<div id="${mapId}" class="map-placeholder">Harita yükleniyor...</div>`;
    } catch (error) {
      console.error("Harita verisi ayrıştırılamadı:", error);
      return '<div class="map-error">Harita verisi ayrıştırılamadı</div>';
    }
  });

  // Linkleri işle
  processedContent = processedContent.replace(URL_REGEX, (url) => {
    return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="auto-link">${url}</a>`;
  });

  // Markdown'ı HTML'e dönüştür
  let html = marked(processedContent);

  // Eğer kaynak varsa, kaynakları ekle
  if (citations.length > 0) {
    html += '<div class="citations-container">';
    html += '<h4 class="citations-title">Kaynaklar</h4>';
    html += '<ol class="citations-list">';
    citations.forEach(({ num, citation }) => {
      html += `<li id="citation-${num}" class="citation-item">
                 <span class="citation-content">${citation}</span>
                 ${citation.match(URL_REGEX) ? 
                   `<a href="${citation.match(URL_REGEX)[0]}" target="_blank" class="citation-link">Kaynağa Git</a>` : ''}
               </li>`;
    });
    html += '</ol></div>';
  }

  // Temiz HTML döndür
  return { html: DOMPurify.sanitize(html), charts, maps, codeBlocks };
};

// Diğer yardımcı fonksiyonlar buraya eklenebilir