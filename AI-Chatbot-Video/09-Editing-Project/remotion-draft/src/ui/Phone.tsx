import React from 'react';
import { useCurrentFrame } from 'remotion';
import { C, SANS } from '../style';
import scenes from '../data/scenes.json';

type At = [string, number]; // [scene id, seconds into that scene]
export type ChatItem = {
  from: 'user' | 'bot';
  text: string;
  at: At;
  typeFrom?: At;            // user message: typing starts in the input bar
  buttons?: string[][];     // inline buttons under a bot message
  keyboard?: string[][];    // reply keyboard shown after this message
  removeButtonsAt?: At;
  highlight?: [At, At];
  highlightText?: string;   // part of the text to mark
  tap?: { label: string; at: At };
};
export type Toast = { text: string; from: At; to: At };

const start: Record<string, number> = Object.fromEntries((scenes as { id: string; start: number }[]).map((s) => [s.id, s.start]));
export const abs = (a: At) => start[a[0]] + a[1];

const Button: React.FC<{ label: string; tapT?: number; now: number; kb?: boolean }> = ({ label, tapT, now, kb }) => {
  const d = tapT !== undefined ? now - tapT : -1;
  const ring = d >= 0 && d < 0.7;
  return (
    <div style={{ position: 'relative', flex: 1, background: kb ? '#FFFFFF' : 'rgba(255,255,255,0.85)', borderRadius: 10, padding: '9px 6px', textAlign: 'center',
      color: kb ? C.text : C.accent, fontSize: 19, fontWeight: 500, border: kb ? '1px solid #CBD2D9' : '1px solid rgba(31,95,122,0.18)', transform: ring && d < 0.2 ? 'scale(0.96)' : 'none', overflow: 'visible' } as React.CSSProperties}>
      {label}
      {ring && (
        <div style={{ position: 'absolute', left: '50%', top: '50%', width: 30 + d * 90, height: 30 + d * 90, marginLeft: -(15 + d * 45), marginTop: -(15 + d * 45),
          borderRadius: '50%', border: `3px solid ${C.accent}`, opacity: 1 - d / 0.7 }} />
      )}
    </div>
  );
};

const mark = (text: string, part?: string, on?: boolean) => {
  if (!part || !on || !text.includes(part)) return text;
  const [a, b] = [text.indexOf(part), text.indexOf(part) + part.length];
  return (<>{text.slice(0, a)}<span style={{ background: '#FDE9B6', borderRadius: 4, padding: '0 2px' }}>{text.slice(a, b)}</span>{text.slice(b)}</>);
};

export const Phone: React.FC<{ items: ChatItem[]; sceneStart: number; toasts?: Toast[]; clock?: string; x?: number; y?: number; scale?: number; name?: string }> = ({
  items, sceneStart, toasts = [], clock = '00:12', x = 1240, y = 34, scale = 0.88, name = 'AI Chatbot' }) => {
  const frame = useCurrentFrame();
  const now = sceneStart + frame / 25;
  const visible = items.filter((m) => now >= abs(m.at));
  const typing = items.find((m) => m.typeFrom && now >= abs(m.typeFrom) && now < abs(m.at));
  let typed = '';
  if (typing) {
    const p = (now - abs(typing.typeFrom!)) / Math.max(0.1, abs(typing.at) - 0.25 - abs(typing.typeFrom!));
    const chars = Array.from(typing.text);
    typed = chars.slice(0, Math.min(chars.length, Math.ceil(chars.length * Math.min(1, p)))).join('');
  }
  const kbItem = [...visible].reverse().find((m) => m.keyboard);
  const toast = toasts.find((t) => now >= abs(t.from) && now < abs(t.to));
  return (
    <div style={{ position: 'absolute', left: x, top: y, width: 470, height: 940, transform: `scale(${scale})`, transformOrigin: '0 0', zIndex: 30 }}>
      <div style={{ width: 470, height: 940, background: '#111827', borderRadius: 64, padding: 14, boxShadow: '0 18px 50px rgba(17,24,39,0.22)' }}>
        <div style={{ width: '100%', height: '100%', borderRadius: 52, overflow: 'hidden', background: '#E7ECF0', display: 'flex', flexDirection: 'column', fontFamily: SANS, position: 'relative' }}>
          <div style={{ height: 44, display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 36px 0', fontSize: 18, fontWeight: 600, color: C.text, background: '#fff' }}>
            <span>{clock}</span><span style={{ fontSize: 15, color: C.sub }}>●●● ▮</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '10px 22px 14px', background: '#fff', borderBottom: `1px solid ${C.border}` }}>
            <div style={{ width: 48, height: 48, borderRadius: '50%', background: C.accent, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 18 }}>AI</div>
            <div><div style={{ fontSize: 21, fontWeight: 600, color: C.text }}>{name}</div><div style={{ fontSize: 16, color: C.sub }}>bot</div></div>
          </div>
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', gap: 10, padding: '12px 14px', overflow: 'hidden' }}>
            {visible.map((m, i) => {
              const age = now - abs(m.at);
              const e = 1 - Math.pow(1 - Math.min(1, age / 0.3), 3);
              const hl = m.highlight && now >= abs(m.highlight[0]) && now < abs(m.highlight[1]);
              const showButtons = m.buttons && !(m.removeButtonsAt && now >= abs(m.removeButtonsAt));
              const tapT = m.tap ? abs(m.tap.at) : undefined;
              return (
                <div key={i} style={{ alignSelf: m.from === 'user' ? 'flex-end' : 'flex-start', maxWidth: 360, opacity: e, transform: `translateY(${(1 - e) * 16}px)` }}>
                  <div style={{ background: m.from === 'user' ? '#D7EAF7' : '#fff', borderRadius: 18, padding: '11px 16px', fontSize: 21, lineHeight: 1.5, color: C.text,
                    outline: hl ? `3px solid ${C.accent}` : 'none', outlineOffset: 3, whiteSpace: 'pre-wrap' }}>
                    {mark(m.text, m.highlightText, hl)}
                  </div>
                  {showButtons && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 6 }}>
                      {m.buttons!.map((row, r) => (
                        <div key={r} style={{ display: 'flex', gap: 6 }}>
                          {row.map((b) => <Button key={b} label={b} now={now} tapT={m.tap && m.tap.label === b ? tapT : undefined} />)}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
          <div style={{ background: '#fff', padding: '12px 18px', display: 'flex', alignItems: 'center', gap: 12, borderTop: `1px solid ${C.border}` }}>
            <div style={{ flex: 1, minHeight: 44, borderRadius: 22, background: '#F3F4F6', padding: '9px 18px', fontSize: 20, color: typed ? C.text : C.muted, lineHeight: 1.45 }}>
              {typed || 'Message'}{typed && Math.floor(now * 2) % 2 === 0 ? '|' : ''}
            </div>
            <div style={{ width: 44, height: 44, borderRadius: '50%', background: typed ? C.accent : '#CBD2D9', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20 }}>➤</div>
          </div>
          {kbItem && (
            <div style={{ background: '#D9DEE3', padding: '10px 10px 26px', display: 'flex', flexDirection: 'column', gap: 7 }}>
              {kbItem.keyboard!.map((row, r) => (
                <div key={r} style={{ display: 'flex', gap: 7 }}>
                  {row.map((b) => {
                    const tapper = items.find((m) => m.from === 'user' && m.text === b && Math.abs(now - abs(m.at)) < 1);
                    return <Button key={b} label={b} kb now={now} tapT={tapper ? abs(tapper.at) - 0.35 : undefined} />;
                  })}
                </div>
              ))}
            </div>
          )}
          {toast && (
            <div style={{ position: 'absolute', top: 130, left: 30, right: 30, background: 'rgba(17,24,39,0.88)', color: '#fff', borderRadius: 14, padding: '14px 18px', fontSize: 20, textAlign: 'center', lineHeight: 1.5 }}>
              {toast.text}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
