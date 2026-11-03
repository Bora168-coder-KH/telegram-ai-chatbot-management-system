import React from 'react';
import { AbsoluteFill, Img, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { fadeUp, fadeIn, ramp, ease, mix, sec, between, pop } from '../anim';
import { C, Lang, SANS, SERIF } from '../style';
import { Label, LowerThird, Title, Clock, RealTag } from '../ui/Text';
import { Shot } from '../ui/Shot';
import { Phone } from '../ui/Phone';
import { Sokha, Dara } from '../characters/People';
import { Bedroom, Office } from '../characters/Sets';
import { Campus } from '../characters/Campus';
import { SOKHA_CHAT, SOKHA_TOASTS, STUDENT_B_CHAT, WELCOME_KH, WELCOME_EN, FALLBACK_TEXT, FALLBACK_BUTTONS, ANSWER_EN, ANSWER_KH, FAQ_ANSWER_NEW } from '../data/chat';
import scenesData from '../data/scenes.json';

type SceneInfo = { id: string; dur: number; start: number; capKh: string; capEn: string; subKh: { from: number; to: number; text: string }[]; subEn: { from: number; to: number; text: string }[] };
export type P = { lang: Lang; info: SceneInfo };
const L = (lang: Lang, kh: string, en: string) => (lang === 'kh' ? kh : en);
const cap = (p: P) => (p.lang === 'kh' ? p.info.capKh : p.info.capEn);
const Bg: React.FC<{ children?: React.ReactNode; color?: string }> = ({ children, color = C.bg }) => <AbsoluteFill style={{ background: color }}>{children}</AbsoluteFill>;
/** Show children only from `from` seconds (optionally until `to`). */
const At: React.FC<{ from: number; to?: number; children: React.ReactNode }> = ({ from, to, children }) => (
  <Sequence from={sec(from)} durationInFrames={to !== undefined ? sec(to - from) : undefined} layout="none">{children}</Sequence>
);
const SOKHA_X = 660, SOKHA_Y = 180, DARA_X = 660, DARA_Y = 186;

// ---------- reusable layouts ----------
const SideText: React.FC<{ p: P; extra?: React.ReactNode; at?: number }> = ({ p, extra, at = 0.3 }) => {
  const frame = useCurrentFrame();
  const lines = cap(p).split('\n');
  return (
    <div style={{ position: 'absolute', left: 120, top: 250, width: 1000, fontFamily: SANS, color: C.text }}>
      {lines.map((l, i) => (
        <div key={i} style={{ ...fadeUp(frame, at + i * 0.3), fontFamily: i === 0 ? SERIF : SANS, fontSize: i === 0 ? (l.length > 40 ? 42 : l.length > 22 ? 50 : 60) : 32,
          fontWeight: i === 0 ? 600 : 400, color: i === 0 ? C.text : C.sub, lineHeight: 1.4, marginBottom: 18 }}>{l}</div>
      ))}
      {extra}
    </div>
  );
};

const PhoneScene: React.FC<{ p: P; extra?: React.ReactNode; clock?: string; items?: typeof SOKHA_CHAT; name?: string }> = ({ p, extra, clock = '00:12', items = SOKHA_CHAT, name }) => (
  <Bg>
    <SideText p={p} extra={extra} />
    <Phone items={items} toasts={SOKHA_TOASTS} sceneStart={p.info.start} clock={clock} name={name} />
  </Bg>
);

const Split: React.FC<{ left: React.ReactNode; right: React.ReactNode; labels?: [string, string] }> = ({ left, right, labels }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', left: 0, top: 0, width: 958, height: 1080, overflow: 'hidden' }}><div style={{ position: 'absolute', left: -480, top: 0, width: 1920, height: 1080 }}>{left}</div></div>
      <div style={{ position: 'absolute', left: 962, top: 0, width: 958, height: 1080, overflow: 'hidden' }}><div style={{ position: 'absolute', left: -480, top: 0, width: 1920, height: 1080 }}>{right}</div></div>
      <div style={{ position: 'absolute', left: 958, top: 0, width: 4, height: 1080, background: C.bg }} />
      {labels && labels.map((t, i) => (
        <div key={i} style={{ position: 'absolute', top: 60, left: i === 0 ? 60 : 1022, ...fadeUp(frame, 0.5 + i * 0.3), background: C.card, border: `1px solid ${C.border}`,
          borderRadius: 12, padding: '12px 22px', fontFamily: SANS, fontSize: 30, fontWeight: 600, color: C.text }}>{t}</div>
      ))}
    </AbsoluteFill>
  );
};

const SlideIn: React.FC<{ at: number; children: React.ReactNode; from?: number }> = ({ at, children, from = 600 }) => {
  const frame = useCurrentFrame();
  const p = ease(ramp(frame, at, at + 0.6));
  return <div style={{ position: 'absolute', inset: 0, transform: `translateX(${(1 - p) * from}px)`, opacity: p }}>{children}</div>;
};

const Scrim: React.FC<{ at: number }> = ({ at }) => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{ background: 'rgba(250,249,246,0.55)', opacity: ramp(frame, at, at + 0.5) }} />;
};

const PresenterPlaceholder: React.FC<{ lang: Lang }> = ({ lang }) => (
  <Bg color={C.card2}>
    <div style={{ position: 'absolute', left: 340, top: 120, width: 1240, height: 700, border: `3px dashed ${C.muted}`, borderRadius: 18, background: '#ECE8E0',
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontFamily: SANS }}>
      <svg width={260} height={260} viewBox="0 0 260 260"><circle cx={130} cy={92} r={58} fill="#D6D1C6" /><path d="M30 260 Q36 160 130 156 Q224 160 230 260 Z" fill="#D6D1C6" /></svg>
      <div style={{ fontSize: 36, color: C.sub, marginTop: 18, fontWeight: 500 }}>{L(lang, 'ដាក់វីដេអូពិតរបស់អ្នកធ្វើបទបង្ហាញនៅទីនេះ', 'Place the real presenter video here')}</div>
      <div style={{ fontSize: 26, color: C.muted, marginTop: 8 }}>{L(lang, 'ថតបញ្ញាដោយទូរស័ព្ទ (មិនប្រើ AI)', 'Film Panhna with a phone (no AI)')}</div>
    </div>
  </Bg>
);

// ---------- Chapter 1 ----------
const S001: React.FC<P> = (p) => (
  <Bg><AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
    <Title lines={[...cap(p).split('\n')]} size={74} at={0.6} gap={0.6} />
  </AbsoluteFill></Bg>
);

const S002: React.FC<P> = (p) => (
  <AbsoluteFill>
    <At from={0} to={3.2}><Campus /></At>
    <At from={3.2}><PresenterPlaceholder lang={p.lang} />
      <LowerThird name={L(p.lang, 'បញ្ញា', 'Panhna')} role={L(p.lang, 'អ្នកធ្វើបទបង្ហាញ · វិទ្យាសាស្ត្រ និងវិស្វកម្មកំព្យូទ័រ', 'Presenter · Computer Science and Engineering')}
        note={L(p.lang, 'សាកលវិទ្យាល័យពាណិជ្ជសាស្ត្រ អេស៊ីលីដា', 'ACLEDA University of Business')} at={0.5} />
    </At>
  </AbsoluteFill>
);

const S003: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const names = cap(p).split('\n')[1].split(' · ');
  const subs = p.lang === 'kh' ? p.info.subKh : p.info.subEn;
  const c2 = subs[1] ?? subs[0];
  return (
    <Bg>
      <div style={{ position: 'absolute', top: 150, width: '100%', textAlign: 'center', fontFamily: SERIF, fontSize: 66, fontWeight: 600, color: C.text, ...fadeUp(frame, 0.3) }}>{cap(p).split('\n')[0]}</div>
      <div style={{ position: 'absolute', top: 330, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 60 }}>
        {names.map((n, i) => {
          const t = c2.from + (i / names.length) * (c2.to - c2.from);
          const on = ramp(frame, t, t + 0.3);
          return (
            <div key={n} style={{ ...fadeUp(frame, 0.6 + i * 0.15), width: 300, textAlign: 'center', fontFamily: SANS, opacity: (0.45 + 0.55 * on) * fadeUp(frame, 0.6 + i * 0.15).opacity }}>
              <div style={{ width: 240, height: 240, margin: '0 auto', borderRadius: '50%', background: C.card2, border: `${on > 0.5 ? 4 : 2}px solid ${on > 0.5 ? C.accent : C.border}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                <div style={{ fontFamily: SERIF, fontSize: 90, color: C.sub }}>{n.slice(0, 1)}</div>
                <div style={{ fontSize: 18, color: C.muted }}>{L(p.lang, 'ដាក់រូបថតពិត', 'Add real photo')}</div>
              </div>
              <div style={{ fontSize: 40, fontWeight: 600, color: C.text, marginTop: 24 }}>{n}</div>
            </div>
          );
        })}
      </div>
    </Bg>
  );
};

const S004: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const [sup, name] = cap(p).split('\n');
  const subs = p.lang === 'kh' ? p.info.subKh : p.info.subEn;
  const t3 = subs[2]?.from ?? 4;
  return (
    <Bg><AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', fontFamily: SANS }}>
      <div style={{ ...fadeUp(frame, 0.8), fontSize: 40, color: C.sub }}>{sup}</div>
      <div style={{ ...fadeUp(frame, t3), fontFamily: SERIF, fontSize: 76, fontWeight: 600, color: C.text, marginTop: 40, textAlign: 'center', maxWidth: 1500, lineHeight: 1.25 }}>{name}</div>
    </AbsoluteFill></Bg>
  );
};

const Step: React.FC<{ n: number; text: string; at: number }> = ({ n, text, at }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ ...fadeUp(frame, at), width: 420, background: C.card, border: `1px solid ${C.border}`, borderRadius: 18, padding: '34px 30px', fontFamily: SANS }}>
      <div style={{ fontFamily: SERIF, fontSize: 64, color: C.accent, fontWeight: 600 }}>{n}</div>
      <div style={{ fontSize: 34, color: C.text, lineHeight: 1.45, marginTop: 8 }}>{text}</div>
    </div>
  );
};
const Arrow: React.FC<{ at: number }> = ({ at }) => {
  const frame = useCurrentFrame();
  const p = ramp(frame, at, at + 0.4);
  return <svg width={90} height={40}><line x1={6} y1={20} x2={6 + 70 * p} y2={20} stroke={C.sub} strokeWidth={4} />{p > 0.9 && <path d="M66 8 L82 20 L66 32" stroke={C.sub} strokeWidth={4} fill="none" />}</svg>;
};

const S005: React.FC<P> = (p) => (
  <Bg>
    <Label text={cap(p)} x={0} y={150} size={40} width={1920} />
    <AbsoluteFill style={{ flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 18, top: 60 }}>
      <Step n={1} at={0.8} text={L(p.lang, 'និស្សិតសួរសំណួរ', 'A student asks a question')} />
      <Arrow at={2.0} />
      <Step n={2} at={2.4} text={L(p.lang, 'Bot ឆ្លើយពី FAQ ដែលបានរក្សាទុក', 'The bot answers from saved FAQs')} />
      <Arrow at={3.6} />
      <Step n={3} at={4.0} text={L(p.lang, 'បុគ្គលិកជួយសំណួរដែល Bot មិនអាចឆ្លើយ', 'Staff help with the questions the bot cannot answer')} />
    </AbsoluteFill>
  </Bg>
);

// ---------- Chapter 2 ----------
const sokhaName = (lang: Lang) => <LowerThird name={L(lang, 'សុខា', 'Sokha')} role={L(lang, 'អ្នកដាក់ពាក្យចូលសិក្សា', 'University applicant')} note={L(lang, 'តួអង្គប្រឌិត', 'Fictional character')} at={0.8} />;
const daraName = (lang: Lang) => <LowerThird name={L(lang, 'ដារ៉ា', 'Dara')} role={L(lang, 'បុគ្គលិកបម្រើសេវាអតិថិជន', 'Customer service staff')} note={L(lang, 'តួអង្គប្រឌិត', 'Fictional character')} at={1.6} />;

const S006: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const t = frame / 25;
  return (
    <AbsoluteFill>
      <Bedroom folder zoom={mix(1, 1.08, ramp(frame, 0, 9))} focusY={430}>
        <Sokha x={SOKHA_X} y={SOKHA_Y} expr={t > 3.6 ? 'unsure' : 'neutral'} look={t < 3.2 ? 'down' : 'forward'} />
      </Bedroom>
      {sokhaName(p.lang)}
    </AbsoluteFill>
  );
};

const OldChat: React.FC<{ lang: Lang }> = ({ lang }) => {
  const frame = useCurrentFrame();
  return (
    <Bg color="#E9ECEF">
      <div style={{ position: 'absolute', left: 560, top: 110, width: 800, height: 760, background: '#fff', borderRadius: 24, border: `1px solid ${C.border}`, fontFamily: SANS, overflow: 'hidden' }}>
        <div style={{ padding: '24px 32px', borderBottom: `1px solid ${C.border}`, fontSize: 30, fontWeight: 600, color: C.text }}>{L(lang, 'ផ្នែកចុះឈ្មោះ (ឧទាហរណ៍)', 'Admissions office (example)')}
          <div style={{ fontSize: 22, color: C.muted, fontWeight: 400 }}>{L(lang, 'មុនពេលមាន Chatbot', 'Before the chatbot')}</div></div>
        <div style={{ position: 'absolute', right: 32, bottom: 60, maxWidth: 560, ...fadeUp(frame, 0.4) }}>
          <div style={{ background: '#D7EAF7', borderRadius: 20, padding: '18px 24px', fontSize: 30, lineHeight: 1.55, color: C.text }}>
            {L(lang, 'ជម្រាបសួរ! ខ្ញុំចង់ដាក់ពាក្យចូលរៀន។ តើត្រូវការឯកសារអ្វីខ្លះ?', 'Hello! I want to apply. Which documents do I need?')}</div>
          <div style={{ textAlign: 'right', fontSize: 22, color: C.muted, marginTop: 8 }}>00:12 · {L(lang, 'បានផ្ញើ', 'Sent')} ✓</div>
        </div>
      </div>
    </Bg>
  );
};

const S007: React.FC<P> = (p) => (
  <AbsoluteFill>
    <At from={0} to={3.4}><Bedroom folder zoom={1.18} focusY={480}><Sokha x={SOKHA_X} y={SOKHA_Y} holding="phone" look="down" phoneLight={1} /></Bedroom></At>
    <At from={3.4}><OldChat lang={p.lang} /></At>
    <Clock from="00:12" />
  </AbsoluteFill>
);

const S008: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const t = frame / 25;
  return (
    <AbsoluteFill>
      <Bedroom folder zoom={1.12} focusY={460}>
        <Sokha x={SOKHA_X} y={SOKHA_Y} holding={t < 4.4 ? 'phone' : 'none'} look={t < 4.4 ? 'down' : 'forward'} expr={t > 2.2 ? 'sad' : 'neutral'} phoneLight={t < 4.4 ? 1 : 0} />
      </Bedroom>
      <Clock from="00:12" to="00:45" switchAt={3} />
      <Label text={cap(p)} x={72} y={64} size={34} at={2.2} />
      <AbsoluteFill style={{ background: C.bg, opacity: ramp(frame, p.info.dur - 0.8, p.info.dur) }} />
    </AbsoluteFill>
  );
};

const S009: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const enter = ease(ramp(frame, 0, 1.4));
  return (
    <AbsoluteFill>
      <Office coffee={enter > 0.99}>
        <Dara x={DARA_X + (1 - enter) * 700} y={DARA_Y} action={enter < 1 ? 'coffee' : 'sit'} />
      </Office>
      {daraName(p.lang)}
      <AbsoluteFill style={{ background: C.bg, opacity: 1 - ramp(frame, 0, 0.6) }} />
    </AbsoluteFill>
  );
};

const INBOX: [string, boolean, string][] = [
  ['Which documents do I need?', true, 'S.'], ['តើត្រូវការឯកសារអ្វីខ្លះ?', true, 'V.'], ['When is the registration deadline?', false, 'M.'],
  ['What documents should I bring to apply?', true, 'R.'], ['តើត្រូវការឯកសារអ្វីខ្លះដើម្បីចុះឈ្មោះ?', true, 'N.'], ['Is there a registration fee?', false, 'K.'],
  ['ជម្រាបសួរ! ខ្ញុំចង់ដាក់ពាក្យចូលរៀន។ តើត្រូវការឯកសារអ្វីខ្លះ?', true, 'Sokha'], ['Which documents do I need?', true, 'D.'],
];
const Inbox: React.FC<{ lang: Lang; at: number }> = ({ lang, at }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ position: 'absolute', left: 980, top: 70, width: 860, background: '#fff', borderRadius: 20, border: `1px solid ${C.border}`, fontFamily: SANS, overflow: 'hidden', boxShadow: '0 12px 40px rgba(17,24,39,0.12)', ...fadeUp(frame, at, 30) }}>
      <div style={{ padding: '20px 28px', fontSize: 30, fontWeight: 600, borderBottom: `1px solid ${C.border}` }}>{L(lang, 'សារមិនទាន់អាន', 'Unread messages')}</div>
      {INBOX.map(([q, rep, who], i) => (
        <div key={i} style={{ ...fadeUp(frame, at + 0.3 + i * 0.32, 12), display: 'flex', gap: 18, alignItems: 'center', padding: '13px 28px', borderBottom: `1px solid ${C.border}`, background: rep ? '#F1F4F6' : '#fff' }}>
          <div style={{ width: 46, height: 46, borderRadius: '50%', background: '#D9DEE3', fontSize: 17, display: 'flex', alignItems: 'center', justifyContent: 'center', color: C.sub, flexShrink: 0 }}>{who.slice(0, 2)}</div>
          <div style={{ fontSize: 25, color: C.text, flex: 1, lineHeight: 1.5 }}>{q}</div>
          <div style={{ fontSize: 20, color: C.muted }}>{who === 'Sokha' ? '00:12' : `0${(i % 3) + 6}:${10 + i * 7}`}</div>
        </div>
      ))}
    </div>
  );
};

const S010: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const t = frame / 25;
  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', inset: 0, transform: `translateX(${-ease(ramp(frame, 3.2, 4.0)) * 420}px)` }}>
        <Office zoom={1.12} focusY={420}><Dara x={DARA_X} y={DARA_Y} expr={t > 1.2 ? 'surprised' : 'neutral'} look="down" /></Office>
      </div>
      <Inbox lang={p.lang} at={3.6} />
      <Label text={cap(p)} x={72} y={64} size={32} at={6.5} />
    </AbsoluteFill>
  );
};

const S011: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const reply = L(p.lang, 'សូមយកអត្តសញ្ញាណប័ណ្ណ រូបថត ១ សន្លឹក និងវិញ្ញាបនបត្រចុងក្រោយ។', 'Please bring your ID card, one photo and your latest certificate.');
  return (
    <AbsoluteFill>
      <Office zoom={1.06} focusY={500}><Dara x={DARA_X - 260} y={DARA_Y} action="type" look="down" /></Office>
      <div style={{ position: 'absolute', left: 1080, top: 120, width: 760, fontFamily: SANS }}>
        {[0.6, 2.0, 3.4].map((at, i) => (
          <div key={i} style={{ ...fadeUp(frame, at, 14), background: '#fff', border: `1px solid ${C.border}`, borderRadius: 16, padding: '16px 22px', marginBottom: 16 }}>
            <div style={{ fontSize: 20, color: C.muted, marginBottom: 6 }}>{L(p.lang, 'ចម្លង → បិទភ្ជាប់ → ផ្ញើ', 'Copy → paste → send')} · {i + 1}</div>
            <div style={{ fontSize: 27, color: C.text, lineHeight: 1.5 }}>{reply}</div>
          </div>
        ))}
      </div>
      <Label text={cap(p)} x={72} y={64} size={32} at={0.6} />
    </AbsoluteFill>
  );
};

const S012: React.FC<P> = () => {
  const frame = useCurrentFrame();
  const t = frame / 25;
  const rub = t > 0.7 && t < 3.4;
  return <Office zoom={1.14} focusY={420}><Dara x={DARA_X} y={DARA_Y} action={rub ? 'rub' : 'sit'} expr={rub ? 'closed' : 'tired'} /></Office>;
};

const S013: React.FC<P> = () => {
  const frame = useCurrentFrame();
  const b = pop(frame, 1.4);
  const check = ramp(frame, 4.2, 4.8);
  return (
    <AbsoluteFill>
      <Office zoom={1.08} focusY={440}><Dara x={DARA_X} y={DARA_Y} look="side" expr="thinking" /></Office>
      <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0 }}>
        <g opacity={Math.min(1, b)} transform={`translate(520 200) scale(${0.6 + 0.4 * b})`}>
          <circle cx={300} cy={250} r={10} fill="#fff" stroke={C.text} strokeWidth={3} />
          <circle cx={260} cy={205} r={16} fill="#fff" stroke={C.text} strokeWidth={3} />
          <ellipse cx={130} cy={100} rx={150} ry={95} fill="#fff" stroke={C.text} strokeWidth={3} />
          <g transform="translate(70 40)">
            <rect x={0} y={20} width={120} height={80} rx={18} fill={C.card2} stroke={C.text} strokeWidth={3} />
            <text x={60} y={78} textAnchor="middle" fontFamily={SERIF} fontSize={54} fill={C.sub} opacity={1 - check}>?</text>
            <path d="M34 62 L54 82 L90 42" stroke={C.ok} strokeWidth={8} fill="none" strokeLinecap="round" strokeDasharray={90} strokeDashoffset={90 * (1 - check)} />
          </g>
        </g>
      </svg>
    </AbsoluteFill>
  );
};

// ---------- Chapter 3 ----------
const Db: React.FC = () => (
  <svg width={150} height={170} viewBox="0 0 150 170"><ellipse cx={75} cy={30} rx={65} ry={22} fill={C.card2} stroke={C.text} strokeWidth={3} />
    <path d="M10 30 L10 140 Q75 175 140 140 L140 30" fill={C.card2} stroke={C.text} strokeWidth={3} /><path d="M10 72 Q75 104 140 72 M10 108 Q75 140 140 108" fill="none" stroke={C.text} strokeWidth={3} /></svg>
);
const Line: React.FC<{ x1: number; y1: number; x2: number; y2: number; at: number }> = ({ x1, y1, x2, y2, at }) => {
  const frame = useCurrentFrame();
  const p = ramp(frame, at, at + 0.6);
  return <line x1={x1} y1={y1} x2={mix(x1, x2, p)} y2={mix(y1, y2, p)} stroke={C.sub} strokeWidth={4} strokeDasharray="10 8" />;
};

const S014: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const w = p.lang === 'kh' ? WELCOME_KH : WELCOME_EN;
  const items = [{ from: 'user' as const, text: '/start', at: [p.info.id, 0] as [string, number] }, { from: 'bot' as const, text: w.text, keyboard: w.buttons, at: [p.info.id, 0] as [string, number] }];
  const subs = p.lang === 'kh' ? p.info.subKh : p.info.subEn;
  const t2 = subs[1]?.from ?? 4;
  return (
    <Bg>
      <div style={{ position: 'absolute', top: 64, width: '100%', textAlign: 'center', fontFamily: SERIF, fontSize: 60, fontWeight: 600, ...fadeUp(frame, 0.4) }}>AI Chatbot Management System</div>
      <div style={{ opacity: fadeUp(frame, t2).opacity }}><Phone items={items} sceneStart={p.info.start} x={250} y={190} scale={0.66} clock="08:00" /></div>
      <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0 }}>
        <Line x1={580} y1={520} x2={830} y2={560} at={t2 + 0.6} />
        <Line x1={1000} y1={560} x2={1120} y2={520} at={t2 + 1.4} />
      </svg>
      <div style={{ position: 'absolute', left: 840, top: 470, ...fadeUp(frame, t2 + 0.5) }}><Db /></div>
      <div style={{ position: 'absolute', left: 1130, top: 300, width: 680, ...fadeUp(frame, t2 + 1.2) }}>
        <div style={{ background: '#111827', borderRadius: 18, padding: 14 }}><Img src={staticFile('shots/dashboard-top.png')} style={{ width: '100%', borderRadius: 8, display: 'block' }} /></div>
        <div style={{ height: 18, background: '#C9CDD2', margin: '0 -30px', borderRadius: '0 0 16px 16px' }} />
      </div>
      <div style={{ position: 'absolute', left: 230, top: 840, width: 360, textAlign: 'center', fontFamily: SANS, fontSize: 30, color: C.text, ...fadeUp(frame, t2 + 0.3) }}>{L(p.lang, 'Telegram Bot · សម្រាប់និស្សិត', 'Telegram bot · for students')}</div>
      <div style={{ position: 'absolute', left: 1130, top: 760, width: 680, textAlign: 'center', fontFamily: SANS, fontSize: 30, color: C.text, ...fadeUp(frame, t2 + 1.5) }}>{L(p.lang, 'ផ្ទាំងគ្រប់គ្រងលើវេបសាយ · សម្រាប់បុគ្គលិក', 'Web dashboard · for staff')}</div>
      <div style={{ position: 'absolute', left: 800, top: 650, width: 230, textAlign: 'center', fontFamily: SANS, fontSize: 24, color: C.sub, ...fadeUp(frame, t2 + 0.8) }}>{L(p.lang, 'មូលដ្ឋានទិន្នន័យ', 'Database')}</div>
    </Bg>
  );
};

const ShotScene: React.FC<{ p: P; children: React.ReactNode; label?: boolean }> = ({ p, children, label = true }) => (
  <AbsoluteFill>
    {children}
    <RealTag lang={p.lang} />
    {label && <Label text={cap(p)} x={1920 - 28 - 760} y={78} size={26} width={760} at={0.4} />}
  </AbsoluteFill>
);

const S015: React.FC<P> = (p) => (
  <ShotScene p={p}><Shot name="faq-page" highlights={[{ key: 'form', from: 0.8, to: 5.4 }, { key: 'toggle', from: 5.4, to: p.info.dur }]} zoom={{ key: 'toggle', scale: 1.15, from: 5.2, to: 7.4 }} /></ShotScene>
);

const S016: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const mk = (w: typeof WELCOME_KH) => [{ from: 'bot' as const, text: w.text, keyboard: w.buttons, at: [p.info.id, 0] as [string, number] }];
  return (
    <Bg>
      <div style={{ position: 'absolute', left: 470, top: 40, width: 420, textAlign: 'center', fontFamily: SANS, fontSize: 36, fontWeight: 600, ...fadeUp(frame, 0.3) }}>ខ្មែរ</div>
      <div style={{ position: 'absolute', left: 1030, top: 40, width: 420, textAlign: 'center', fontFamily: SANS, fontSize: 36, fontWeight: 600, ...fadeUp(frame, 0.6) }}>English</div>
      <Phone items={mk(WELCOME_KH)} sceneStart={p.info.start} x={470} y={110} scale={0.88} clock="08:00" />
      <Phone items={mk(WELCOME_EN)} sceneStart={p.info.start} x={1030} y={110} scale={0.88} clock="08:00" />
    </Bg>
  );
};

const QCard: React.FC<{ text: string; at: number; x: number; y: number; move: number; tag: string }> = ({ text, at, x, y, move, tag }) => {
  const frame = useCurrentFrame();
  const m = ease(ramp(frame, move, move + 0.8));
  return (
    <div style={{ position: 'absolute', left: mix(x, x + 120, m), top: y, width: 660, ...fadeUp(frame, at), background: '#D7EAF7', borderRadius: 20, padding: '22px 28px', fontFamily: SANS }}>
      <div style={{ fontSize: 22, color: C.sub, marginBottom: 6 }}>{tag}</div>
      <div style={{ fontSize: 33, color: C.text, lineHeight: 1.5 }}>{text}</div>
    </div>
  );
};

const S017: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const [q1, q2, a] = p.lang === 'kh'
    ? ['តើខ្ញុំត្រូវការឯកសារអ្វីខ្លះដើម្បីចុះឈ្មោះ?', 'តើចុះឈ្មោះចូលរៀន ត្រូវការឯកសារអ្វីខ្លះ?', ANSWER_KH]
    : ['What documents do I need to register?', 'What are the required documents for registration?', ANSWER_EN];
  return (
    <Bg>
      <Label text={cap(p)} x={140} y={70} size={38} />
      <QCard text={q1} at={0.6} x={140} y={300} move={2.4} tag={L(p.lang, 'សំណួរដែលបានរក្សាទុក', 'Saved question')} />
      <QCard text={q2} at={1.3} x={140} y={560} move={2.4} tag={L(p.lang, 'សំណួរថ្មី ពាក្យផ្សេង', 'New question, different words')} />
      <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0 }}>
        <Line x1={930} y1={380} x2={1150} y2={500} at={3.0} />
        <Line x1={930} y1={640} x2={1150} y2={540} at={3.0} />
      </svg>
      <div style={{ position: 'absolute', left: 1160, top: 380, width: 640, ...fadeUp(frame, 3.6), background: '#fff', border: `2px solid ${C.accent}`, borderRadius: 20, padding: '24px 28px', fontFamily: SANS }}>
        <div style={{ fontSize: 22, color: C.accent, marginBottom: 8, fontWeight: 600 }}>{L(p.lang, 'ចម្លើយតែមួយ', 'One saved answer')}</div>
        <div style={{ fontSize: 30, color: C.text, lineHeight: 1.55 }}>{a}</div>
      </div>
    </Bg>
  );
};

const S018: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const fbText = p.lang === 'kh' ? 'សូមអភ័យទោស ខ្ញុំមិនយល់សំណួររបស់អ្នកទេ។ សូមសរសេរម្ដងទៀត ជ្រើសរើសម៉ឺនុយ ឬស្នើសុំជំនួយពីមនុស្ស។' : FALLBACK_TEXT;
  const btns = p.lang === 'kh' ? ['សរសេរម្ដងទៀត', 'ម៉ឺនុយមេ', 'ជំនួយពីមនុស្ស'] : FALLBACK_BUTTONS[0];
  const box = (at: number, children: React.ReactNode, w = 420) => (
    <div style={{ ...fadeUp(frame, at), width: w, background: '#fff', border: `1px solid ${C.border}`, borderRadius: 18, padding: '22px 24px', fontFamily: SANS, fontSize: 28, lineHeight: 1.5, color: C.text }}>{children}</div>
  );
  return (
    <Bg>
      <Label text={cap(p)} x={140} y={70} size={38} />
      <AbsoluteFill style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 14, top: 40 }}>
        {box(0.5, <><div style={{ fontSize: 20, color: C.sub }}>{L(p.lang, 'សំណួរ', 'Question')}</div>Is there a bus to campus?</>, 330)}
        <Arrow at={1.4} />
        {box(1.8, <><div style={{ fontSize: 20, color: C.sub }}>FAQ · Intent · KB</div>{L(p.lang, 'រកមិនឃើញចម្លើយដែលទុកចិត្តបាន', 'No reliable answer found')}</>, 330)}
        <Arrow at={2.8} />
        {box(3.2, <><div>{fbText}</div><div style={{ display: 'flex', gap: 8, marginTop: 14 }}>{btns.map((b) => <div key={b} style={{ flex: 1, textAlign: 'center', fontSize: 20, color: C.accent, border: `1px solid ${C.border}`, borderRadius: 10, padding: '8px 4px' }}>{b}</div>)}</div></>, 520)}
        <Arrow at={5.0} />
        {box(5.4, <><div style={{ fontSize: 20, color: C.sub }}>{L(p.lang, 'ក្រុមជំនួយ', 'Support team')}</div>{L(p.lang, 'មនុស្សពិតឆ្លើយតប', 'A real person replies')}</>, 280)}
      </AbsoluteFill>
    </Bg>
  );
};

const S019: React.FC<P> = (p) => {
  const [l, r] = cap(p).split(' · ').length === 2 ? cap(p).split(' · ') as [string, string] : [cap(p), ''];
  return (
    <Split labels={[l, r]}
      left={<Bedroom lamp={1}><Sokha x={SOKHA_X} y={SOKHA_Y} holding="phone" expr="smile" phoneLight={1} /></Bedroom>}
      right={<Office><Dara x={DARA_X} y={DARA_Y} action="coffee" expr="smile" /></Office>} />
  );
};

// ---------- Chapter 4 ----------
const S020: React.FC<P> = (p) => (
  <AbsoluteFill>
    <PhoneScene p={p} />
    <At from={0} to={2.3}><AbsoluteFill style={{ zIndex: 35 }}><Bedroom zoom={1.15} focusY={460}><Sokha x={SOKHA_X} y={SOKHA_Y} holding="phone" look="down" phoneLight={1} /></Bedroom></AbsoluteFill></At>
  </AbsoluteFill>
);
const S021: React.FC<P> = (p) => <PhoneScene p={p} />;
const S022: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  return <PhoneScene p={p} extra={<div style={{ ...fadeUp(frame, 1.4), marginTop: 30, display: 'inline-block', fontSize: 34, fontWeight: 600, background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: '10px 22px' }}>00:12 · {L(p.lang, 'នៅតែពាក់កណ្ដាលអធ្រាត្រ', 'still midnight')}</div>} />;
};
const S023: React.FC<P> = (p) => <PhoneScene p={p} />;
const S024: React.FC<P> = (p) => <PhoneScene p={p} />;
const S025: React.FC<P> = (p) => <PhoneScene p={p} />;
const S026: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  return <PhoneScene p={p} extra={<div style={{ ...fadeUp(frame, 5.4), marginTop: 30, fontSize: 28, color: C.sub, lineHeight: 1.5 }}>{L(p.lang, 'កាលបរិច្ឆេទត្រូវបានរក្សាទុកក្នុងការសន្ទនា ហើយបុគ្គលិកអាចមើលឃើញនៅ Dashboard។', 'The date is saved in the conversation, and staff can see it in the dashboard.')}</div>} />;
};
const S027: React.FC<P> = (p) => <PhoneScene p={p} />;
const S028: React.FC<P> = (p) => <PhoneScene p={p} />;
const S029: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const t0 = p.info.dur - 3;
  return (
    <AbsoluteFill>
      <PhoneScene p={p} />
      <At from={t0}><AbsoluteFill style={{ zIndex: 35 }}><Bedroom lamp={1 - ramp(frame - sec(t0), 1.2, 1.6)}><Sokha x={SOKHA_X} y={SOKHA_Y} expr="smile" /></Bedroom></AbsoluteFill></At>
    </AbsoluteFill>
  );
};

// ---------- Chapter 5 ----------
const S030: React.FC<P> = (p) => (
  <AbsoluteFill>
    <At from={0} to={2.6}><Office><Dara x={DARA_X} y={DARA_Y} action="type" look="down" /></Office><Label text={cap(p)} x={72} y={64} size={34} /></At>
    <At from={2.6}><ShotScene p={p} label={false}><Shot name="login" highlights={[{ key: 'form', from: 0.3, to: 3.4 }]} /></ShotScene></At>
  </AbsoluteFill>
);
const S031: React.FC<P> = (p) => (
  <ShotScene p={p}>
    <At from={0} to={3.8}><Shot name="dashboard-top" highlights={[{ key: 'cards', from: 0.6, to: 3.6 }]} /></At>
    <At from={3.8}><Shot name="dashboard-unanswered" fadeAt={0} highlights={[{ key: 'row', from: 0.4, to: 9 }]} zoom={{ key: 'row', scale: 1.18, from: 0.2, to: 2.4 }} /></At>
  </ShotScene>
);
const S032: React.FC<P> = (p) => (
  <ShotScene p={p}>
    <At from={0} to={2.6}><Shot name="nav-conversations" highlights={[{ key: 'nav', from: 0.3, to: 2.6 }]} /></At>
    <At from={2.6}><Shot name="conversations" fadeAt={0} highlights={[{ key: 'row', from: 0.3, to: 9 }]} zoom={{ key: 'row', scale: 1.15, from: 0.2, to: 2 }} /></At>
  </ShotScene>
);
const S033: React.FC<P> = (p) => (
  <ShotScene p={p}>
    <At from={0} to={3.8}><Shot name="conversation-start" /></At>
    <At from={3.8}><Shot name="conversation-detected" fadeAt={0} highlights={[{ key: 'detected', from: 0.4, to: 9 }]} zoom={{ key: 'detected', scale: 1.3, from: 0.3, to: 2.2 }} /></At>
  </ShotScene>
);
const SidePhone: React.FC<{ p: P; at: number; x?: number }> = ({ p, at, x = 1240 }) => (
  <><Scrim at={at} /><SlideIn at={at} from={x > 900 ? 600 : -600}><Phone items={SOKHA_CHAT} sceneStart={p.info.start} clock="08:35" x={x} /></SlideIn></>
);
const S034: React.FC<P> = (p) => (
  <ShotScene p={p}>
    <At from={0} to={3.6}><Shot name="conversation-reply-typed" highlights={[{ key: 'box', from: 0.4, to: 2.6 }, { key: 'send', from: 2.4, to: 3.6 }]} zoom={{ key: 'box', scale: 1.25, from: 0.2, to: 1.8 }} /></At>
    <At from={3.6}><Shot name="conversation-reply-sent" /></At>
    <SidePhone p={p} at={3.8} x={80} />
  </ShotScene>
);
const S035: React.FC<P> = (p) => (
  <ShotScene p={p}>
    <Shot name="conversation-resolved" highlights={[{ key: 'status', from: 0.5, to: 3 }]} zoom={{ key: 'status', scale: 1.3, from: 0.3, to: 1.8 }} />
    <SidePhone p={p} at={2.4} x={80} />
  </ShotScene>
);
const S036: React.FC<P> = (p) => (
  <ShotScene p={p}>
    <At from={0} to={3.8}><Shot name="dashboard-addfaq" highlights={[{ key: 'addfaq', from: 0.5, to: 3.8 }]} zoom={{ key: 'addfaq', scale: 1.3, from: 0.3, to: 2.4 }} /></At>
    <At from={3.8}><Shot name="faq-prefilled" fadeAt={0} highlights={[{ key: 'question', from: 0.4, to: 9 }]} zoom={{ key: 'question', scale: 1.2, from: 0.3, to: 2 }} /></At>
  </ShotScene>
);
const S037: React.FC<P> = (p) => (
  <ShotScene p={p}>
    <At from={0} to={4.8}><Shot name="faq-filled" highlights={[{ key: 'answer', from: 0.3, to: 2.4 }, { key: 'keywords', from: 2.4, to: 4.0 }, { key: 'add', from: 3.8, to: 4.8 }]} /></At>
    <At from={4.8}><Shot name="faq-added" fadeAt={0} highlights={[{ key: 'row', from: 0.3, to: 9 }]} zoom={{ key: 'row', scale: 1.2, from: 0.2, to: 1.8 }} /></At>
  </ShotScene>
);
const S038: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  return (
    <Bg>
      <SideText p={p} extra={<div style={{ ...fadeUp(frame, 0.8), fontSize: 30, color: C.sub, lineHeight: 1.5 }}>{L(p.lang, 'និស្សិតម្នាក់ទៀត (គណនីសាកល្បង «Student B»)', 'Another student (test account "Student B")')}</div>} />
      <Phone items={STUDENT_B_CHAT} sceneStart={p.info.start} clock="10:05" />
    </Bg>
  );
};
const S039: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const card = (title: string, text: string, at: number, good: boolean) => (
    <div style={{ ...fadeUp(frame, at), width: 700, background: '#fff', border: `${good ? 2 : 1}px solid ${good ? C.accent : C.border}`, borderRadius: 20, padding: '28px 32px', fontFamily: SANS }}>
      <div style={{ fontFamily: SERIF, fontSize: 44, fontWeight: 600, color: C.text }}>{title}</div>
      <div style={{ fontSize: 24, color: C.sub, margin: '8px 0 16px' }}>“Is there a bus to campus?”</div>
      <div style={{ fontSize: 27, color: C.text, lineHeight: 1.55, background: good ? '#EEF5F0' : '#F3F4F6', borderRadius: 14, padding: '16px 20px' }}>{text}</div>
    </div>
  );
  return (
    <Bg>
      <AbsoluteFill style={{ flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: 70, top: -40 }}>
        {card(L(p.lang, 'ម្សិលមិញ', 'Yesterday'), FALLBACK_TEXT, 0.4, false)}
        {card(L(p.lang, 'ថ្ងៃនេះ', 'Today'), FAQ_ANSWER_NEW, 1.4, true)}
      </AbsoluteFill>
      <div style={{ position: 'absolute', top: 800, width: '100%', textAlign: 'center', fontFamily: SANS, fontSize: 32, color: C.sub, ...fadeUp(frame, 2.6) }}>
        {L(p.lang, 'បុគ្គលិកបានបន្ថែមចម្លើយដែលបានផ្ទៀងផ្ទាត់ — Bot មិនរៀនដោយខ្លួនឯងទេ។', 'A staff member added a verified answer — the bot does not retrain itself.')}</div>
    </Bg>
  );
};
const S040: React.FC<P> = (p) => (
  <ShotScene p={p}>
    <At from={0} to={3.6}><Shot name="broadcast-preview" highlights={[{ key: 'message', from: 0.3, to: 2.0 }, { key: 'audience', from: 1.6, to: 2.8 }, { key: 'send', from: 2.6, to: 3.6 }]} /></At>
    <At from={3.6}><Shot name="broadcast-history" fadeAt={0} highlights={[{ key: 'history', from: 0.3, to: 9 }]} /></At>
    <SidePhone p={p} at={3.9} x={80} />
  </ShotScene>
);
const S041: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const z = ease(ramp(frame, 3.6, 5.4));
  // report-hi.png: PDF page 1 at 220 dpi (about 1819 x 2573 px)
  const s = mix(0.4, 1.05, z), ty = mix(30, -1900 * 1.05 + 420, z);
  return (
    <ShotScene p={p}>
      <At from={0} to={3.0}><Shot name="reports" highlights={[{ key: 'pdf', from: 0.4, to: 3.0 }, { key: 'excel', from: 1.2, to: 3.0 }]} /></At>
      <At from={3.0}>
        <Bg color="#525659">
          <Img src={staticFile('shots/report-hi-1.png')} style={{ position: 'absolute', left: 960 - (1819 * s) / 2 + mix(0, 300, z), top: ty, width: 1819 * s, boxShadow: '0 6px 30px rgba(0,0,0,0.35)', ...fadeIn(frame - sec(3.0), 0) }} />
        </Bg>
      </At>
    </ShotScene>
  );
};
const S042: React.FC<P> = (p) => (
  <ShotScene p={p}>
    <At from={0} to={3.4}><Shot name="settings-roles" highlights={[{ key: 'roles', from: 0.3, to: 3.4 }]} /></At>
    <At from={3.4}><Shot name="settings-accounts" fadeAt={0} highlights={[{ key: 'viewer', from: 0.3, to: 9 }]} zoom={{ key: 'viewer', scale: 1.2, from: 0.2, to: 1.8 }} /></At>
  </ShotScene>
);
const S043: React.FC<P> = (p) => (
  <ShotScene p={p}>
    <At from={0} to={3.8}><Shot name="viewer-dashboard" highlights={[{ key: 'nav', from: 0.4, to: 3.8 }]} /></At>
    <At from={3.8}><Shot name="viewer-users" fadeAt={0} highlights={[{ key: 'row', from: 0.4, to: 9 }, { key: 'nav', from: 0.4, to: 9 }]} /></At>
  </ShotScene>
);

// ---------- Chapter 6 ----------
const S044: React.FC<P> = () => (
  <Split
    left={<Bedroom lamp={1}><Sokha x={SOKHA_X} y={SOKHA_Y} holding="phone" expr="smile" phoneLight={1} /></Bedroom>}
    right={<Office visitor><Dara x={DARA_X - 140} y={DARA_Y} expr="smile" look="side" /></Office>} />
);
const kn = (lang: Lang, s: string) => (lang === 'kh' ? s.replace('.', ',').replace(/[0-9]/g, (d) => '០១២៣៤៥៦៧៨៩'[+d]) : s);
const S045: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const stats: [string, string, number][] = [
    ['57', L(p.lang, 'សំណួរសាកល្បង', 'test questions'), 0.5], ['53', L(p.lang, 'ឆ្លើយត្រូវ', 'correct'), 2.5],
    ['4', L(p.lang, 'មិនត្រឹមត្រូវ', 'incorrect'), 3.5], ['≈ 92.98%', L(p.lang, 'ភាពត្រឹមត្រូវ', 'accuracy'), 6.0]];
  return (
    <Bg>
      <AbsoluteFill style={{ flexDirection: 'row', justifyContent: 'center', gap: 50, top: 170 }}>
        {stats.map(([n, l, at]) => (
          <div key={l} style={{ ...fadeUp(frame, at), width: n.length > 3 ? 460 : 300, textAlign: 'center', fontFamily: SANS }}>
            <div style={{ fontFamily: SERIF, fontSize: n.length > 3 ? 92 : 110, fontWeight: 600, color: C.text, whiteSpace: 'nowrap' }}>{kn(p.lang, n)}</div>
            <div style={{ fontSize: 32, color: C.sub }}>{l}</div>
          </div>
        ))}
      </AbsoluteFill>
      <div style={{ position: 'absolute', left: 260, top: 560, width: 1400, display: 'flex', gap: 4, ...fadeIn(frame, 2.4) }}>
        {Array.from({ length: 57 }, (_, i) => (
          <div key={i} style={{ flex: 1, height: 64, borderRadius: 3, background: i < 53 ? C.accent : '#D1D5DB', opacity: ramp(frame, 2.4 + i * 0.03, 2.6 + i * 0.03) }} />
        ))}
      </div>
      <div style={{ position: 'absolute', top: 680, width: '100%', textAlign: 'center', fontFamily: SANS, fontSize: 36, color: C.sub, ...fadeUp(frame, 6.6) }}>
        {kn(p.lang, '53 ÷ 57 × 100 ≈ 92.98%')}</div>
    </Bg>
  );
};
const S046: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  return (
    <Bg><AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', fontFamily: SANS, top: -60 }}>
      <div style={{ ...fadeUp(frame, 0.4), fontFamily: SERIF, fontSize: 54, fontWeight: 600, color: C.text, maxWidth: 1500, textAlign: 'center', lineHeight: 1.4 }}>{cap(p)}</div>
      <div style={{ ...fadeUp(frame, 1.2), fontSize: 34, color: C.sub, marginTop: 40 }}>{L(p.lang, 'មិនមែនការវាយតម្លៃសាធារណៈទ្រង់ទ្រាយធំទេ', 'Not a large public benchmark')}</div>
      <div style={{ ...fadeUp(frame, 1.8), fontSize: 24, color: C.muted, marginTop: 30, fontFamily: 'monospace' }}>docs/evaluation/test_questions.csv</div>
    </AbsoluteFill></Bg>
  );
};
const S047: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const pts: [string, boolean][] = [[L(p.lang, 'គំរូសាកល្បងរួច', 'Prototype tested'), true], [L(p.lang, 'ដាក់ឱ្យដំណើរការ', 'Deploy'), false], [L(p.lang, 'សាកល្បងជាមួយនិស្សិតពិត', 'Test with real students'), false]];
  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', inset: 0, opacity: 0.35 }}><Campus people pan={false} /></div>
      <AbsoluteFill style={{ background: 'rgba(250,249,246,0.6)' }} />
      <svg width={1920} height={1080} style={{ position: 'absolute', inset: 0 }}><Line x1={420} y1={470} x2={1500} y2={470} at={0.6} /></svg>
      {pts.map(([t, done], i) => (
        <div key={t} style={{ position: 'absolute', left: 420 + i * 540 - 190, top: 430, width: 380, textAlign: 'center', fontFamily: SANS, ...fadeUp(frame, 0.8 + i * 1.0) }}>
          <div style={{ width: 80, height: 80, margin: '0 auto', borderRadius: '50%', background: done ? C.accent : '#fff', border: `4px solid ${C.accent}`, color: '#fff', fontSize: 40, lineHeight: '72px' }}>{done ? '✓' : ''}</div>
          <div style={{ fontSize: 36, fontWeight: 600, color: C.text, marginTop: 22 }}>{t}</div>
        </div>
      ))}
    </AbsoluteFill>
  );
};
const S048: React.FC<P> = (p) => (
  <AbsoluteFill>
    <PresenterPlaceholder lang={p.lang} />
    <div style={{ position: 'absolute', top: 860, width: '100%' }}><Title lines={[L(p.lang, 'សូមអរគុណ', 'Thank you')]} size={64} at={0.6} /></div>
  </AbsoluteFill>
);
const S049: React.FC<P> = (p) => {
  const frame = useCurrentFrame();
  const lines = cap(p).split('\n');
  return (
    <Bg><AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', fontFamily: SANS }}>
      {lines.map((l, i) => <div key={i} style={{ ...fadeUp(frame, 0.3 + i * 0.3), fontSize: i === 0 ? 46 : 34, fontFamily: i === 0 ? SERIF : SANS, fontWeight: i === 0 ? 600 : 400,
        color: i === lines.length - 1 ? C.muted : i === 0 ? C.text : C.sub, marginTop: i === lines.length - 1 ? 40 : 16 }}>{l}</div>)}
    </AbsoluteFill></Bg>
  );
};

export const SCENES: Record<string, React.FC<P>> = {
  'SC-001': S001, 'SC-002': S002, 'SC-003': S003, 'SC-004': S004, 'SC-005': S005, 'SC-006': S006, 'SC-007': S007, 'SC-008': S008, 'SC-009': S009,
  'SC-010': S010, 'SC-011': S011, 'SC-012': S012, 'SC-013': S013, 'SC-014': S014, 'SC-015': S015, 'SC-016': S016, 'SC-017': S017, 'SC-018': S018,
  'SC-019': S019, 'SC-020': S020, 'SC-021': S021, 'SC-022': S022, 'SC-023': S023, 'SC-024': S024, 'SC-025': S025, 'SC-026': S026, 'SC-027': S027,
  'SC-028': S028, 'SC-029': S029, 'SC-030': S030, 'SC-031': S031, 'SC-032': S032, 'SC-033': S033, 'SC-034': S034, 'SC-035': S035, 'SC-036': S036,
  'SC-037': S037, 'SC-038': S038, 'SC-039': S039, 'SC-040': S040, 'SC-041': S041, 'SC-042': S042, 'SC-043': S043, 'SC-044': S044, 'SC-045': S045,
  'SC-046': S046, 'SC-047': S047, 'SC-048': S048, 'SC-049': S049,
};
export const SCENE_LIST = scenesData as unknown as SceneInfo[];
export { between };
