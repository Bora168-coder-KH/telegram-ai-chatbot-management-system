import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';

/** Simple modern campus building in the morning (no signs, no logos). */
export const Campus: React.FC<{ pan?: boolean; people?: boolean }> = ({ pan = true, people = false }) => {
  const frame = useCurrentFrame();
  const dx = pan ? -frame * 0.6 : 0;
  return (
    <AbsoluteFill style={{ background: '#E6EEF2' }}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080">
        <rect width={1920} height={700} fill="#E3ECF1" />
        <circle cx={1550} cy={210} r={80} fill="#F6E7C8" opacity={0.8} />
        <g transform={`translate(${dx} 0)`}>
          <rect x={300} y={300} width={1300} height={420} fill="#F4F2EE" stroke="#C9CED3" strokeWidth={4} />
          <rect x={700} y={220} width={500} height={500} fill="#FBFAF7" stroke="#C9CED3" strokeWidth={4} />
          {Array.from({ length: 4 }, (_, r) => Array.from({ length: 16 }, (_, c) => (
            <rect key={`${r}-${c}`} x={330 + c * 78} y={340 + r * 88} width={54} height={56} fill="#B9CCD8" opacity={c >= 5 && c <= 10 ? 0 : 0.9} />)))}
          {Array.from({ length: 5 }, (_, r) => Array.from({ length: 5 }, (_, c) => (
            <rect key={`g${r}-${c}`} x={740 + c * 88} y={250 + r * 86} width={70} height={62} fill="#A9C1D0" />)))}
          <rect x={880} y={620} width={160} height={100} fill="#8FA9B9" />
          {[200, 1700, 2000, -80].map((x, i) => (
            <g key={i}><rect x={x + 30} y={600} width={18} height={130} fill="#8A7461" /><ellipse cx={x + 40} cy={560} rx={110} ry={120} fill={i % 2 ? '#8FB08A' : '#A3C19A'} /></g>
          ))}
        </g>
        <rect y={720} width={1920} height={360} fill="#CFD6CF" />
        <rect y={760} width={1920} height={80} fill="#E7E3DA" />
        {people && [0, 1, 2, 3, 4].map((i) => {
          const x = ((i * 410 + frame * (1.2 + i * 0.2)) % 2100) - 100;
          return <g key={i} opacity={0.75}><circle cx={x} cy={735} r={13} fill="#3B3B3F" /><rect x={x - 12} y={748} width={24} height={46} rx={10} fill={['#7C8FA3', '#A98C6E', '#6F8F6A', '#9A7FA0', '#8C9AA8'][i]} /></g>;
        })}
      </svg>
    </AbsoluteFill>
  );
};
