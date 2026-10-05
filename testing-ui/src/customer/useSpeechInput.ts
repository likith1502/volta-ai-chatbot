import { useCallback, useEffect, useRef, useState } from 'react';

/**
 * Speech-to-text using the browser's Web Speech API (Chrome, Edge, Safari).
 * This is an accessibility INPUT method only: the recognised text is sent
 * through the normal chat, so all booking rules (explicit confirmation etc.)
 * still apply. It is not the Voice Agent (no text-to-speech, no phone calls).
 *
 * Privacy: Chrome/Edge send audio to the browser vendor's speech service.
 */

export const SPEECH_LANGUAGES = [
  { code: 'en-IN', label: 'English' },
  { code: 'hi-IN', label: 'हिन्दी' },
  { code: 'te-IN', label: 'తెలుగు' },
] as const;

// Minimal typings: the Web Speech API isn't in TypeScript's DOM lib yet.
interface SpeechRecognitionResultLike {
  isFinal: boolean;
  0: { transcript: string };
}
interface SpeechRecognitionEventLike {
  resultIndex: number;
  results: ArrayLike<SpeechRecognitionResultLike>;
}
interface SpeechRecognitionLike {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  maxAlternatives: number;
  onresult: ((e: SpeechRecognitionEventLike) => void) | null;
  onerror: ((e: { error: string }) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
  abort(): void;
}
type SpeechRecognitionCtor = new () => SpeechRecognitionLike;

function getRecognitionCtor(): SpeechRecognitionCtor | null {
  const w = window as unknown as {
    SpeechRecognition?: SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

const ERROR_MESSAGES: Record<string, string> = {
  'not-allowed': 'Microphone permission was blocked. Allow the microphone in your browser (lock icon in the address bar) and try again.',
  'service-not-allowed': 'Microphone permission was blocked. Allow the microphone in your browser and try again.',
  'no-speech': "I didn't hear anything. Tap the mic and speak again.",
  'audio-capture': 'No microphone was found. Please connect a microphone.',
  network: 'Voice input needs an internet connection. Please check your connection.',
};

interface Options {
  lang: string;
  /** Live text while the person is speaking. */
  onInterim: (text: string) => void;
  /** Final text once they stop speaking. */
  onFinal: (text: string) => void;
}

export function useSpeechInput({ lang, onInterim, onFinal }: Options) {
  const [isSupported] = useState(() => typeof window !== 'undefined' && !!getRecognitionCtor());
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recRef = useRef<SpeechRecognitionLike | null>(null);
  const finalRef = useRef('');
  const cbRef = useRef({ onInterim, onFinal });
  cbRef.current = { onInterim, onFinal };

  const stop = useCallback(() => {
    recRef.current?.stop();
  }, []);

  const start = useCallback(() => {
    const Ctor = getRecognitionCtor();
    if (!Ctor) return;
    recRef.current?.abort();
    const rec = new Ctor();
    rec.lang = lang;
    rec.interimResults = true;
    rec.continuous = false; // stops automatically after a pause
    rec.maxAlternatives = 1;
    finalRef.current = '';
    setError(null);

    rec.onresult = e => {
      let interim = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const r = e.results[i];
        if (r.isFinal) finalRef.current += r[0].transcript;
        else interim += r[0].transcript;
      }
      cbRef.current.onInterim((finalRef.current + interim).trim());
    };
    rec.onerror = e => {
      if (e.error !== 'aborted') {
        setError(ERROR_MESSAGES[e.error] ?? 'Voice input stopped unexpectedly. Please try again.');
      }
    };
    rec.onend = () => {
      setIsListening(false);
      recRef.current = null;
      const text = finalRef.current.trim();
      if (text) cbRef.current.onFinal(text);
    };

    recRef.current = rec;
    try {
      rec.start();
      setIsListening(true);
    } catch {
      setError('Could not start the microphone. Please try again.');
    }
  }, [lang]);

  useEffect(() => () => recRef.current?.abort(), []);

  return { isSupported, isListening, error, clearError: () => setError(null), start, stop };
}
