import React, { useState, useRef } from 'react';
import { Image as ImageIcon, Upload, Loader2, X, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { multimodalService } from '@/services/multimodalService';
import { cn } from '@/lib/utils';
import { Progress } from './ui/progress';

interface ImageFile {
  file: File;
  previewUrl: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  analysis?: string;
  tasks?: Array<{ description: string; source: string }>;
  error?: string;
}

interface ImageBatchUploadProps {
  onBatchComplete: (results: ImageFile[]) => void;
  onError?: (error: string) => void;
  customPrompt?: string;
  className?: string;
  maxFiles?: number;
  autoAnalyze?: boolean;
}

export const ImageBatchUpload: React.FC<ImageBatchUploadProps> = ({
  onBatchComplete,
  onError,
  customPrompt,
  className,
  maxFiles = 10,
  autoAnalyze = true,
}) => {
  const [images, setImages] = useState<ImageFile[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState(0);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (files: FileList) => {
    const fileArray = Array.from(files);

    // Validate file count
    if (fileArray.length > maxFiles) {
      onError?.(`Maximum ${maxFiles} images allowed. ${fileArray.length} selected.`);
      return;
    }

    // Validate each file and create previews
    const validImages: ImageFile[] = [];
    const errors: string[] = [];

    fileArray.forEach((file) => {
      try {
        multimodalService.validateFile(file, 'image');

        const previewUrl = URL.createObjectURL(file);
        validImages.push({
          file,
          previewUrl,
          status: 'pending',
        });
      } catch (error) {
        errors.push(
          `${file.name}: ${error instanceof Error ? error.message : 'Invalid file'}`
        );
      }
    });

    if (errors.length > 0) {
      onError?.(
        `Some files were rejected:\n${errors.slice(0, 3).join('\n')}${
          errors.length > 3 ? `\n... and ${errors.length - 3} more` : ''
        }`
      );
    }

    if (validImages.length > 0) {
      setImages(validImages);

      // Auto-analyze if enabled
      if (autoAnalyze) {
        analyzeBatch(validImages);
      }
    }
  };

  const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);

    const files = event.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelect(files);
    }
  };

  const analyzeBatch = async (imagesToAnalyze: ImageFile[]) => {
    setIsProcessing(true);
    setProgress(0);

    const totalImages = imagesToAnalyze.length;
    let completed = 0;

    // Process images in parallel (with concurrency limit of 3)
    const concurrencyLimit = 3;
    const results: ImageFile[] = [...imagesToAnalyze];

    for (let i = 0; i < totalImages; i += concurrencyLimit) {
      const batch = imagesToAnalyze.slice(i, i + concurrencyLimit);

      await Promise.all(
        batch.map(async (imageFile, batchIndex) => {
          const actualIndex = i + batchIndex;

          try {
            // Update status to processing
            setImages((prev) =>
              prev.map((img, idx) =>
                idx === actualIndex ? { ...img, status: 'processing' as const } : img
              )
            );

            // Analyze image
            const result = await multimodalService.analyzeImage(
              imageFile.file,
              customPrompt
            );

            // Update with results
            results[actualIndex] = {
              ...imageFile,
              status: 'completed',
              analysis: result.analysis,
              tasks: result.tasks,
            };

            setImages((prev) =>
              prev.map((img, idx) => (idx === actualIndex ? results[actualIndex] : img))
            );
          } catch (error) {
            // Update with error
            results[actualIndex] = {
              ...imageFile,
              status: 'error',
              error:
                error instanceof Error ? error.message : 'Failed to analyze image',
            };

            setImages((prev) =>
              prev.map((img, idx) => (idx === actualIndex ? results[actualIndex] : img))
            );
          } finally {
            completed++;
            setProgress((completed / totalImages) * 100);
          }
        })
      );
    }

    setIsProcessing(false);
    onBatchComplete(results.filter((r) => r.status === 'completed'));
  };

  const removeImage = (index: number) => {
    setImages((prev) => {
      const updated = [...prev];
      const removed = updated.splice(index, 1)[0];
      if (removed.previewUrl) {
        URL.revokeObjectURL(removed.previewUrl);
      }
      return updated;
    });
  };

  const clearAll = () => {
    images.forEach((img) => {
      if (img.previewUrl) {
        URL.revokeObjectURL(img.previewUrl);
      }
    });
    setImages([]);
    setProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const getStatusIcon = (status: ImageFile['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-destructive" />;
      case 'processing':
        return <Loader2 className="h-4 w-4 animate-spin text-primary" />;
      default:
        return null;
    }
  };

  return (
    <div className={cn('flex flex-col gap-3', className)}>
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".png,.jpg,.jpeg,.heic,.webp"
        onChange={handleFileInputChange}
        className="hidden"
        multiple
        aria-label="Upload multiple images"
      />

      {/* Upload area */}
      <div
        className={cn(
          'flex flex-col items-center justify-center gap-4 rounded-lg border-2 border-dashed p-6 transition-colors',
          isDragging
            ? 'border-primary bg-primary/10'
            : 'border-muted-foreground/25 hover:border-muted-foreground/50',
          'cursor-pointer'
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={triggerFileInput}
      >
        <div className="flex flex-col items-center gap-2 text-center">
          {isDragging ? (
            <Upload className="h-8 w-8 text-primary" />
          ) : (
            <ImageIcon className="h-8 w-8 text-muted-foreground" />
          )}
          <div>
            <p className="text-sm font-medium">
              {isDragging ? 'Drop images here' : 'Upload multiple images'}
            </p>
            <p className="text-xs text-muted-foreground">or drag and drop</p>
          </div>
          <p className="text-xs text-muted-foreground">
            PNG, JPG, JPEG, HEIC, WEBP (max {maxFiles} files, 20MB each)
          </p>
        </div>
      </div>

      {/* Progress bar */}
      {isProcessing && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Processing images...</span>
            <span className="font-medium">{Math.round(progress)}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      )}

      {/* Images grid */}
      {images.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">
              {images.length} image{images.length > 1 ? 's' : ''} selected
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={clearAll}
              disabled={isProcessing}
            >
              Clear All
            </Button>
          </div>

          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4">
            {images.map((image, index) => (
              <div
                key={index}
                className="relative rounded-lg border bg-card p-1 transition-shadow hover:shadow-md"
              >
                {/* Preview image */}
                <div className="relative aspect-square overflow-hidden rounded">
                  <img
                    src={image.previewUrl}
                    alt={image.file.name}
                    className="h-full w-full object-cover"
                  />

                  {/* Status overlay */}
                  <div className="absolute bottom-1 right-1">
                    {getStatusIcon(image.status)}
                  </div>

                  {/* Remove button */}
                  {!isProcessing && (
                    <Button
                      variant="destructive"
                      size="icon"
                      className="absolute right-1 top-1 h-6 w-6 opacity-0 transition-opacity hover:opacity-100"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeImage(index);
                      }}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  )}
                </div>

                {/* File info */}
                <div className="mt-1 px-1">
                  <p className="truncate text-xs text-muted-foreground">
                    {image.file.name}
                  </p>
                </div>

                {/* Error message */}
                {image.status === 'error' && (
                  <div className="mt-1 rounded bg-destructive/10 p-1">
                    <p className="text-xs text-destructive">{image.error}</p>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Analyze button (if not auto-analyzing) */}
          {!autoAnalyze && !isProcessing && (
            <Button className="w-full" onClick={() => analyzeBatch(images)}>
              Analyze {images.length} Image{images.length > 1 ? 's' : ''}
            </Button>
          )}
        </div>
      )}
    </div>
  );
};
