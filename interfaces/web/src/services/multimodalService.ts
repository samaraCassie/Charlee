import api from './api';

// ==================== Types ====================

export interface TranscriptionResponse {
  text: string;
  language: string;
  success: boolean;
}

export interface ImageAnalysisResponse {
  analysis: string;
  tasks: Array<{
    description: string;
    source: string;
  }>;
  success: boolean;
}

export interface MultimodalProcessResponse {
  success: boolean;
  message: string;
  transcription?: string;
  analysis?: string;
  tasks_created: number[];
}

// ==================== Multimodal Service ====================

export const multimodalService = {
  /**
   * Transcribe audio file to text using OpenAI Whisper.
   *
   * Supported formats: mp3, wav, m4a, webm, ogg, flac
   * Max file size: 25 MB
   */
  async transcribeAudio(
    file: File,
    language?: string
  ): Promise<TranscriptionResponse> {
    const formData = new FormData();
    formData.append('file', file);

    if (language) {
      formData.append('language', language);
    }

    const response = await api.post('/v2/multimodal/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * Analyze image using GPT-4o Vision API.
   *
   * Use cases:
   * - Extract tasks from handwritten planner
   * - Analyze screenshot of email and create tasks
   * - Read scribbled notes and add to inbox
   *
   * Supported formats: png, jpg, jpeg, heic, webp
   * Max file size: 20 MB
   */
  async analyzeImage(
    file: File,
    prompt?: string
  ): Promise<ImageAnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);

    if (prompt) {
      formData.append('prompt', prompt);
    }

    const response = await api.post('/v2/multimodal/analyze-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * Process audio or image file and automatically create tasks.
   *
   * Unified endpoint that:
   * 1. Detects file type (audio or image)
   * 2. Processes with appropriate service (Whisper or Vision)
   * 3. Extracts tasks from content
   * 4. Creates tasks in database if auto_create_tasks=true
   * 5. Returns processing result with created task IDs
   */
  async processMultimodal(
    file: File,
    options?: {
      autoCreateTasks?: boolean;
      bigRockId?: number;
    }
  ): Promise<MultimodalProcessResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('auto_create_tasks', String(options?.autoCreateTasks ?? true));

    if (options?.bigRockId) {
      formData.append('big_rock_id', String(options.bigRockId));
    }

    const response = await api.post('/v2/multimodal/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * Validate file size and type before upload.
   *
   * @param file - File to validate
   * @param type - 'audio' or 'image'
   * @returns true if valid, throws error if invalid
   */
  validateFile(file: File, type: 'audio' | 'image'): boolean {
    const audioFormats = ['mp3', 'wav', 'm4a', 'webm', 'ogg', 'flac'];
    const imageFormats = ['png', 'jpg', 'jpeg', 'heic', 'webp'];

    const maxAudioSize = 25 * 1024 * 1024; // 25 MB
    const maxImageSize = 20 * 1024 * 1024; // 20 MB

    // Get file extension
    const extension = file.name.split('.').pop()?.toLowerCase();

    if (!extension) {
      throw new Error('File has no extension');
    }

    // Validate format
    if (type === 'audio') {
      if (!audioFormats.includes(extension)) {
        throw new Error(
          `Unsupported audio format: ${extension}. Supported formats: ${audioFormats.join(', ')}`
        );
      }

      if (file.size > maxAudioSize) {
        throw new Error(
          `File size (${(file.size / 1024 / 1024).toFixed(2)} MB) exceeds maximum allowed size (25 MB)`
        );
      }
    } else if (type === 'image') {
      if (!imageFormats.includes(extension)) {
        throw new Error(
          `Unsupported image format: ${extension}. Supported formats: ${imageFormats.join(', ')}`
        );
      }

      if (file.size > maxImageSize) {
        throw new Error(
          `File size (${(file.size / 1024 / 1024).toFixed(2)} MB) exceeds maximum allowed size (20 MB)`
        );
      }
    }

    return true;
  },

  /**
   * Get supported formats for a file type.
   */
  getSupportedFormats(type: 'audio' | 'image'): string[] {
    const audioFormats = ['mp3', 'wav', 'm4a', 'webm', 'ogg', 'flac'];
    const imageFormats = ['png', 'jpg', 'jpeg', 'heic', 'webp'];

    return type === 'audio' ? audioFormats : imageFormats;
  },
};
