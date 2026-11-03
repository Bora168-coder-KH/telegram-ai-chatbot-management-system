import { ChatItem, Toast } from '../ui/Phone';
import transcript from './transcript.json';
import outbox from './outbox.json';

// Real bot texts, captured by playing the story through the project's own handlers (branch feature/all-screens).
type Step = { user?: string; tap?: string; bot: { text: string; buttons: string[][]; kind: string }[]; toast?: string[] };
const S = (transcript as { sokha: Step[]; student_b: Step[] }).sokha;
const B = (transcript as { sokha: Step[]; student_b: Step[] }).student_b;
const toSokha = (outbox as { chat_id: number; text: string }[]).filter((m) => m.chat_id === 8100001).map((m) => m.text);

const KH_CHOOSE_LANGUAGE = 'សូមជ្រើសរើសភាសារបស់អ្នក៖'; // app/i18n.py "choose_language" (km)

export const SOKHA_CHAT: ChatItem[] = [
  // SC-020 /start, choose Khmer
  { from: 'user', text: '/start', typeFrom: ['SC-020', 2.4], at: ['SC-020', 3.2] },
  { from: 'bot', text: S[0].bot[0].text, buttons: S[0].bot[0].buttons, at: ['SC-020', 3.9], removeButtonsAt: ['SC-020', 5.6], tap: { label: 'ខ្មែរ', at: ['SC-020', 5.0] } },
  { from: 'bot', text: S[1].bot[0].text, keyboard: S[1].bot[0].buttons, at: ['SC-020', 5.9] },
  // SC-021 the Khmer question
  { from: 'user', text: S[2].user!, typeFrom: ['SC-021', 0.6], at: ['SC-021', 4.6] },
  // SC-022 instant FAQ answer
  { from: 'bot', text: S[2].bot[0].text, buttons: S[2].bot[0].buttons, at: ['SC-022', 0.5], highlight: [['SC-022', 1.3], ['SC-022', 5.2]],
    removeButtonsAt: ['SC-023', 1.5], tap: { label: '👍', at: ['SC-023', 1.0] } },
  // SC-024 switch to English
  { from: 'user', text: '🌐 ភាសា', at: ['SC-024', 0.9] },
  { from: 'bot', text: KH_CHOOSE_LANGUAGE, buttons: [['English', 'ខ្មែរ']], at: ['SC-024', 1.5], removeButtonsAt: ['SC-024', 3.1], tap: { label: 'English', at: ['SC-024', 2.6] } },
  { from: 'bot', text: S[4].bot[0].text, keyboard: S[4].bot[0].buttons, at: ['SC-024', 3.4] },
  // SC-025 paraphrase in English
  { from: 'user', text: S[5].user!, typeFrom: ['SC-025', 0.4], at: ['SC-025', 3.4] },
  { from: 'bot', text: S[5].bot[0].text, buttons: S[5].bot[0].buttons, at: ['SC-025', 4.1], highlight: [['SC-025', 4.6], ['SC-025', 7.5]] },
  // SC-026 date capture
  { from: 'user', text: S[6].user!, typeFrom: ['SC-026', 0.4], at: ['SC-026', 3.4], highlight: [['SC-026', 4.8], ['SC-026', 9.4]], highlightText: '2026-12-15' },
  { from: 'bot', text: S[6].bot[0].text, buttons: S[6].bot[0].buttons, at: ['SC-026', 4.2], highlight: [['SC-026', 5.2], ['SC-026', 9.4]], highlightText: '2026-12-15' },
  // SC-027 unknown question
  { from: 'user', text: S[7].user!, typeFrom: ['SC-027', 0.5], at: ['SC-027', 3.0] },
  // SC-028 honest fallback
  { from: 'bot', text: S[7].bot[0].text, buttons: S[7].bot[0].buttons, at: ['SC-028', 0.5],
    highlight: [['SC-028', 1.4], ['SC-028', 4.0]], removeButtonsAt: ['SC-029', 1.3], tap: { label: 'Human Support', at: ['SC-029', 0.9] } },
  // SC-029 handoff
  { from: 'bot', text: S[8].bot[0].text, at: ['SC-029', 1.6], highlight: [['SC-029', 2.2], ['SC-029', 5.6]] },
  // Chapter 5: messages sent from the dashboard (captured from the dashboard's own send function)
  { from: 'bot', text: toSokha[0], at: ['SC-034', 4.6], highlight: [['SC-034', 5.0], ['SC-034', 7.8]] },
  { from: 'bot', text: toSokha[1], at: ['SC-035', 3.0], highlight: [['SC-035', 3.4], ['SC-035', 5.8]] },
  { from: 'bot', text: toSokha[2], at: ['SC-040', 4.4], highlight: [['SC-040', 4.8], ['SC-040', 6.8]] },
];

export const SOKHA_TOASTS: Toast[] = [{ text: S[3].toast![0], from: ['SC-023', 1.2], to: ['SC-023', 4.6] }];

export const STUDENT_B_CHAT: ChatItem[] = [
  { from: 'user', text: B[2].user!, typeFrom: ['SC-038', 0.4], at: ['SC-038', 3.0] },
  { from: 'bot', text: B[2].bot[0].text, buttons: B[2].bot[0].buttons, at: ['SC-038', 3.8], highlight: [['SC-038', 4.3], ['SC-038', 7.6]] },
];

export const WELCOME_KH = S[1].bot[0];
export const WELCOME_EN = S[4].bot[0];
export const FALLBACK_TEXT = S[7].bot[0].text;
export const FALLBACK_BUTTONS = S[7].bot[0].buttons;
export const ANSWER_EN = S[5].bot[0].text;
export const ANSWER_KH = S[2].bot[0].text;
export const FAQ_ANSWER_NEW = B[2].bot[0].text;
