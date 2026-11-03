import { loadFont } from '@remotion/fonts';
import { staticFile } from 'remotion';

export const C = {
  bg: '#FAF9F6', card: '#FFFFFF', card2: '#F2EFE9', text: '#111827', sub: '#4B5563', border: '#E5E7EB',
  accent: '#1F5F7A', accentSoft: '#DCE9EF', muted: '#9CA3AF', ok: '#2F6B4F', warn: '#9A6B1F',
};
export const FPS = 25;
export type Lang = 'kh' | 'en';

const fonts: [string, string, string][] = [
  ['Kantumruy', 'kantumruy-pro-khmer-400-normal.woff2', '400'],
  ['Kantumruy', 'kantumruy-pro-khmer-600-normal.woff2', '600'],
  ['Kantumruy', 'kantumruy-pro-khmer-700-normal.woff2', '700'],
  ['Inter', 'inter-latin-400-normal.woff2', '400'],
  ['Inter', 'inter-latin-500-normal.woff2', '500'],
  ['Inter', 'inter-latin-600-normal.woff2', '600'],
  ['Inter', 'inter-latin-700-normal.woff2', '700'],
  ['Newsreader', 'newsreader-latin-500-normal.woff2', '500'],
  ['Newsreader', 'newsreader-latin-600-normal.woff2', '600'],
];
for (const [family, file, weight] of fonts) {
  loadFont({ family, url: staticFile('fonts/' + file), weight });
}

// Latin text uses Inter; Khmer letters fall back to Kantumruy Pro.
export const SANS = "'Inter', 'Kantumruy', sans-serif";
export const SERIF = "'Newsreader', 'Kantumruy', serif";
export const font = (_lang: Lang) => SANS;
