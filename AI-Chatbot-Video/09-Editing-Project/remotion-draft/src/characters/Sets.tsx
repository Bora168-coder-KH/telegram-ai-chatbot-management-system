import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';

const OUT = '#111827';

/** Sokha's bedroom at night. `lamp` 0..1, children = the character (drawn between wall and desk). */
export const Bedroom: React.FC<{ lamp?: number; folder?: boolean; children?: React.ReactNode; zoom?: number; focusY?: number }> = ({ lamp = 1, folder = false, children, zoom = 1, focusY = 540 }) => {
  const frame = useCurrentFrame();
  const lights = Array.from({ length: 34 }, (_, i) => ({ x: 190 + ((i * 97) % 480), y: 380 + ((i * 53) % 220), on: (i * 7 + Math.floor(frame / 50)) % 9 !== 0 }));
  return (
    <AbsoluteFill style={{ background: '#1D2433' }}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{ transform: `scale(${zoom})`, transformOrigin: `960px ${focusY}px` }}>
        <defs>
          <linearGradient id="wallN" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#2C3547" /><stop offset="1" stopColor="#222A39" /></linearGradient>
          <radialGradient id="lampGlow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stopColor="#F4D9A6" stopOpacity="0.55" /><stop offset="1" stopColor="#F4D9A6" stopOpacity="0" /></radialGradient>
        </defs>
        <rect width={1920} height={1080} fill="url(#wallN)" />
        {/* window with city */}
        <rect x={150} y={150} width={540} height={500} rx={8} fill="#141B28" stroke="#3B4658" strokeWidth={14} />
        <path d="M164 650 L164 470 L230 470 L230 420 L300 420 L300 500 L360 500 L360 380 L430 380 L430 455 L500 455 L500 410 L560 410 L560 520 L620 520 L620 440 L676 440 L676 650 Z" fill="#0F1520" />
        {lights.map((l, i) => l.on && <rect key={i} x={l.x} y={l.y} width={9} height={11} fill="#E8C88E" opacity={0.75} />)}
        <line x1={420} y1={150} x2={420} y2={650} stroke="#3B4658" strokeWidth={10} />
        <path d="M130 130 Q170 400 140 680 L200 680 Q220 400 190 130 Z" fill="#46506A" />
        {/* shelf */}
        <rect x={1380} y={300} width={400} height={14} fill="#5C4A3B" />
        {[0, 1, 2, 3, 4, 5, 6].map((i) => <rect key={i} x={1400 + i * 44} y={200 + (i % 3) * 10} width={36} height={100 - (i % 3) * 10} fill={['#7B5E57', '#5F7464', '#8C7B5A', '#5D6B85', '#7A6A55', '#6B5B70', '#556B6B'][i]} />)}
        {/* lamp glow */}
        <circle cx={1330} cy={600} r={560} fill="url(#lampGlow)" opacity={lamp * 0.9} />
      </svg>
      <AbsoluteFill style={{ transform: `scale(${zoom})`, transformOrigin: `960px ${focusY}px` }}>
        <svg width={1920} height={1080} viewBox="0 0 1920 1080">
          {children}
          {/* desk */}
          <rect x={420} y={772} width={1100} height={34} rx={6} fill="#7E624A" stroke={OUT} strokeWidth={3} />
          <rect x={460} y={806} width={1020} height={300} fill="#5F4A38" />
          {folder && <g><rect x={720} y={740} width={250} height={36} rx={4} fill="#D9C8A4" stroke={OUT} strokeWidth={3} /><rect x={740} y={730} width={210} height={14} fill="#F3EEE2" /></g>}
          {/* lamp */}
          <rect x={1300} y={752} width={110} height={22} rx={8} fill="#3F3A35" />
          <path d="M1352 752 L1330 600 L1290 560" stroke="#3F3A35" strokeWidth={10} fill="none" strokeLinecap="round" />
          <path d="M1230 520 L1340 520 L1310 590 L1250 590 Z" fill={lamp > 0.5 ? '#E8D3A6' : '#8B8375'} stroke={OUT} strokeWidth={3} transform="rotate(-18 1290 560)" />
          {/* books on desk */}
          <rect x={560} y={730} width={120} height={22} fill="#7A8796" stroke={OUT} strokeWidth={2} /><rect x={570} y={708} width={100} height={22} fill="#9E7E62" stroke={OUT} strokeWidth={2} />
        </svg>
      </AbsoluteFill>
      <AbsoluteFill style={{ background: '#0B1020', opacity: (1 - lamp) * 0.45 }} />
    </AbsoluteFill>
  );
};

/** The university help-desk office in the morning. */
export const Office: React.FC<{ children?: React.ReactNode; laptop?: boolean; coffee?: boolean; zoom?: number; focusY?: number; visitor?: boolean }> = ({ children, laptop = true, coffee = true, zoom = 1, focusY = 540, visitor = false }) => {
  const frame = useCurrentFrame();
  const sway = Math.sin(frame / 30) * 3;
  return (
    <AbsoluteFill style={{ background: '#EEF0EC' }}>
      <AbsoluteFill style={{ transform: `scale(${zoom})`, transformOrigin: `960px ${focusY}px` }}>
        <svg width={1920} height={1080} viewBox="0 0 1920 1080">
          <rect width={1920} height={1080} fill="#ECEEEA" />
          <rect x={0} y={860} width={1920} height={220} fill="#D8D4CC" />
          {/* big window */}
          <rect x={110} y={110} width={700} height={560} fill="#DCE8EF" stroke="#FFFFFF" strokeWidth={16} />
          <ellipse cx={300 + sway} cy={560} rx={170} ry={130} fill="#A9C3A0" />
          <ellipse cx={600 - sway} cy={600} rx={200} ry={110} fill="#93B08B" />
          <rect x={290} y={600} width={18} height={70} fill="#8A7461" />
          <line x1={460} y1={110} x2={460} y2={670} stroke="#fff" strokeWidth={12} />
          {/* notice board (blank) */}
          <rect x={1460} y={170} width={300} height={200} rx={6} fill="#E3D9C8" stroke="#C9BBA4" strokeWidth={6} />
          <rect x={1490} y={200} width={90} height={110} fill="#FFFFFF" /><rect x={1600} y={210} width={120} height={70} fill="#F5F0E6" />
          {/* blurred colleague far away */}
          <g opacity={0.35}><circle cx={1250} cy={420} r={34} fill="#6B5544" /><path d="M1200 560 Q1205 470 1250 462 Q1295 470 1300 560 Z" fill="#8FA3B8" /></g>
          {/* plant */}
          <rect x={1660} y={760} width={110} height={110} rx={10} fill="#C4A484" stroke="#111827" strokeWidth={3} />
          {[-40, -10, 20, 45].map((a, i) => <ellipse key={i} cx={1715 + a} cy={690 - Math.abs(a)} rx={22} ry={70} fill={i % 2 ? '#6F8F6A' : '#5E7D5B'} transform={`rotate(${a} ${1715 + a} ${740})`} />)}
          {visitor && <g><circle cx={1530} cy={560} r={70} fill="#2B2B2E" /><path d="M1410 900 Q1420 680 1530 650 Q1640 680 1650 900 Z" fill="#7C8FA3" /></g>}
        </svg>
      </AbsoluteFill>
      <AbsoluteFill style={{ transform: `scale(${zoom})`, transformOrigin: `960px ${focusY}px` }}>
        <svg width={1920} height={1080} viewBox="0 0 1920 1080">
          {children}
          {/* help-desk counter */}
          <rect x={360} y={772} width={1200} height={36} rx={6} fill="#D9BE9A" stroke={OUT} strokeWidth={3} />
          <rect x={390} y={808} width={1140} height={300} fill="#C7A97F" />
          {laptop && (
            <g>
              <path d="M1110 772 L1150 600 L1390 600 L1370 772 Z" fill="#C9CDD2" stroke={OUT} strokeWidth={3} />
              <rect x={1090} y={766} width={300} height={12} rx={4} fill="#B4B9BF" stroke={OUT} strokeWidth={2} />
            </g>
          )}
          {coffee && <g><rect x={640} y={708} width={56} height={66} rx={8} fill="#fff" stroke={OUT} strokeWidth={3} /><path d="M696 724 Q722 728 698 756" stroke={OUT} strokeWidth={3} fill="none" /></g>}
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
