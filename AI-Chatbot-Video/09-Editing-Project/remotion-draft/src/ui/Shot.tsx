import React from 'react';
import { Img, staticFile, useCurrentFrame } from 'remotion';
import { ramp, ease, mix, between } from '../anim';
import { C } from '../style';
import boxes from '../data/boxes.json';

type Box = [number, number, number, number];
export type HL = { key: string; from: number; to: number };

/** A real dashboard screenshot (1920x1080) with optional slow zoom toward a box and highlight outlines. */
export const Shot: React.FC<{ name: string; highlights?: HL[]; zoom?: { key: string; scale: number; from: number; to: number }; fadeAt?: number; dim?: boolean }> = ({ name, highlights = [], zoom, fadeAt, dim = true }) => {
  const frame = useCurrentFrame();
  const b = (boxes as unknown as Record<string, Record<string, Box>>)[name] || {};
  let transform = 'none';
  if (zoom && b[zoom.key]) {
    const [x, y, w, h] = b[zoom.key];
    const p = ease(ramp(frame, zoom.from, zoom.to));
    const s = mix(1, zoom.scale, p);
    const cx = x + w / 2, cy = y + h / 2;
    // point c maps to mix(c, centre, p); keep the image covering the frame
    const tx = Math.min(0, Math.max(1920 - s * 1920, mix(cx, 960, p) - s * cx));
    const ty = Math.min(0, Math.max(1080 - s * 1080, mix(cy, 540, p) - s * cy));
    transform = `translate(${tx}px, ${ty}px) scale(${s})`;
  }
  const active = highlights.map((h) => ({ h, o: between(frame, h.from, h.to, 0.25), r: b[h.key] })).filter((a) => a.r && a.o > 0);
  const dimO = dim && active.length ? Math.max(...active.map((a) => a.o)) * 0.28 : 0;
  return (
    <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', opacity: fadeAt !== undefined ? ramp(frame, fadeAt, fadeAt + 0.35) : 1, background: C.bg }}>
      <div style={{ position: 'absolute', inset: 0, transform, transformOrigin: '0 0' }}>
        <Img src={staticFile('shots/' + name + '.png')} style={{ width: 1920, height: 1080, display: 'block' }} />
        <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0 }}>
          <defs>
            <mask id={'m-' + name}>
              <rect width={1920} height={1080} fill="white" />
              {active.map(({ r }, i) => <rect key={i} x={r![0] - 10} y={r![1] - 10} width={r![2] + 20} height={r![3] + 20} rx={10} fill="black" />)}
            </mask>
          </defs>
          {dimO > 0 && <rect width={1920} height={1080} fill="#111827" opacity={dimO} mask={`url(#m-${name})`} />}
          {active.map(({ r, o }, i) => (
            <rect key={i} x={r![0] - 10} y={r![1] - 10} width={r![2] + 20} height={r![3] + 20} rx={10} fill="none" stroke={C.accent} strokeWidth={4} opacity={o} />
          ))}
        </svg>
      </div>
    </div>
  );
};
