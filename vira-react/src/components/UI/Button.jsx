import React from 'react';

/**
 * Genel amaçlı buton bileşeni
 * 
 * @param {Object} props - Bileşen özellikleri
 * @param {string} [props.variant='primary'] - Buton varyantı: 'primary', 'secondary', 'danger'
 * @param {boolean} [props.disabled=false] - Buton devre dışı mı?
 * @param {string} [props.type='button'] - Buton tipi: 'button', 'submit', 'reset'
 * @param {Function} [props.onClick] - Tıklama olayı işleyici
 * @param {ReactNode} props.children - Buton içeriği
 * @param {string} [props.className] - Ek CSS sınıfları
 */
const Button = ({ 
  variant = 'primary', 
  disabled = false, 
  type = 'button',
  onClick,
  children,
  className = '',
  ...rest
}) => {
  const baseClass = 'btn';
  const variantClass = `btn-${variant}`;
  const classes = [baseClass, variantClass, className].filter(Boolean).join(' ');
  
  return (
    <button
      type={type}
      className={classes}
      disabled={disabled}
      onClick={onClick}
      {...rest}
    >
      {children}
    </button>
  );
};

export default Button;