import React from 'react';
import { Composition } from 'remotion';
import { Video } from './Video';
import { SCENE_LIST } from './scenes/Scenes';
import './style';

const total = Math.round(SCENE_LIST.reduce((a, s) => a + s.dur, 0) * 25);

export const Root: React.FC = () => (
  <>
    <Composition id="VideoKH" component={Video} durationInFrames={total} fps={25} width={1920} height={1080} defaultProps={{ lang: 'kh' as const }} />
    <Composition id="VideoEN" component={Video} durationInFrames={total} fps={25} width={1920} height={1080} defaultProps={{ lang: 'en' as const }} />
  </>
);
