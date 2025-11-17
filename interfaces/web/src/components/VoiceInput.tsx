import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Loader2, Play, RotateCcw, Send } from 'lucide-react';
import { Button } from './ui/button';
import { multimodalService } from '@/services/multimodalService';
import { cn } from '@/lib/utils';

/**
 * Props for the VoiceInput component
 */
interface VoiceInputProps {
  /** Callback fired when audio transcription completes successfully */
  onTranscription: (result: { text: string; language: string }) => void;
  /** Callback fired when an error occurs during recording or transcription */
  onError?: (error: string) => void;
  /** Language code for transcription (e.g., 'en', 'pt'). If not specified, auto-detects */
  language?: string;
  /** Additional CSS classes to apply to the component */
  className?: string;
}

/**
 * VoiceInput Component
 *
 * A fully accessible voice recording and transcription component using
 * OpenAI Whisper API for speech-to-text conversion.
 *
 * @example
 * ```tsx
 * <VoiceInput
 *   onTranscription={(result) => {
 *     console.log('Text:', result.text);
 *     console.log('Language:', result.language);
 *   }}
 *   onError={(error) => console.error(error)}
 *   language="pt"
 * />
 * ```
 *
 * @features
 * - Browser-based audio recording (MediaRecorder API)
 * - Real-time recording timer
 * - Audio preview with playback controls
 * - Re-record functionality
 * - Keyboard accessible with ARIA labels
 * - Screen reader announcements
 * - Automatic cleanup of media resources
 *
 * @supported-formats Recorded as WebM audio
 * @max-file-size 25MB (enforced by multimodalService)
 */
const VoiceInputComponent: React.FC<VoiceInputProps> = ({
  onTranscription,
  onError,
  language,
  className,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current !== null) {
        window.clearInterval(timerRef.current);
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
      // Stop media stream tracks
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop());
      }
      stopRecording();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [audioUrl]);

  const startRecording = async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      // Create media recorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // Handle data available
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Handle recording stop
      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

        // Stop all tracks
        if (mediaStreamRef.current) {
          mediaStreamRef.current.getTracks().forEach((track) => track.stop());
          mediaStreamRef.current = null;
        }

        // Save blob and create preview URL
        setAudioBlob(blob);
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
      };

      // Start recording
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      timerRef.current = window.setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      onError?.('Failed to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      if (timerRef.current !== null) {
        window.clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const handleTranscribe = async () => {
    if (!audioBlob) return;

    try {
      setIsProcessing(true);

      // Convert blob to file
      const file = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });

      // Transcribe audio
      const result = await multimodalService.transcribeAudio(file, language);

      // Call callback with transcription
      onTranscription(result);

      // Reset state
      handleReset();
    } catch (error) {
      console.error('Error processing audio:', error);
      onError?.(
        error instanceof Error
          ? error.message
          : 'Erro ao transcrever áudio. Por favor, tente novamente.'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioBlob(null);
    setAudioUrl(null);
    setRecordingTime(0);
  };

  const handleReRecord = () => {
    handleReset();
    startRecording();
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={cn('space-y-3', className)} role="region" aria-label="Voice recording">
      {/* Live region for screen reader announcements */}
      <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
        {isRecording && `Recording... ${formatTime(recordingTime)}`}
        {isProcessing && 'Processing transcription...'}
        {audioUrl && !isProcessing && 'Recording ready. Use audio controls to play or transcribe.'}
      </div>

      {/* Recording controls */}
      {!audioUrl && (
        <div className="flex items-center gap-2">
          {/* Recording button */}
          <Button
            variant={isRecording ? 'destructive' : 'outline'}
            size="sm"
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
            aria-label={isRecording ? 'Stop recording voice input' : 'Start recording voice input'}
            aria-pressed={isRecording}
            title={isRecording ? 'Parar gravação' : 'Gravar entrada de voz'}
          >
            {isProcessing ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
            ) : isRecording ? (
              <MicOff className="mr-2 h-4 w-4" aria-hidden="true" />
            ) : (
              <Mic className="mr-2 h-4 w-4" aria-hidden="true" />
            )}
            {isRecording ? 'Parar Gravação' : 'Iniciar Gravação'}
          </Button>

          {/* Recording indicator */}
          {isRecording && (
            <div className="flex items-center gap-2 text-sm text-destructive" role="timer" aria-label={`Recording time: ${formatTime(recordingTime)}`}>
              <span className="relative flex h-2 w-2" aria-hidden="true">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-destructive opacity-75"></span>
                <span className="relative inline-flex h-2 w-2 rounded-full bg-destructive"></span>
              </span>
              <span className="font-mono">{formatTime(recordingTime)}</span>
            </div>
          )}
        </div>
      )}

      {/* Audio preview */}
      {audioUrl && !isProcessing && (
        <div className="space-y-3 rounded-md border border-border bg-muted/30 p-3" role="group" aria-label="Recorded audio preview">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Play className="h-4 w-4" aria-hidden="true" />
            <span>Preview do áudio gravado ({formatTime(recordingTime)})</span>
          </div>

          {/* Audio player */}
          <audio
            ref={audioRef}
            controls
            className="w-full"
            src={audioUrl}
            aria-label={`Recorded audio preview, duration ${formatTime(recordingTime)}`}
          />

          {/* Action buttons */}
          <div className="flex gap-2" role="group" aria-label="Audio actions">
            <Button
              variant="outline"
              size="sm"
              onClick={handleReRecord}
              disabled={isProcessing}
              aria-label="Re-record audio"
            >
              <RotateCcw className="mr-2 h-4 w-4" aria-hidden="true" />
              Re-gravar
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={handleTranscribe}
              disabled={isProcessing}
              aria-label={`Transcribe recorded audio, duration ${formatTime(recordingTime)}`}
            >
              <Send className="mr-2 h-4 w-4" aria-hidden="true" />
              Transcrever
            </Button>
          </div>
        </div>
      )}

      {/* Processing indicator */}
      {isProcessing && (
        <div
          className="flex items-center gap-2 text-sm text-muted-foreground"
          role="status"
          aria-label="Processing transcription"
        >
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          <span>Processando transcrição...</span>
        </div>
      )}
    </div>
  );
};

/**
 * Memoized VoiceInput component to prevent unnecessary re-renders.
 * Only re-renders when props change.
 */
export const VoiceInput = React.memo(VoiceInputComponent);
