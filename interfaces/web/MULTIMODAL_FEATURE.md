# Multimodal Input Feature

Comprehensive voice recording, transcription, and image analysis feature powered by OpenAI's Whisper and GPT-4o Vision APIs.

## 📋 Table of Contents

- [Overview](#overview)
- [Components](#components)
- [Services](#services)
- [Features](#features)
- [Usage Examples](#usage-examples)
- [Accessibility](#accessibility)
- [Testing](#testing)
- [API Reference](#api-reference)

## 🎯 Overview

The multimodal input feature allows users to:

- **Record and transcribe voice input** using OpenAI Whisper API
- **Upload and analyze images** using GPT-4o Vision API
- **Extract tasks** automatically from both audio and images
- **Offline support** with request queueing
- **Full accessibility** with ARIA labels and keyboard navigation

## 🧩 Components

### ImageUpload

A fully accessible image upload component with drag-and-drop support.

**Location:** `/interfaces/web/src/components/ImageUpload.tsx`

**Features:**
- ✅ Drag and drop support
- ✅ Image preview before analysis
- ✅ File validation (size, format)
- ✅ Keyboard accessible (Enter/Space)
- ✅ Screen reader friendly
- ✅ Auto-analyze or manual trigger
- ✅ React.memo optimized

**Supported Formats:** PNG, JPG, JPEG, HEIC, WEBP
**Max File Size:** 20MB

**Example:**
```tsx
import { ImageUpload } from '@/components/ImageUpload';

<ImageUpload
  onAnalysis={(analysis, tasks) => {
    console.log('Analysis:', analysis);
    tasks.forEach(task => {
      console.log('Task:', task.description);
    });
  }}
  onError={(error) => console.error(error)}
  autoAnalyze={true}
  customPrompt="Extract all action items from this image"
/>
```

### VoiceInput

A fully accessible voice recording and transcription component.

**Location:** `/interfaces/web/src/components/VoiceInput.tsx`

**Features:**
- ✅ Browser-based audio recording (MediaRecorder API)
- ✅ Real-time recording timer
- ✅ Audio preview with playback controls
- ✅ Re-record functionality
- ✅ Keyboard accessible
- ✅ Screen reader announcements
- ✅ Automatic media cleanup
- ✅ React.memo optimized

**Supported Formats:** WebM audio
**Max File Size:** 25MB

**Example:**
```tsx
import { VoiceInput } from '@/components/VoiceInput';

<VoiceInput
  onTranscription={(result) => {
    console.log('Text:', result.text);
    console.log('Language:', result.language);
  }}
  onError={(error) => console.error(error)}
  language="pt" // Optional: 'en', 'pt', 'es', etc.
/>
```

## 🔧 Services

### multimodalService

Handles all API communication for multimodal operations.

**Location:** `/interfaces/web/src/services/multimodalService.ts`

**Methods:**

#### `transcribeAudio(file: File, language?: string)`
Transcribes audio to text using OpenAI Whisper.

```typescript
const result = await multimodalService.transcribeAudio(audioFile, 'pt');
console.log(result.text); // Transcribed text
console.log(result.language); // Detected/specified language
```

#### `analyzeImage(file: File, prompt?: string)`
Analyzes image using GPT-4o Vision.

```typescript
const result = await multimodalService.analyzeImage(imageFile);
console.log(result.analysis); // AI analysis
console.log(result.tasks); // Extracted tasks
```

#### `processMultimodal(file: File, options?)`
Unified endpoint for processing files and auto-creating tasks.

```typescript
const result = await multimodalService.processMultimodal(file, {
  autoCreateTasks: true,
  bigRockId: 123
});
console.log(result.tasks_created); // Created task IDs
```

#### `validateFile(file: File, type: 'audio' | 'image')`
Validates file before upload.

```typescript
try {
  multimodalService.validateFile(file, 'image');
  // File is valid
} catch (error) {
  console.error(error.message); // Validation error
}
```

### attachmentsService

Manages attachment CRUD operations.

**Location:** `/interfaces/web/src/services/attachmentsService.ts`

**Methods:**
- `getTaskAttachments(taskId)` - Get all attachments for a task
- `getAllAttachments(options)` - Get all user attachments with filtering
- `getAttachment(attachmentId)` - Get specific attachment
- `deleteAttachment(attachmentId)` - Delete attachment
- `reprocessAttachment(attachmentId)` - Re-transcribe or re-analyze
- `downloadAttachment(attachmentId)` - Download attachment file

### Retry Utilities

Exponential backoff retry logic with offline support.

**Location:** `/interfaces/web/src/lib/retry.ts`

**Features:**
- ✅ Exponential backoff with configurable parameters
- ✅ Retryable error detection (network, 5xx errors)
- ✅ Offline queue for failed requests
- ✅ Online/offline state detection
- ✅ 100% test coverage

**Example:**
```typescript
import { retryWithBackoff } from '@/lib/retry';

const data = await retryWithBackoff(
  () => api.post('/endpoint', payload),
  {
    maxAttempts: 5,
    initialDelay: 1000,
    onRetry: (attempt, error) => {
      console.log(`Retry attempt ${attempt}:`, error.message);
    }
  }
);
```

## ✨ Features

### Offline Support

All multimodal operations support offline queueing:

```typescript
import { OfflineQueue } from '@/lib/retry';

// Automatically queues when offline
await multimodalService.transcribeAudio(file);

// Check queue size
console.log(OfflineQueue.size());

// Get queued requests
const queue = OfflineQueue.getQueue();

// Clear queue
OfflineQueue.clear();
```

### Accessibility

Both components are fully accessible:

- **ARIA labels** on all interactive elements
- **Live regions** for screen reader announcements
- **Keyboard navigation** (Enter/Space for upload trigger)
- **Focus management** with proper tab order
- **aria-hidden** on decorative icons
- **role attributes** for semantic structure
- **WCAG 2.1 Level AA** compliant

### Performance Optimizations

- **React.memo** on both components to prevent unnecessary re-renders
- **Lazy imports** (can be added via React.lazy)
- **Automatic cleanup** of object URLs and media streams
- **Debounced** retry logic with exponential backoff

## 📚 Usage Examples

### Complete Task Creation Flow

```tsx
import { VoiceInput } from '@/components/VoiceInput';
import { ImageUpload } from '@/components/ImageUpload';

function TaskCreator() {
  const handleVoiceTask = (result) => {
    // Create task from voice transcription
    createTask({ title: result.text });
  };

  const handleImageTask = (analysis, tasks) => {
    // Create multiple tasks from image
    tasks.forEach(task => {
      createTask({ title: task.description });
    });
  };

  return (
    <div>
      <h2>Create tasks by voice</h2>
      <VoiceInput onTranscription={handleVoiceTask} />

      <h2>Create tasks from image</h2>
      <ImageUpload onAnalysis={handleImageTask} />
    </div>
  );
}
```

### Error Handling

```tsx
<ImageUpload
  onAnalysis={(analysis, tasks) => {
    // Success handling
  }}
  onError={(error) => {
    if (error.includes('File size')) {
      toast.error('Image is too large. Max 20MB.');
    } else if (error.includes('Unsupported')) {
      toast.error('Please use PNG, JPG, or WEBP format.');
    } else {
      toast.error('Analysis failed. Please try again.');
    }
  }}
/>
```

### Custom Analysis Prompts

```tsx
<ImageUpload
  customPrompt="Extract all dates, names, and action items from this document"
  onAnalysis={(analysis, tasks) => {
    // Processes with custom prompt
  }}
/>
```

## 🧪 Testing

### Test Coverage

| File | Statements | Branches | Functions | Lines |
|------|-----------|----------|-----------|-------|
| **ImageUpload.tsx** | 100% | 84.37% | 100% | 100% |
| **VoiceInput.tsx** | 93.82% | 84.44% | 80% | 96.1% |
| **multimodalService.ts** | 92.85% | 90.62% | 72.72% | 92.85% |
| **attachmentsService.ts** | 100% | 100% | 100% | 100% |
| **retry.ts** | **100%** | **100%** | **100%** | **100%** |

**Total Tests:** 173 passing ✅
**Overall Branch Coverage:** 79.8% (exceeds 78% threshold) ✅

### Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- ImageUpload.test.tsx

# Watch mode
npm test -- --watch
```

### Test Examples

```typescript
// Testing ImageUpload
it('should validate file size', async () => {
  vi.mocked(multimodalService.validateFile).mockImplementation(() => {
    throw new Error('File size exceeds maximum');
  });

  render(<ImageUpload onAnalysis={vi.fn()} onError={onError} />);

  const file = new File(['x'.repeat(21 * 1024 * 1024)], 'large.png');
  const input = screen.getByLabelText('Upload image file');

  await userEvent.upload(input, file);

  expect(onError).toHaveBeenCalledWith(expect.stringContaining('File size'));
});
```

## 📖 API Reference

### ImageUpload Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `onAnalysis` | `(analysis: string, tasks: Task[]) => void` | ✅ | - | Called when analysis completes |
| `onError` | `(error: string) => void` | ❌ | - | Called on errors |
| `customPrompt` | `string` | ❌ | - | Custom analysis prompt |
| `className` | `string` | ❌ | - | Additional CSS classes |
| `autoAnalyze` | `boolean` | ❌ | `true` | Auto-analyze on upload |

### VoiceInput Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `onTranscription` | `(result: TranscriptionResult) => void` | ✅ | - | Called when transcription completes |
| `onError` | `(error: string) => void` | ❌ | - | Called on errors |
| `language` | `string` | ❌ | Auto-detect | Language code (e.g., 'pt', 'en') |
| `className` | `string` | ❌ | - | Additional CSS classes |

### Types

```typescript
interface Task {
  description: string;
  source: string;
}

interface TranscriptionResult {
  text: string;
  language: string;
  success: boolean;
}

interface ImageAnalysisResponse {
  analysis: string;
  tasks: Task[];
  success: boolean;
}
```

## 🚀 Future Enhancements

Potential improvements for future iterations:

- [ ] **Progress indicators** for large file uploads
- [ ] **Toast notifications** for success/error feedback
- [ ] **Batch processing** for multiple files
- [ ] **E2E tests** with Playwright/Cypress
- [ ] **i18n support** for multilingual UIs
- [ ] **Custom themes** for components
- [ ] **Advanced analytics** dashboard
- [ ] **File compression** before upload
- [ ] **WebSocket** for real-time processing updates

## 📄 License

This feature is part of the Charlee project and follows the project's license.

## 🤝 Contributing

When contributing to this feature:

1. Ensure all tests pass (`npm test`)
2. Maintain >78% branch coverage
3. Add JSDoc comments for new functions
4. Update this README for significant changes
5. Follow accessibility best practices
6. Test with screen readers

---

**Last Updated:** 2025-11-17
**Version:** 1.0.0
**Maintainer:** Charlee Team
