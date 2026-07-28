/** Official brand icon assets — white monochrome for dark UI (Simple Icons + SmartView). */
window.BRAND_ICON_SRC = {
  apple: '/assets/apple-brand.svg',
  teams: '/assets/teams-brand.svg',
  browser: '/assets/browser-brand.svg',
  airplay: '/assets/airplay-brand.svg',
  smartview: '/assets/smartview-brand.svg',
  stb: '/assets/stb-brand.png',
  usb_c: '/assets/usb-c-brand.png',
  whiteboard: '/assets/whiteboard-brand.png',
};

window.brandIconHtml = function brandIconHtml(key) {
  const src = window.BRAND_ICON_SRC[key];
  if (!src) return '';
  return `<img class="brand-icon-img" src="${src}" alt="" />`;
};

window.isBrandIcon = function isBrandIcon(key) {
  return Object.prototype.hasOwnProperty.call(window.BRAND_ICON_SRC, key);
};
