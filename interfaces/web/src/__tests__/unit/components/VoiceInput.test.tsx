import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { VoiceInput } from '@/components/VoiceInput';
import * as multimodalService from '@/services/multimodalService';

// Mock the multimodal service
vi.mock('@/services/multimodalService');

// Mock MediaRecorder
class MockMediaRecorder {
  state = 'inactive';
  ondataavailable: ((event: { data: Blob }) => void) | null = null;
  onstop: (() => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  start() {
    this.state = 'recording';
  }

  stop() {
    this.state = 'inactive';
    if (this.ondataavailable) {
      const blob = new Blob(['fake audio data'], { type: 'audio/webm' });
      this.ondataavailable({ data: blob });
    }
    if (this.onstop) {
      this.onstop();
    }
  }

  addEventListener(event: string, handler: any) {
    if (event === 'dataavailable') {
      this.ondataavailable = handler;
    } else if (event === 'stop') {
      this.onstop = handler;
    } else if (event === 'error') {
      this.onerror = handler;
    }
  }

  removeEventListener() {}
}

describe('VoiceInput', () => {
  let mockGetUserMedia: any;
  let mockMediaRecorder: typeof MockMediaRecorder;

  beforeEach(() => {
    // Setup MediaRecorder mock
    mockMediaRecorder = MockMediaRecorder as any;
    global.MediaRecorder = mockMediaRecorder as any;
    (global.MediaRecorder as any).isTypeSupported = () => true;

    // Setup getUserMedia mock
    mockGetUserMedia = vi.fn().mockResolvedValue({
      getTracks: () => [{ stop: vi.fn() }],
    });

    Object.defineProperty(global.navigator, 'mediaDevices', {
      value: {
        getUserMedia: mockGetUserMedia,
      },
      writable: true,
      configurable: true,
    });

    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should render voice input button', () => {
    const onTranscription = vi.fn();
    const onError = vi.fn();

    render(<VoiceInput onTranscription={onTranscription} onError={onError} />);

    expect(screen.getByText('Iniciar Gravação')).toBeInTheDocument();
  });

  it('should request microphone permission on record start', async () => {
    const onTranscription = vi.fn();
    const onError = vi.fn();

    render(<VoiceInput onTranscription={onTranscription} onError={onError} />);

    const recordButton = screen.getByText('Iniciar Gravação');
    fireEvent.click(recordButton);

    await waitFor(() => {
      expect(mockGetUserMedia).toHaveBeenCalledWith({ audio: true });
    });
  });

  it('should show recording state when recording', async () => {
    const onTranscription = vi.fn();
    const onError = vi.fn();

    render(<VoiceInput onTranscription={onTranscription} onError={onError} />);

    const recordButton = screen.getByText('Iniciar Gravação');
    fireEvent.click(recordButton);

    await waitFor(() => {
      expect(screen.getByText('Parar Gravação')).toBeInTheDocument();
    });
  });

  it('should stop recording and transcribe audio', async () => {
    const onTranscription = vi.fn();
    const onError = vi.fn();

    const mockTranscriptionResponse = {
      text: 'Test transcription',
      language: 'pt',
    };

    vi.mocked(multimodalService.multimodalService.transcribeAudio).mockResolvedValue(
      mockTranscriptionResponse
    );

    render(<VoiceInput onTranscription={onTranscription} onError={onError} language="pt" />);

    // Start recording
    const recordButton = screen.getByText('Iniciar Gravação');
    fireEvent.click(recordButton);

    await waitFor(() => {
      expect(screen.getByText('Parar Gravação')).toBeInTheDocument();
    });

    // Stop recording
    const stopButton = screen.getByText(/Parar/i);
    fireEvent.click(stopButton);

    await waitFor(() => {
      expect(multimodalService.multimodalService.transcribeAudio).toHaveBeenCalled();
      expect(onTranscription).toHaveBeenCalledWith(mockTranscriptionResponse);
    });
  });

  it('should handle transcription errors', async () => {
    const onTranscription = vi.fn();
    const onError = vi.fn();

    vi.mocked(multimodalService.multimodalService.transcribeAudio).mockRejectedValue(
      new Error('Transcription failed')
    );

    render(<VoiceInput onTranscription={onTranscription} onError={onError} />);

    // Start recording
    const recordButton = screen.getByText('Iniciar Gravação');
    fireEvent.click(recordButton);

    await waitFor(() => {
      expect(screen.getByText('Parar Gravação')).toBeInTheDocument();
    });

    // Stop recording
    const stopButton = screen.getByText(/Parar/i);
    fireEvent.click(stopButton);

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith(expect.stringContaining('Erro ao transcrever áudio'));
    });
  });

  it('should handle microphone permission denied', async () => {
    const onTranscription = vi.fn();
    const onError = vi.fn();

    mockGetUserMedia.mockRejectedValue(new Error('Permission denied'));

    render(<VoiceInput onTranscription={onTranscription} onError={onError} />);

    const recordButton = screen.getByText('Iniciar Gravação');
    fireEvent.click(recordButton);

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith(
        expect.stringContaining('Failed to access microphone')
      );
    });
  });

  it('should display recording timer', async () => {
    const onTranscription = vi.fn();
    const onError = vi.fn();

    vi.useFakeTimers();

    render(<VoiceInput onTranscription={onTranscription} onError={onError} />);

    const recordButton = screen.getByText('Iniciar Gravação');
    fireEvent.click(recordButton);

    await waitFor(() => {
      expect(screen.getByText('Parar Gravação')).toBeInTheDocument();
    });

    // Advance timer by 2 seconds
    vi.advanceTimersByTime(2000);

    await waitFor(() => {
      expect(screen.getByText(/0:02/)).toBeInTheDocument();
    });

    vi.useRealTimers();
  });

  it('should clean up media stream on unmount', async () => {
    const onTranscription = vi.fn();
    const onError = vi.fn();

    const stopMock = vi.fn();
    mockGetUserMedia.mockResolvedValue({
      getTracks: () => [{ stop: stopMock }],
    });

    const { unmount } = render(<VoiceInput onTranscription={onTranscription} onError={onError} />);

    const recordButton = screen.getByText('Iniciar Gravação');
    fireEvent.click(recordButton);

    await waitFor(() => {
      expect(screen.getByText('Parar Gravação')).toBeInTheDocument();
    });

    unmount();

    expect(stopMock).toHaveBeenCalled();
  });

  it('should show processing state while transcribing', async () => {
    const onTranscription = vi.fn();
    const onError = vi.fn();

    let resolveTranscription: any;
    const transcriptionPromise = new Promise((resolve) => {
      resolveTranscription = resolve;
    });

    vi.mocked(multimodalService.multimodalService.transcribeAudio).mockReturnValue(
      transcriptionPromise as any
    );

    render(<VoiceInput onTranscription={onTranscription} onError={onError} />);

    // Start recording
    const recordButton = screen.getByText('Iniciar Gravação');
    fireEvent.click(recordButton);

    await waitFor(() => {
      expect(screen.getByText('Parar Gravação')).toBeInTheDocument();
    });

    // Stop recording
    const stopButton = screen.getByText(/Parar/i);
    fireEvent.click(stopButton);

    await waitFor(() => {
      expect(screen.getByText('Processando transcrição...')).toBeInTheDocument();
    });

    // Resolve transcription
    resolveTranscription({ text: 'Test', language: 'pt' });

    await waitFor(() => {
      expect(onTranscription).toHaveBeenCalled();
    });
  });
});
