import { FONT_CSS } from './fontData';

export const C = {
  bg: '#FAF9F6', card: '#FFFFFF', card2: '#F2EFE9', text: '#111827', sub: '#4B5563', border: '#E5E7EB',
  accent: '#1F5F7A', accentSoft: '#DCE9EF', muted: '#9CA3AF', ok: '#2F6B4F', warn: '#9A6B1F',
};
export const FPS = 25;
export type Lang = 'kh' | 'en';

// Fonts are embedded (src/fontData.ts) and added once; Video.tsx waits for them with delayRender.
if (typeof document !== 'undefined' && !document.getElementById('embedded-fonts')) {
  const el = document.createElement('style');
  el.id = 'embedded-fonts';
  el.textContent = FONT_CSS;
  document.head.appendChild(el);
}
export const FONT_PROBES = ['400 20px Kantumruy', '600 20px Kantumruy', '700 20px Kantumruy', '400 20px Inter', '500 20px Inter', '600 20px Inter', '700 20px Inter', '500 20px Newsreader', '600 20px Newsreader'];

// Latin text uses Inter; Khmer letters fall back to Kantumruy Pro.
export const SANS = "'Inter', 'Kantumruy', sans-serif";
export const SERIF = "'Newsreader', 'Kantumruy', serif";
export const font = (_lang: Lang) => SANS;
