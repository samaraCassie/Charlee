import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Loader2, Play, RotateCcw, Send } from 'lucide-react';
import { Button } from './ui/button';
import { multimodalService } from '@/services/multimodalService';
import { cn } from '@/lib/utils';

interface VoiceInputProps {
  onTranscription: (result: { text: string; language: string }) => void;
  onError?: (error: string) => void;
  language?: string; // Optional language code (e.g., 'en', 'pt')
  className?: string;
}

export const VoiceInput: React.FC<VoiceInputProps> = ({
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
    <div className={cn('space-y-3', className)}>
      {/* Recording controls */}
      {!audioUrl && (
        <div className="flex items-center gap-2">
          {/* Recording button */}
          <Button
            variant={isRecording ? 'destructive' : 'outline'}
            size="sm"
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
            aria-label={isRecording ? 'Parar gravação' : 'Iniciar gravação'}
            title={isRecording ? 'Parar gravação' : 'Gravar entrada de voz'}
          >
            {isProcessing ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : isRecording ? (
              <MicOff className="mr-2 h-4 w-4" />
            ) : (
              <Mic className="mr-2 h-4 w-4" />
            )}
            {isRecording ? 'Parar Gravação' : 'Iniciar Gravação'}
          </Button>

          {/* Recording indicator */}
          {isRecording && (
            <div className="flex items-center gap-2 text-sm text-destructive">
              <span className="relative flex h-2 w-2">
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
        <div className="space-y-3 rounded-md border border-border bg-muted/30 p-3">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Play className="h-4 w-4" />
            <span>Preview do áudio gravado ({formatTime(recordingTime)})</span>
          </div>

          {/* Audio player */}
          <audio
            ref={audioRef}
            controls
            className="w-full"
            src={audioUrl}
          />

          {/* Action buttons */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleReRecord}
              disabled={isProcessing}
            >
              <RotateCcw className="mr-2 h-4 w-4" />
              Re-gravar
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={handleTranscribe}
              disabled={isProcessing}
            >
              <Send className="mr-2 h-4 w-4" />
              Transcrever
            </Button>
          </div>
        </div>
      )}

      {/* Processing indicator */}
      {isProcessing && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Processando transcrição...</span>
        </div>
      )}
    </div>
  );
};
