import React, { useEffect, useState } from 'react';
import { AbsoluteFill, Sequence, continueRender, delayRender, useCurrentFrame } from 'remotion';
import { SCENES, SCENE_LIST } from './scenes/Scenes';
import { Subtitles } from './ui/Text';
import { ramp } from './anim';
import { Lang, C, FONT_PROBES } from './style';

// Fades to and from black at chapter breaks (from the storyboard transitions).
const FADE_IN_BLACK = new Set(['SC-001', 'SC-006', 'SC-030', 'SC-044']);
const FADE_OUT_BLACK = new Set(['SC-005', 'SC-029', 'SC-043', 'SC-049']);

const Fades: React.FC<{ id: string; dur: number }> = ({ id, dur }) => {
  const frame = useCurrentFrame();
  let o = 0;
  if (FADE_IN_BLACK.has(id)) o = Math.max(o, 1 - ramp(frame, 0, id === 'SC-001' ? 1 : 0.6));
  if (FADE_OUT_BLACK.has(id)) o = Math.max(o, ramp(frame, dur - (id === 'SC-049' ? 1 : 0.6), dur));
  return o > 0 ? <AbsoluteFill style={{ background: '#000', opacity: o, zIndex: 100 }} /> : null;
};

/** Wait until the embedded fonts are ready (Remotion's documented pattern for fonts). */
const useFonts = () => {
  const [handle] = useState(() => delayRender('fonts', { timeoutInMilliseconds: 20000 }));
  useEffect(() => {
    Promise.all(FONT_PROBES.map((f) => document.fonts.load(f, f.includes('Kantumruy') ? 'ក' : 'A')))
      .then(() => document.fonts.ready)
      .finally(() => continueRender(handle));
  }, [handle]);
};

export const Video: React.FC<{ lang: Lang; only?: string }> = (props) => {
  useFonts();
  return <VideoInner {...props} />;
};

const VideoInner: React.FC<{ lang: Lang; only?: string }> = ({ lang, only }) => (
  <AbsoluteFill style={{ background: C.bg }}>
    {SCENE_LIST.filter((s) => !only || s.id === only).map((s) => {
      const Scene = SCENES[s.id];
      return (
        <Sequence key={s.id} from={only ? 0 : Math.round(s.start * 25)} durationInFrames={Math.round(s.dur * 25)} name={`${s.id} ${s.id}`}>
          <Scene lang={lang} info={s} />
          <Subtitles cues={lang === 'kh' ? s.subKh : s.subEn} lang={lang} />
          <Fades id={s.id} dur={s.dur} />
        </Sequence>
      );
    })}
  </AbsoluteFill>
);
