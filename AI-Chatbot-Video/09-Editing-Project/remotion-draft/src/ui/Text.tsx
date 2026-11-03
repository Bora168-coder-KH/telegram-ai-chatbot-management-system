import React from 'react';
import { useCurrentFrame } from 'remotion';
import { fadeUp, fadeIn, between } from '../anim';
import { C, SANS, SERIF, Lang } from '../style';

type Cue = { from: number; to: number; text: string };

/** Burned-in subtitles (bottom centre). */
export const Subtitles: React.FC<{ cues: Cue[]; lang: Lang }> = ({ cues, lang }) => {
  const frame = useCurrentFrame();
  const t = frame / 25;
  const cue = cues.find((c) => t >= c.from && t < c.to);
  if (!cue) return null;
  const o = between(frame, cue.from, cue.to, 0.12);
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, bottom: 44, display: 'flex', justifyContent: 'center', opacity: o, zIndex: 50 }}>
      <div style={{ maxWidth: 1480, background: 'rgba(17,24,39,0.84)', color: '#fff', borderRadius: 12, padding: lang === 'kh' ? '10px 28px 14px' : '12px 28px',
        fontFamily: SANS, fontSize: lang === 'kh' ? 38 : 40, lineHeight: lang === 'kh' ? 1.6 : 1.35, fontWeight: 500, textAlign: 'center' }}>
        {cue.text}
      </div>
    </div>
  );
};

/** Small on-screen label card (top-left by default). */
export const Label: React.FC<{ text: string; at?: number; x?: number; y?: number; size?: number; width?: number }> = ({ text, at = 0.3, x = 72, y = 64, size = 30, width }) => {
  const frame = useCurrentFrame();
  if (!text) return null;
  const lines = text.split('\n');
  return (
    <div style={{ position: 'absolute', left: x, top: y, ...fadeUp(frame, at), background: C.card, border: `1px solid ${C.border}`, borderRadius: 14,
      padding: '16px 26px', maxWidth: width ?? 1100, fontFamily: SANS, color: C.text, zIndex: 40, boxShadow: '0 2px 10px rgba(17,24,39,0.06)' }}>
      {lines.map((l, i) => (
        <div key={i} style={{ fontSize: i === 0 ? size : size * 0.78, fontWeight: i === 0 ? 600 : 400, color: i === 0 ? C.text : C.sub, lineHeight: 1.5 }}>{l}</div>
      ))}
    </div>
  );
};

/** Name lower-third for characters and the presenter. */
export const LowerThird: React.FC<{ name: string; role: string; note?: string; at?: number }> = ({ name, role, note, at = 0.6 }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ position: 'absolute', left: 96, bottom: 190, ...fadeUp(frame, at), background: C.card, border: `1px solid ${C.border}`, borderRadius: 14,
      padding: '16px 28px', fontFamily: SANS, zIndex: 40 }}>
      <div style={{ fontSize: 40, fontWeight: 600, color: C.text, fontFamily: SERIF }}>{name}</div>
      <div style={{ fontSize: 26, color: C.sub, marginTop: 2 }}>{role}</div>
      {note ? <div style={{ fontSize: 20, color: C.muted, marginTop: 4 }}>{note}</div> : null}
    </div>
  );
};

/** Centered title text block. */
export const Title: React.FC<{ lines: string[]; at?: number; size?: number; color?: string; gap?: number; serif?: boolean }> = ({ lines, at = 0.3, size = 72, color = C.text, gap = 0.35, serif = true }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ textAlign: 'center', fontFamily: serif ? SERIF : SANS, color }}>
      {lines.map((l, i) => (
        <div key={i} style={{ ...fadeUp(frame, at + i * gap), fontSize: i === 0 ? size : size * 0.42, fontWeight: i === 0 ? 600 : 400,
          color: i === 0 ? color : C.sub, fontFamily: i === 0 && serif ? SERIF : SANS, marginTop: i === 0 ? 0 : 22, lineHeight: 1.35 }}>{l}</div>
      ))}
    </div>
  );
};

export const Clock: React.FC<{ from: string; to?: string; switchAt?: number; at?: number; dark?: boolean }> = ({ from, to, switchAt = 99, at = 0.2, dark = true }) => {
  const frame = useCurrentFrame();
  const shown = to && frame / 25 >= switchAt ? to : from;
  return (
    <div style={{ position: 'absolute', right: 72, top: 64, ...fadeIn(frame, at), fontFamily: SANS, fontSize: 44, fontWeight: 600, letterSpacing: 1,
      color: dark ? '#F3F4F6' : C.text, background: dark ? 'rgba(17,24,39,0.55)' : C.card, border: dark ? '1px solid rgba(255,255,255,0.15)' : `1px solid ${C.border}`,
      borderRadius: 12, padding: '8px 22px', zIndex: 40 }}>{shown}</div>
  );
};

/** Honest tag on screenshots of the real system. */
export const RealTag: React.FC<{ lang: Lang }> = ({ lang }) => (
  <div style={{ position: 'absolute', right: 28, top: 22, fontFamily: SANS, fontSize: 20, color: C.sub, background: 'rgba(255,255,255,0.92)',
    border: `1px solid ${C.border}`, borderRadius: 8, padding: '6px 14px', zIndex: 45 }}>
    {lang === 'kh' ? 'ប្រព័ន្ធពិត · ទិន្នន័យសាកល្បង' : 'Real system · demo data'}
  </div>
);
