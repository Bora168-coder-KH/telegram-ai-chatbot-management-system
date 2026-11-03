import { interpolate, spring } from 'remotion';
import { FPS } from './style';

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
export const sec = (s: number) => Math.round(s * FPS);
/** 0 -> 1 between two times (seconds). */
export const ramp = (frame: number, from: number, to: number) => interpolate(frame, [sec(from), sec(to)], [0, 1], clamp);
/** opacity + translateY for a fade-up entrance starting at `at` seconds. */
export const fadeUp = (frame: number, at: number, dist = 24, len = 0.45) => {
  const p = ramp(frame, at, at + len);
  const e = 1 - Math.pow(1 - p, 3);
  return { opacity: e, transform: `translateY(${(1 - e) * dist}px)` };
};
export const fadeIn = (frame: number, at: number, len = 0.4) => ({ opacity: ramp(frame, at, at + len) });
export const pop = (frame: number, at: number) =>
  spring({ frame: frame - sec(at), fps: FPS, config: { damping: 14, stiffness: 160, mass: 0.6 } });
/** visible between two times, with short fades. */
export const between = (frame: number, from: number, to: number, f = 0.3) =>
  Math.min(ramp(frame, from, from + f), 1 - ramp(frame, to - f, to));
export const ease = (p: number) => (p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2);
export const mix = (a: number, b: number, p: number) => a + (b - a) * p;
