import React, { useState, useRef, useEffect } from 'react';
import { Image as ImageIcon, Upload, Loader2, X } from 'lucide-react';
import { Button } from './ui/button';
import { multimodalService } from '@/services/multimodalService';
import { cn } from '@/lib/utils';

interface ImageUploadProps {
  onAnalysis: (analysis: string, tasks: Array<{ description: string; source: string }>) => void;
  onError?: (error: string) => void;
  customPrompt?: string;
  className?: string;
  autoAnalyze?: boolean; // Automatically analyze on upload
}

export const ImageUpload: React.FC<ImageUploadProps> = ({
  onAnalysis,
  onError,
  customPrompt,
  className,
  autoAnalyze = true,
}) => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleFileSelect = (file: File) => {
    try {
      // Validate file
      multimodalService.validateFile(file, 'image');

      // Set selected file
      setSelectedImage(file);

      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);

      // Auto-analyze if enabled
      if (autoAnalyze) {
        analyzeImage(file);
      }
    } catch (error) {
      console.error('Invalid image file:', error);
      onError?.(error instanceof Error ? error.message : 'Invalid image file');
    }
  };

  const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileSelect(file);
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

    const file = event.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const analyzeImage = async (file: File) => {
    try {
      setIsProcessing(true);

      // Analyze image
      const result = await multimodalService.analyzeImage(file, customPrompt);

      // Call callback with results
      onAnalysis(result.analysis, result.tasks);
    } catch (error) {
      console.error('Error analyzing image:', error);
      onError?.(
        error instanceof Error
          ? error.message
          : 'Failed to analyze image. Please try again.'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const clearImage = () => {
    setSelectedImage(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className={cn('flex flex-col gap-2', className)}>
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".png,.jpg,.jpeg,.heic,.webp"
        onChange={handleFileInputChange}
        className="hidden"
        aria-label="Upload image"
      />

      {/* Upload button or preview */}
      {!selectedImage ? (
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
                {isDragging ? 'Drop image here' : 'Upload image'}
              </p>
              <p className="text-xs text-muted-foreground">
                or drag and drop
              </p>
            </div>
            <p className="text-xs text-muted-foreground">
              PNG, JPG, JPEG, HEIC, WEBP (max 20MB)
            </p>
          </div>
        </div>
      ) : (
        <div className="relative rounded-lg border bg-card p-2">
          {/* Preview */}
          {previewUrl && (
            <div className="relative">
              <img
                src={previewUrl}
                alt="Preview"
                className="h-48 w-full rounded object-contain"
              />

              {/* Clear button */}
              <Button
                variant="destructive"
                size="icon"
                className="absolute right-2 top-2 h-6 w-6"
                onClick={clearImage}
                disabled={isProcessing}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          )}

          {/* File info */}
          <div className="mt-2 flex items-center justify-between text-sm">
            <span className="truncate text-muted-foreground">
              {selectedImage.name}
            </span>
            <span className="text-xs text-muted-foreground">
              {(selectedImage.size / 1024 / 1024).toFixed(2)} MB
            </span>
          </div>

          {/* Analyze button (if not auto-analyzing) */}
          {!autoAnalyze && !isProcessing && (
            <Button
              className="mt-2 w-full"
              onClick={() => analyzeImage(selectedImage)}
            >
              Analyze Image
            </Button>
          )}

          {/* Processing indicator */}
          {isProcessing && (
            <div className="mt-2 flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Analyzing...</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
