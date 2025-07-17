/**
 * Tarih formatla
 * @param {Date} date - Formatlanacak tarih
 * @returns {string} Formatlanmış tarih
 */
export const formatDate = (date) => {
  if (!date) return '';
  
  try {
    return new Intl.DateTimeFormat('tr-TR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  } catch (error) {
    console.error('Tarih formatlama hatası:', error);
    return date.toString();
  }
};

/**
 * Dosya boyutu formatla
 * @param {number} bytes - Dosya boyutu (byte)
 * @returns {string} Formatlanmış boyut
 */
export const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B';
  
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  
  return `${parseFloat((bytes / Math.pow(1024, i)).toFixed(2))} ${sizes[i]}`;
};

/**
 * Telefon numarası formatla
 * @param {string} phoneNumber - Telefon numarası
 * @returns {string} Formatlanmış telefon numarası
 */
export const formatPhoneNumber = (phoneNumber) => {
  if (!phoneNumber) return '';
  
  // Sayısal olmayan karakterleri temizle
  const cleaned = phoneNumber.replace(/\D/g, '');
  
  // TR telefon formatı: +90 (555) 123 45 67
  if (cleaned.length === 10) {
    return `+90 (${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)} ${cleaned.slice(6, 8)} ${cleaned.slice(8, 10)}`;
  } else if (cleaned.length === 11 && cleaned.startsWith('0')) {
    return `+90 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)} ${cleaned.slice(7, 9)} ${cleaned.slice(9, 11)}`;
  }
  
  return phoneNumber;
};

/**
 * HTML içeriğini güvenli bir şekilde işle
 * @param {string} html - HTML içeriği
 * @returns {string} Güvenli HTML
 */
export const sanitizeHtml = (html) => {
  if (!html) return '';
  
  // Basit HTML sanitizer
  return html
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
};

/**
 * Metni belirli bir uzunlukta kısalt
 * @param {string} text - Kısaltılacak metin
 * @param {number} maxLength - Maksimum uzunluk
 * @returns {string} Kısaltılmış metin
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
};