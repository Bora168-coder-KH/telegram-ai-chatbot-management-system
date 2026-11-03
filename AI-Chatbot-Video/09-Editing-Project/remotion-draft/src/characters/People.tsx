import React from 'react';
import { useCurrentFrame } from 'remotion';

const OUT = '#111827';
const SW = 3.5;

export type Expr = 'neutral' | 'unsure' | 'sad' | 'smile' | 'surprised' | 'tired' | 'thinking' | 'closed';

/** Blink: eyes close for ~3 frames every few seconds (offset per character). */
const blinkY = (frame: number, offset: number) => {
  const t = (frame + offset) % 92;
  return t < 3 ? 0.12 : 1;
};

const Eyes: React.FC<{ expr: Expr; frame: number; offset: number; look: 'forward' | 'down' | 'side' | 'up'; skin: string }> = ({ expr, frame, offset, look, skin }) => {
  const by = expr === 'closed' ? 0.1 : expr === 'tired' ? 0.45 : blinkY(frame, offset);
  const dx = look === 'side' ? -7 : look === 'up' ? -4 : 0;
  const dy = look === 'down' ? 6 : look === 'up' ? -5 : 0;
  const ry = (expr === 'surprised' ? 13 : 11) * by;
  return (
    <g>
      {[268, 332].map((x) => (
        <g key={x}>
          <ellipse cx={x + dx} cy={250 + dy} rx={9} ry={Math.max(1.2, ry)} fill="#2B1B12" />
          {by > 0.5 && <circle cx={x + dx + 3} cy={246 + dy} r={2.6} fill="#fff" />}
          {(look === 'down' || expr === 'tired') && <path d={`M${x - 13} ${242 + dy} Q${x} ${236 + dy} ${x + 13} ${242 + dy} L${x + 13} ${247 + dy} L${x - 13} ${247 + dy} Z`} fill={skin} />}
        </g>
      ))}
    </g>
  );
};

const Brows: React.FC<{ expr: Expr; color: string }> = ({ expr, color }) => {
  const d: Record<string, [string, string]> = {
    neutral: ['M252 224 Q268 216 284 222', 'M316 222 Q332 216 348 224'],
    smile: ['M252 222 Q268 213 284 219', 'M316 219 Q332 213 348 222'],
    unsure: ['M252 222 Q268 214 284 224', 'M316 218 Q332 210 348 220'],
    sad: ['M252 226 Q268 222 284 216', 'M316 216 Q332 222 348 226'],
    surprised: ['M252 214 Q268 204 284 212', 'M316 212 Q332 204 348 214'],
    tired: ['M252 228 Q268 224 284 222', 'M316 222 Q332 224 348 228'],
    thinking: ['M252 220 Q268 212 284 218', 'M316 222 Q332 218 348 222'],
    closed: ['M252 228 Q268 222 284 224', 'M316 224 Q332 222 348 228'],
  };
  const [a, b] = d[expr];
  return <g stroke={color} strokeWidth={6} strokeLinecap="round" fill="none"><path d={a} /><path d={b} /></g>;
};

const Mouth: React.FC<{ expr: Expr; lip: string }> = ({ expr, lip }) => {
  switch (expr) {
    case 'smile': return <path d="M276 296 Q300 318 324 296 Q300 308 276 296 Z" fill="#7A2E2E" stroke={lip} strokeWidth={2.5} strokeLinejoin="round" />;
    case 'sad': return <path d="M282 306 Q300 296 318 306" stroke={lip} strokeWidth={4} fill="none" strokeLinecap="round" />;
    case 'surprised': return <ellipse cx={300} cy={302} rx={9} ry={11} fill="#7A2E2E" />;
    case 'unsure': return <path d="M284 302 Q296 298 306 302 Q312 304 318 300" stroke={lip} strokeWidth={4} fill="none" strokeLinecap="round" />;
    case 'tired': case 'closed': return <path d="M286 304 L314 304" stroke={lip} strokeWidth={4} strokeLinecap="round" />;
    case 'thinking': return <path d="M290 303 Q302 299 312 304" stroke={lip} strokeWidth={4} fill="none" strokeLinecap="round" />;
    default: return <path d="M282 300 Q300 310 318 300" stroke={lip} strokeWidth={4} fill="none" strokeLinecap="round" />;
  }
};

type PersonProps = { expr?: Expr; look?: 'forward' | 'down' | 'side' | 'up'; action?: string; x?: number; y?: number; scale?: number };

/** SOKHA — 20, light-brown skin, shoulder-length black hair with a black clip on the left side, light-blue blouse, white phone. */
export const Sokha: React.FC<PersonProps & { holding?: 'phone' | 'folder' | 'none'; phoneLight?: number }> = ({
  expr = 'neutral', look = 'forward', holding = 'none', phoneLight = 0, x = 0, y = 0, scale = 1 }) => {
  const frame = useCurrentFrame();
  const skin = '#C98E62', skinD = '#B47A50', hair = '#17171A', blouse = '#A9CBE8', blouseD = '#8FB6DA';
  const breathe = 1 + Math.sin(frame / 22) * 0.006;
  const tilt = Math.sin(frame / 37) * 1.2 + (look === 'down' ? 4 : 0);
  return (
    <g transform={`translate(${x},${y}) scale(${scale})`}>
      <g transform={`translate(300 640) scale(1 ${breathe}) translate(-300 -640)`}>
        {/* back hair */}
        <path d="M212 200 Q206 330 222 392 L378 392 Q394 330 388 200 Z" fill={hair} />
        {/* body */}
        <path d="M160 640 L176 430 Q186 392 236 380 L272 368 Q300 384 328 368 L364 380 Q414 392 424 430 L440 640 Z" fill={blouse} stroke={OUT} strokeWidth={SW} />
        <path d="M272 368 L300 414 L328 368" fill="none" stroke={blouseD} strokeWidth={5} />
        <rect x={276} y={312} width={48} height={62} rx={12} fill={skinD} />
        {/* head */}
        <g transform={`rotate(${tilt} 300 330)`}>
          <ellipse cx={220} cy={252} rx={13} ry={20} fill={skinD} />
          <ellipse cx={380} cy={252} rx={13} ry={20} fill={skinD} />
          <ellipse cx={300} cy={248} rx={80} ry={94} fill={skin} stroke={OUT} strokeWidth={SW} />
          <circle cx={258} cy={282} r={13} fill="#E07A6A" opacity={0.18} />
          <circle cx={342} cy={282} r={13} fill="#E07A6A" opacity={0.18} />
          {/* fringe with side part */}
          <path d="M218 252 Q206 160 286 146 Q350 138 380 186 Q392 214 384 252 Q368 198 330 176 Q300 206 246 214 Q230 226 218 252 Z" fill={hair} />
          {/* hair clip on her left (viewer right) */}
          <rect x={348} y={178} width={34} height={9} rx={4} fill="#3F4652" stroke="#6B7280" strokeWidth={1.5} transform="rotate(-28 365 182)" />
          <Brows expr={expr} color={hair} />
          <Eyes expr={expr} frame={frame} offset={11} look={look} skin={skin} />
          <path d="M300 262 Q295 278 304 282" stroke={skinD} strokeWidth={3.5} fill="none" strokeLinecap="round" />
          <Mouth expr={expr} lip="#8A3B35" />
          {phoneLight > 0 && <ellipse cx={300} cy={262} rx={86} ry={100} fill="#DDEBFF" opacity={0.18 * phoneLight} />}
        </g>
        {/* arms and hands */}
        {holding === 'phone' ? (
          <g>
            <path d="M188 470 Q200 560 268 560 L282 532 Q228 520 224 462 Z" fill={blouse} stroke={OUT} strokeWidth={SW} />
            <path d="M412 470 Q400 560 332 560 L318 532 Q372 520 376 462 Z" fill={blouse} stroke={OUT} strokeWidth={SW} />
            <rect x={252} y={446} width={96} height={150} rx={16} fill="#F7F7F5" stroke={OUT} strokeWidth={SW} transform="rotate(-6 300 520)" />
            <ellipse cx={268} cy={552} rx={22} ry={18} fill={skin} stroke={OUT} strokeWidth={SW} />
            <ellipse cx={334} cy={552} rx={22} ry={18} fill={skin} stroke={OUT} strokeWidth={SW} />
          </g>
        ) : (
          <g>
            <path d="M176 470 Q170 590 236 610 L250 580 Q214 566 214 470 Z" fill={blouse} stroke={OUT} strokeWidth={SW} />
            <path d="M424 470 Q430 590 364 610 L350 580 Q386 566 386 470 Z" fill={blouse} stroke={OUT} strokeWidth={SW} />
          </g>
        )}
      </g>
    </g>
  );
};

/** DARA — 28, medium-brown skin, short side-parted black hair, thin black rectangular glasses, white shirt, navy lanyard, silver watch. */
export const Dara: React.FC<PersonProps> = ({ expr = 'neutral', look = 'forward', action = 'sit', x = 0, y = 0, scale = 1 }) => {
  const frame = useCurrentFrame();
  const skin = '#A86E46', skinD = '#93603C', hair = '#141416', shirt = '#F7F7F4', shirtD = '#E1E3E0';
  const breathe = 1 + Math.sin(frame / 24) * 0.006;
  const turn = look === 'side' ? -14 : 0;
  const tilt = Math.sin(frame / 41) * 1 + (look === 'down' ? 3 : 0) + (action === 'rub' ? 5 : 0);
  const typeL = action === 'type' ? Math.sin(frame / 2.2) * 6 : 0;
  const typeR = action === 'type' ? Math.cos(frame / 2.6) * 6 : 0;
  return (
    <g transform={`translate(${x},${y}) scale(${scale})`}>
      <g transform={`translate(300 640) scale(1 ${breathe}) translate(-300 -640)`}>
        {/* body */}
        <path d="M150 640 L166 440 Q176 396 232 384 L272 370 Q300 380 328 370 L368 384 Q424 396 434 440 L450 640 Z" fill={shirt} stroke={OUT} strokeWidth={SW} />
        <rect x={274} y={310} width={52} height={66} rx={12} fill={skinD} />
        <path d="M262 372 L300 404 L276 418 Z M338 372 L300 404 L324 418 Z" fill={shirtD} stroke={OUT} strokeWidth={2.5} />
        {/* lanyard + blank staff card */}
        <path d="M268 380 L292 470 M332 380 L308 470" stroke="#1E3A5F" strokeWidth={7} strokeLinecap="round" />
        <rect x={274} y={466} width={52} height={68} rx={6} fill="#fff" stroke="#1E3A5F" strokeWidth={3} />
        <rect x={284} y={480} width={32} height={6} rx={3} fill="#D1D5DB" />
        <line x1={300} y1={410} x2={300} y2={640} stroke={shirtD} strokeWidth={3} />
        {/* head */}
        <g transform={`rotate(${tilt} 300 330) translate(${turn} 0)`}>
          <ellipse cx={222 - turn * 0.4} cy={252} rx={12} ry={19} fill={skinD} />
          <ellipse cx={378 - turn * 0.4} cy={252} rx={12} ry={19} fill={skinD} />
          <ellipse cx={300} cy={246} rx={78} ry={92} fill={skin} stroke={OUT} strokeWidth={SW} />
          {/* short hair with side part */}
          <path d="M222 236 Q214 160 280 146 Q356 136 380 196 Q384 214 378 236 Q370 196 336 184 L262 186 Q236 196 222 236 Z" fill={hair} />
          <path d="M262 186 Q282 166 300 160" stroke="#3A3A3E" strokeWidth={3} fill="none" />
          <Brows expr={expr} color={hair} />
          <Eyes expr={expr} frame={frame} offset={47} look={look} skin={skin} />
          {/* glasses */}
          <g fill="none" stroke="#111" strokeWidth={4.5}>
            <rect x={244} y={234} width={48} height={34} rx={7} />
            <rect x={308} y={234} width={48} height={34} rx={7} />
            <path d="M292 248 Q300 243 308 248 M244 246 L226 242 M356 246 L374 242" />
          </g>
          <path d="M300 266 Q294 280 304 284" stroke={skinD} strokeWidth={3.5} fill="none" strokeLinecap="round" />
          <Mouth expr={expr} lip="#6E3A2A" />
        </g>
        {/* arms */}
        {action === 'rub' ? (
          <g>
            <path d="M412 452 Q470 380 352 270 L330 292 Q420 380 380 452 Z" fill={shirt} stroke={OUT} strokeWidth={SW} />
            <ellipse cx={338} cy={268} rx={24} ry={20} fill={skin} stroke={OUT} strokeWidth={SW} />
            <path d="M176 470 Q170 590 236 610 L250 580 Q214 566 214 470 Z" fill={shirt} stroke={OUT} strokeWidth={SW} />
          </g>
        ) : action === 'coffee' ? (
          <g>
            <path d="M410 456 Q440 380 352 330 L336 356 Q404 400 380 456 Z" fill={shirt} stroke={OUT} strokeWidth={SW} />
            <rect x={324} y={300} width={44} height={52} rx={6} fill="#fff" stroke={OUT} strokeWidth={SW} />
            <ellipse cx={342} cy={350} rx={20} ry={16} fill={skin} stroke={OUT} strokeWidth={SW} />
            <rect x={348} y={344} width={18} height={6} fill="#C0C4C8" />
            <path d="M176 470 Q170 590 236 610 L250 580 Q214 566 214 470 Z" fill={shirt} stroke={OUT} strokeWidth={SW} />
          </g>
        ) : (
          <g>
            <path d={`M176 470 Q170 ${590 + typeL} 250 ${604 + typeL} L262 ${574 + typeL} Q214 566 214 470 Z`} fill={shirt} stroke={OUT} strokeWidth={SW} />
            <path d={`M424 470 Q430 ${590 + typeR} 350 ${604 + typeR} L338 ${574 + typeR} Q386 566 386 470 Z`} fill={shirt} stroke={OUT} strokeWidth={SW} />
            {/* silver watch on his left wrist (viewer right) */}
            <rect x={360} y={570 + typeR} width={22} height={30} rx={5} fill="#C9CDD2" stroke={OUT} strokeWidth={2} transform={`rotate(-58 371 ${585 + typeR})`} />
          </g>
        )}
      </g>
    </g>
  );
};
