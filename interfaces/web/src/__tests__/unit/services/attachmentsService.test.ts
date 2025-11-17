import { describe, it, expect, vi, beforeEach } from 'vitest';
import { attachmentsService } from '@/services/attachmentsService';
import api from '@/services/api';

vi.mock('@/services/api');

describe('attachmentsService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getTaskAttachments', () => {
    it('should fetch all attachments for a task', async () => {
      const mockAttachments = [
        {
          id: 1,
          task_id: 123,
          file_name: 'audio.mp3',
          file_type: 'audio',
          file_path: '/uploads/audio.mp3',
          processed_text: 'Transcription text',
          file_metadata: { size: 1024000, duration: 60 },
          created_at: '2025-11-17T10:00:00Z',
        },
        {
          id: 2,
          task_id: 123,
          file_name: 'image.png',
          file_type: 'image',
          file_path: '/uploads/image.png',
          processed_text: 'Image analysis',
          file_metadata: { size: 2048000, width: 1920, height: 1080 },
          created_at: '2025-11-17T11:00:00Z',
        },
      ];

      vi.mocked(api.get).mockResolvedValue({ data: mockAttachments });

      const result = await attachmentsService.getTaskAttachments(123);

      expect(api.get).toHaveBeenCalledWith('/v2/tasks/123/attachments');
      expect(result).toEqual(mockAttachments);
      expect(result).toHaveLength(2);
    });

    it('should return empty array for task with no attachments', async () => {
      vi.mocked(api.get).mockResolvedValue({ data: [] });

      const result = await attachmentsService.getTaskAttachments(456);

      expect(api.get).toHaveBeenCalledWith('/v2/tasks/456/attachments');
      expect(result).toEqual([]);
      expect(result).toHaveLength(0);
    });

    it('should handle API errors', async () => {
      vi.mocked(api.get).mockRejectedValue(new Error('Failed to fetch attachments'));

      await expect(attachmentsService.getTaskAttachments(123)).rejects.toThrow(
        'Failed to fetch attachments'
      );
    });
  });

  describe('getAttachment', () => {
    it('should fetch a specific attachment by ID', async () => {
      const mockAttachment = {
        id: 1,
        task_id: 123,
        file_name: 'audio.mp3',
        file_type: 'audio',
        file_path: '/uploads/audio.mp3',
        processed_text: 'Transcription text',
        file_metadata: { size: 1024000, duration: 60 },
        created_at: '2025-11-17T10:00:00Z',
      };

      vi.mocked(api.get).mockResolvedValue({ data: mockAttachment });

      const result = await attachmentsService.getAttachment(1);

      expect(api.get).toHaveBeenCalledWith('/v2/attachments/1');
      expect(result).toEqual(mockAttachment);
    });

    it('should handle 404 for non-existent attachment', async () => {
      vi.mocked(api.get).mockRejectedValue(new Error('Attachment not found'));

      await expect(attachmentsService.getAttachment(999)).rejects.toThrow('Attachment not found');
    });
  });

  describe('deleteAttachment', () => {
    it('should delete an attachment', async () => {
      vi.mocked(api.delete).mockResolvedValue({ status: 204 });

      await attachmentsService.deleteAttachment(1);

      expect(api.delete).toHaveBeenCalledWith('/v2/attachments/1');
    });

    it('should handle delete errors', async () => {
      vi.mocked(api.delete).mockRejectedValue(new Error('Delete failed'));

      await expect(attachmentsService.deleteAttachment(1)).rejects.toThrow('Delete failed');
    });
  });

  describe('reprocessAttachment', () => {
    it('should reprocess an audio attachment', async () => {
      const mockAttachment = {
        id: 1,
        task_id: 123,
        file_name: 'audio.mp3',
        file_type: 'audio',
        file_path: '/uploads/audio.mp3',
        processed_text: 'New transcription after reprocessing',
        file_metadata: { size: 1024000, duration: 60 },
        created_at: '2025-11-17T10:00:00Z',
      };

      vi.mocked(api.post).mockResolvedValue({ data: mockAttachment });

      const result = await attachmentsService.reprocessAttachment(1);

      expect(api.post).toHaveBeenCalledWith('/v2/attachments/1/reprocess');
      expect(result.processed_text).toBe('New transcription after reprocessing');
    });

    it('should reprocess an image attachment', async () => {
      const mockAttachment = {
        id: 2,
        task_id: 123,
        file_name: 'image.png',
        file_type: 'image',
        file_path: '/uploads/image.png',
        processed_text: 'New analysis after reprocessing',
        file_metadata: { size: 2048000, width: 1920, height: 1080 },
        created_at: '2025-11-17T11:00:00Z',
      };

      vi.mocked(api.post).mockResolvedValue({ data: mockAttachment });

      const result = await attachmentsService.reprocessAttachment(2);

      expect(result.processed_text).toBe('New analysis after reprocessing');
    });

    it('should handle reprocess errors', async () => {
      vi.mocked(api.post).mockRejectedValue(new Error('Reprocess failed'));

      await expect(attachmentsService.reprocessAttachment(1)).rejects.toThrow('Reprocess failed');
    });
  });

  describe('downloadAttachment', () => {
    it('should download attachment with default filename', async () => {
      const mockBlob = new Blob(['fake file content'], { type: 'application/octet-stream' });

      vi.mocked(api.get).mockResolvedValue({ data: mockBlob });

      // Mock DOM methods
      const createElementSpy = vi.spyOn(document, 'createElement');
      const appendChildSpy = vi.spyOn(document.body, 'appendChild');
      const removeChildSpy = vi.spyOn(document.body, 'removeChild');
      const createObjectURLSpy = vi.spyOn(window.URL, 'createObjectURL').mockReturnValue('blob:url');
      const revokeObjectURLSpy = vi.spyOn(window.URL, 'revokeObjectURL');

      const mockLink = document.createElement('a');
      mockLink.click = vi.fn();
      createElementSpy.mockReturnValue(mockLink);

      await attachmentsService.downloadAttachment(1);

      expect(api.get).toHaveBeenCalledWith('/v2/attachments/1/download', {
        responseType: 'blob',
      });
      expect(mockLink.download).toBe('attachment-1');
      expect(mockLink.click).toHaveBeenCalled();
      expect(appendChildSpy).toHaveBeenCalled();
      expect(removeChildSpy).toHaveBeenCalled();
      expect(revokeObjectURLSpy).toHaveBeenCalled();

      // Restore mocks
      createElementSpy.mockRestore();
      appendChildSpy.mockRestore();
      removeChildSpy.mockRestore();
      createObjectURLSpy.mockRestore();
      revokeObjectURLSpy.mockRestore();
    });

    it('should download attachment with custom filename', async () => {
      const mockBlob = new Blob(['fake file content'], { type: 'application/octet-stream' });

      vi.mocked(api.get).mockResolvedValue({ data: mockBlob });

      const createElementSpy = vi.spyOn(document, 'createElement');
      const appendChildSpy = vi.spyOn(document.body, 'appendChild');
      const removeChildSpy = vi.spyOn(document.body, 'removeChild');
      const createObjectURLSpy = vi.spyOn(window.URL, 'createObjectURL').mockReturnValue('blob:url');
      const revokeObjectURLSpy = vi.spyOn(window.URL, 'revokeObjectURL');

      const mockLink = document.createElement('a');
      mockLink.click = vi.fn();
      createElementSpy.mockReturnValue(mockLink);

      await attachmentsService.downloadAttachment(1, 'my-custom-file.mp3');

      expect(mockLink.download).toBe('my-custom-file.mp3');

      createElementSpy.mockRestore();
      appendChildSpy.mockRestore();
      removeChildSpy.mockRestore();
      createObjectURLSpy.mockRestore();
      revokeObjectURLSpy.mockRestore();
    });
  });

  describe('formatFileSize', () => {
    it('should format bytes to KB', () => {
      expect(attachmentsService.formatFileSize(1024)).toBe('1.0 KB');
      expect(attachmentsService.formatFileSize(512000)).toBe('500.0 KB');
    });

    it('should format bytes to MB', () => {
      expect(attachmentsService.formatFileSize(1048576)).toBe('1.0 MB');
      expect(attachmentsService.formatFileSize(5242880)).toBe('5.0 MB');
    });

    it('should return dash for undefined', () => {
      expect(attachmentsService.formatFileSize(undefined)).toBe('—');
      expect(attachmentsService.formatFileSize(0)).toBe('—');
    });
  });

  describe('getFileIcon', () => {
    it('should return FileAudio for audio files', () => {
      expect(attachmentsService.getFileIcon('audio')).toBe('FileAudio');
    });

    it('should return FileImage for image files', () => {
      expect(attachmentsService.getFileIcon('image')).toBe('FileImage');
    });
  });

  describe('formatDuration', () => {
    it('should format seconds to MM:SS', () => {
      expect(attachmentsService.formatDuration(0)).toBe('0:00');
      expect(attachmentsService.formatDuration(45)).toBe('0:45');
      expect(attachmentsService.formatDuration(60)).toBe('1:00');
      expect(attachmentsService.formatDuration(125)).toBe('2:05');
      expect(attachmentsService.formatDuration(3661)).toBe('61:01');
    });

    it('should return dash for undefined', () => {
      expect(attachmentsService.formatDuration(undefined)).toBe('—');
    });
  });
});
