import { describe, it, expect, vi, beforeEach } from 'vitest';
import { multimodalService } from '@/services/multimodalService';
import api from '@/services/api';

vi.mock('@/services/api');

describe('multimodalService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('transcribeAudio', () => {
    it('should transcribe audio file successfully', async () => {
      const mockResponse = {
        data: {
          text: 'This is a test transcription',
          language: 'en',
        },
      };

      vi.mocked(api.post).mockResolvedValue(mockResponse);

      const audioFile = new File(['fake audio'], 'test.mp3', { type: 'audio/mp3' });
      const result = await multimodalService.transcribeAudio(audioFile);

      expect(api.post).toHaveBeenCalledWith(
        '/v2/multimodal/transcribe',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      expect(result).toEqual({
        text: 'This is a test transcription',
        language: 'en',
      });
    });

    it('should transcribe audio with language parameter', async () => {
      const mockResponse = {
        data: {
          text: 'Esta é uma transcrição de teste',
          language: 'pt',
        },
      };

      vi.mocked(api.post).mockResolvedValue(mockResponse);

      const audioFile = new File(['fake audio'], 'test.mp3', { type: 'audio/mp3' });
      const result = await multimodalService.transcribeAudio(audioFile, 'pt');

      const formDataCalls = vi.mocked(api.post).mock.calls;
      expect(formDataCalls.length).toBe(1);

      expect(result).toEqual({
        text: 'Esta é uma transcrição de teste',
        language: 'pt',
      });
    });

    it('should handle transcription errors', async () => {
      vi.mocked(api.post).mockRejectedValue(new Error('Transcription failed'));

      const audioFile = new File(['fake audio'], 'test.mp3', { type: 'audio/mp3' });

      await expect(multimodalService.transcribeAudio(audioFile)).rejects.toThrow(
        'Transcription failed'
      );
    });
  });

  describe('analyzeImage', () => {
    it('should analyze image successfully', async () => {
      const mockResponse = {
        data: {
          analysis: 'This image contains a cat',
          tasks: ['Buy cat food', 'Schedule vet appointment'],
        },
      };

      vi.mocked(api.post).mockResolvedValue(mockResponse);

      const imageFile = new File(['fake image'], 'test.png', { type: 'image/png' });
      const result = await multimodalService.analyzeImage(imageFile);

      expect(api.post).toHaveBeenCalledWith(
        '/v2/multimodal/analyze-image',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      expect(result).toEqual({
        analysis: 'This image contains a cat',
        tasks: ['Buy cat food', 'Schedule vet appointment'],
      });
    });

    it('should analyze image with custom prompt', async () => {
      const mockResponse = {
        data: {
          analysis: 'Detailed analysis of the image',
          tasks: [],
        },
      };

      vi.mocked(api.post).mockResolvedValue(mockResponse);

      const imageFile = new File(['fake image'], 'test.png', { type: 'image/png' });
      const customPrompt = 'Describe this image in detail';

      const result = await multimodalService.analyzeImage(imageFile, customPrompt);

      expect(api.post).toHaveBeenCalled();
      expect(result).toEqual({
        analysis: 'Detailed analysis of the image',
        tasks: [],
      });
    });

    it('should handle image analysis errors', async () => {
      vi.mocked(api.post).mockRejectedValue(new Error('Analysis failed'));

      const imageFile = new File(['fake image'], 'test.png', { type: 'image/png' });

      await expect(multimodalService.analyzeImage(imageFile)).rejects.toThrow('Analysis failed');
    });
  });

  describe('processMultimodal', () => {
    it('should process audio file', async () => {
      const mockResponse = {
        data: {
          type: 'audio',
          text: 'Transcribed audio',
          language: 'en',
          tasks_created: [],
        },
      };

      vi.mocked(api.post).mockResolvedValue(mockResponse);

      const audioFile = new File(['fake audio'], 'test.mp3', { type: 'audio/mp3' });
      const result = await multimodalService.processMultimodal(audioFile);

      expect(api.post).toHaveBeenCalledWith('/v2/multimodal/process', expect.any(FormData), {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      expect(result).toEqual({
        type: 'audio',
        text: 'Transcribed audio',
        language: 'en',
        tasks_created: [],
      });
    });

    it('should process image file', async () => {
      const mockResponse = {
        data: {
          type: 'image',
          analysis: 'Image analysis',
          tasks: ['Task 1'],
          tasks_created: [],
        },
      };

      vi.mocked(api.post).mockResolvedValue(mockResponse);

      const imageFile = new File(['fake image'], 'test.png', { type: 'image/png' });
      const result = await multimodalService.processMultimodal(imageFile);

      expect(result.type).toBe('image');
      expect(result.analysis).toBe('Image analysis');
    });

    it('should process with auto-create tasks option', async () => {
      const mockResponse = {
        data: {
          type: 'audio',
          text: 'Buy groceries and do laundry',
          language: 'en',
          tasks_created: [
            { id: 1, title: 'Buy groceries' },
            { id: 2, title: 'Do laundry' },
          ],
        },
      };

      vi.mocked(api.post).mockResolvedValue(mockResponse);

      const audioFile = new File(['fake audio'], 'test.mp3', { type: 'audio/mp3' });
      const result = await multimodalService.processMultimodal(audioFile, {
        autoCreateTasks: true,
      });

      expect(result.tasks_created).toHaveLength(2);
    });

    it('should process with big rock id', async () => {
      const mockResponse = {
        data: {
          type: 'audio',
          text: 'Complete project milestone',
          language: 'en',
          tasks_created: [{ id: 1, title: 'Complete project milestone', big_rock_id: 123 }],
        },
      };

      vi.mocked(api.post).mockResolvedValue(mockResponse);

      const audioFile = new File(['fake audio'], 'test.mp3', { type: 'audio/mp3' });
      const result = await multimodalService.processMultimodal(audioFile, {
        autoCreateTasks: true,
        bigRockId: 123,
      });

      expect(result.tasks_created![0].big_rock_id).toBe(123);
    });

    it('should handle processing errors', async () => {
      vi.mocked(api.post).mockRejectedValue(new Error('Processing failed'));

      const audioFile = new File(['fake audio'], 'test.mp3', { type: 'audio/mp3' });

      await expect(multimodalService.processMultimodal(audioFile)).rejects.toThrow(
        'Processing failed'
      );
    });
  });

  describe('validateFile', () => {
    describe('audio validation', () => {
      it('should validate supported audio formats', () => {
        const supportedFormats = ['mp3', 'wav', 'm4a', 'webm', 'ogg', 'flac'];

        supportedFormats.forEach((format) => {
          const file = new File(['fake audio'], `test.${format}`, { type: `audio/${format}` });
          expect(multimodalService.validateFile(file, 'audio')).toBe(true);
        });
      });

      it('should reject unsupported audio formats', () => {
        const file = new File(['fake audio'], 'test.avi', { type: 'video/avi' });
        expect(multimodalService.validateFile(file, 'audio')).toBe(false);
      });

      it('should reject audio files larger than 25MB', () => {
        const largeFile = new File(['x'.repeat(26 * 1024 * 1024)], 'large.mp3', {
          type: 'audio/mp3',
        });
        expect(multimodalService.validateFile(largeFile, 'audio')).toBe(false);
      });

      it('should accept audio files smaller than 25MB', () => {
        const smallFile = new File(['x'.repeat(10 * 1024 * 1024)], 'small.mp3', {
          type: 'audio/mp3',
        });
        expect(multimodalService.validateFile(smallFile, 'audio')).toBe(true);
      });
    });

    describe('image validation', () => {
      it('should validate supported image formats', () => {
        const supportedFormats = ['png', 'jpg', 'jpeg', 'heic', 'webp'];

        supportedFormats.forEach((format) => {
          const file = new File(['fake image'], `test.${format}`, { type: `image/${format}` });
          expect(multimodalService.validateFile(file, 'image')).toBe(true);
        });
      });

      it('should reject unsupported image formats', () => {
        const file = new File(['fake image'], 'test.gif', { type: 'image/gif' });
        expect(multimodalService.validateFile(file, 'image')).toBe(false);
      });

      it('should reject image files larger than 20MB', () => {
        const largeFile = new File(['x'.repeat(21 * 1024 * 1024)], 'large.png', {
          type: 'image/png',
        });
        expect(multimodalService.validateFile(largeFile, 'image')).toBe(false);
      });

      it('should accept image files smaller than 20MB', () => {
        const smallFile = new File(['x'.repeat(10 * 1024 * 1024)], 'small.png', {
          type: 'image/png',
        });
        expect(multimodalService.validateFile(smallFile, 'image')).toBe(true);
      });
    });
  });
});
