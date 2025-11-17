import api from './api';

// ==================== Types ====================

export interface Attachment {
  id: number;
  task_id: number;
  file_name: string;
  file_type: 'audio' | 'image';
  file_path: string;
  processed_text?: string;
  file_metadata?: {
    size?: number;
    duration?: number;
    width?: number;
    height?: number;
  };
  created_at: string;
}

export interface AttachmentsListResponse {
  total: number;
  attachments: Attachment[];
}

export interface ReprocessResponse {
  success: boolean;
  attachment: Attachment;
}

// ==================== Attachments Service ====================

export const attachmentsService = {
  /**
   * Get all attachments for a specific task.
   *
   * @param taskId - ID of the task
   * @returns List of attachments
   */
  async getTaskAttachments(taskId: number): Promise<Attachment[]> {
    const response = await api.get(`/v2/tasks/${taskId}/attachments`);
    return response.data;
  },

  /**
   * Get all attachments for the current user with optional filtering.
   *
   * This is useful for:
   * - Transcription history page
   * - Analytics dashboards
   * - Searching across all attachments
   *
   * @param options - Filtering and pagination options
   * @returns List of attachments
   */
  async getAllAttachments(options?: {
    fileType?: 'audio' | 'image';
    taskId?: number;
    limit?: number;
    offset?: number;
  }): Promise<Attachment[]> {
    const params = new URLSearchParams();

    if (options?.fileType) {
      params.append('file_type', options.fileType);
    }
    if (options?.taskId) {
      params.append('task_id', String(options.taskId));
    }
    if (options?.limit) {
      params.append('limit', String(options.limit));
    }
    if (options?.offset) {
      params.append('offset', String(options.offset));
    }

    const queryString = params.toString();
    const url = `/v2/attachments${queryString ? `?${queryString}` : ''}`;

    const response = await api.get(url);
    return response.data;
  },

  /**
   * Get a specific attachment by ID.
   *
   * @param attachmentId - ID of the attachment
   * @returns Attachment details
   */
  async getAttachment(attachmentId: number): Promise<Attachment> {
    const response = await api.get(`/v2/attachments/${attachmentId}`);
    return response.data;
  },

  /**
   * Delete an attachment.
   *
   * @param attachmentId - ID of the attachment to delete
   */
  async deleteAttachment(attachmentId: number): Promise<void> {
    await api.delete(`/v2/attachments/${attachmentId}`);
  },

  /**
   * Reprocess an attachment (re-transcribe audio or re-analyze image).
   *
   * This is useful when:
   * - The AI made an error in the initial transcription/analysis
   * - You want to try again with potentially improved AI models
   * - The processed text was accidentally deleted
   *
   * @param attachmentId - ID of the attachment to reprocess
   * @returns Updated attachment with new processed text
   */
  async reprocessAttachment(attachmentId: number): Promise<Attachment> {
    const response = await api.post(`/v2/attachments/${attachmentId}/reprocess`);
    return response.data;
  },

  /**
   * Download an attachment file.
   *
   * Opens the file in a new tab or triggers download depending on browser.
   *
   * @param attachmentId - ID of the attachment to download
   * @param fileName - Optional custom file name for download
   */
  async downloadAttachment(attachmentId: number, fileName?: string): Promise<void> {
    const response = await api.get(`/v2/attachments/${attachmentId}/download`, {
      responseType: 'blob',
    });

    // Create blob URL and trigger download
    const blob = new Blob([response.data]);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName || `attachment-${attachmentId}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },

  /**
   * Format file size for display.
   *
   * @param bytes - File size in bytes
   * @returns Formatted string (e.g., "2.5 MB", "150 KB")
   */
  formatFileSize(bytes?: number): string {
    if (!bytes) return '—';
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    const mb = kb / 1024;
    return `${mb.toFixed(1)} MB`;
  },

  /**
   * Get icon name for file type.
   *
   * @param fileType - 'audio' or 'image'
   * @returns Icon name for lucide-react
   */
  getFileIcon(fileType: 'audio' | 'image'): 'FileAudio' | 'FileImage' {
    return fileType === 'audio' ? 'FileAudio' : 'FileImage';
  },

  /**
   * Format duration in seconds to MM:SS format.
   *
   * @param seconds - Duration in seconds
   * @returns Formatted duration (e.g., "3:45", "0:12")
   */
  formatDuration(seconds?: number): string {
    if (!seconds) return '—';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  },
};
