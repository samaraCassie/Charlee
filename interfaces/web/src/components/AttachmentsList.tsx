import React from 'react';
import { FileAudio, FileImage, Download, RotateCcw, Trash2 } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface Attachment {
  id: number;
  file_name: string;
  file_type: string; // 'audio' | 'image'
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

interface AttachmentsListProps {
  attachments: Attachment[];
  onReprocess?: (attachmentId: number) => void;
  onDelete?: (attachmentId: number) => void;
  onDownload?: (attachmentId: number) => void;
}

export const AttachmentsList: React.FC<AttachmentsListProps> = ({
  attachments,
  onReprocess,
  onDelete,
  onDownload,
}) => {
  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return '—';
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    const mb = kb / 1024;
    return `${mb.toFixed(1)} MB`;
  };

  const getFileIcon = (fileType: string) => {
    return fileType === 'audio' ? (
      <FileAudio className="h-5 w-5 text-blue-500" />
    ) : (
      <FileImage className="h-5 w-5 text-green-500" />
    );
  };

  if (attachments.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <p className="text-sm text-muted-foreground">
            Nenhum anexo encontrado para esta tarefa.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold">Anexos ({attachments.length})</h3>

      <div className="space-y-2">
        {attachments.map((attachment) => (
          <Card key={attachment.id}>
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                {/* Icon */}
                <div className="mt-1">{getFileIcon(attachment.file_type)}</div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  {/* File name and metadata */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium truncate">{attachment.file_name}</h4>
                      <div className="flex flex-wrap items-center gap-2 mt-1 text-xs text-muted-foreground">
                        <span className="capitalize">{attachment.file_type}</span>
                        <span>•</span>
                        <span>{formatFileSize(attachment.file_metadata?.size)}</span>
                        {attachment.file_type === 'audio' && attachment.file_metadata?.duration && (
                          <>
                            <span>•</span>
                            <span>{attachment.file_metadata.duration}s</span>
                          </>
                        )}
                        {attachment.file_type === 'image' &&
                          attachment.file_metadata?.width &&
                          attachment.file_metadata?.height && (
                            <>
                              <span>•</span>
                              <span>
                                {attachment.file_metadata.width}x{attachment.file_metadata.height}
                              </span>
                            </>
                          )}
                        <span>•</span>
                        <span>
                          {format(new Date(attachment.created_at), 'dd MMM yyyy HH:mm', {
                            locale: ptBR,
                          })}
                        </span>
                      </div>
                    </div>

                    {/* Action buttons */}
                    <div className="flex gap-1 shrink-0">
                      {onDownload && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => onDownload(attachment.id)}
                          title="Download"
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      )}
                      {onReprocess && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => onReprocess(attachment.id)}
                          title="Re-processar"
                        >
                          <RotateCcw className="h-4 w-4" />
                        </Button>
                      )}
                      {onDelete && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-destructive"
                          onClick={() => onDelete(attachment.id)}
                          title="Excluir"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Processed text */}
                  {attachment.processed_text && (
                    <div className="mt-3 p-3 rounded-md bg-muted/50 text-sm">
                      <p className="text-xs font-medium text-muted-foreground mb-1">
                        {attachment.file_type === 'audio' ? 'Transcrição:' : 'Análise:'}
                      </p>
                      <p className="text-foreground">{attachment.processed_text}</p>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
