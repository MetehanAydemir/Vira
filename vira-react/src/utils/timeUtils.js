/**
 * Şu anki saati formatlanmış olarak döndürür
 * @returns {string} Şu anki saat (HH:MM:SS)
 */
export const getCurrentTime = () => {
  const now = new Date();
  return now.toLocaleTimeString('tr-TR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

/**
 * Şu anki tarihi formatlanmış olarak döndürür
 * @returns {string} Şu anki tarih (DD.MM.YYYY)
 */
export const getCurrentDate = () => {
  const now = new Date();
  return now.toLocaleDateString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
};

/**
 * İki tarih arasındaki farkı "... önce" formatında döndürür
 * @param {Date|string|number} date - Tarih objesi, string veya timestamp
 * @returns {string} "... önce" formatında zaman
 */
export const getTimeAgo = (date) => {
  if (!date) return '';
  
  const now = new Date();
  const pastDate = new Date(date);
  
  // Geçersiz tarih kontrolü
  if (isNaN(pastDate.getTime())) return '';
  
  const seconds = Math.floor((now - pastDate) / 1000);
  
  // Gelecek tarih kontrolü
  if (seconds < 0) {
    return 'şimdi';
  }
  
  // Zaman aralıklarını hesapla
  const intervals = {
    yıl: Math.floor(seconds / 31536000),
    ay: Math.floor(seconds / 2592000),
    hafta: Math.floor(seconds / 604800),
    gün: Math.floor(seconds / 86400),
    saat: Math.floor(seconds / 3600),
    dakika: Math.floor(seconds / 60)
  };
  
  // İlk uygun zaman aralığını bul
  for (const [interval, value] of Object.entries(intervals)) {
    if (value >= 1) {
      return `${value} ${interval}${value > 1 && interval !== 'ay' ? '' : ''} önce`;
    }
  }
  
  return 'az önce';
};

/**
 * Saniye cinsinden süreyi formatlar (mm:ss)
 * @param {number} seconds - Saniye cinsinden süre
 * @returns {string} Formatlanmış süre (mm:ss)
 */
export const formatDuration = (seconds) => {
  if (!seconds || isNaN(seconds)) return '00:00';
  
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

/**
 * Bir ISO tarihini yerel saat dilimine dönüştürür
 * @param {string} isoDate - ISO formatında tarih
 * @returns {Date} Yerel saat diliminde tarih
 */
export const toLocalTime = (isoDate) => {
  if (!isoDate) return null;
  
  try {
    return new Date(isoDate);
  } catch (error) {
    console.error('Tarih dönüştürme hatası:', error);
    return null;
  }
};