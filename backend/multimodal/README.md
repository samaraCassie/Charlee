# 🎙️📷 Multimodal Input Feature

> **Feature Branch:** `feat/multimodal-input`
> **Version:** V2
> **Priority:** ⭐ 3 (MUITO ALTO - Diferencial Competitivo)

## 📋 Overview

The Multimodal Input feature enables users to create tasks using voice recordings and image uploads. It leverages OpenAI's Whisper API for speech-to-text transcription and GPT-4o Vision API for image analysis and task extraction.

### Key Capabilities

- 🎙️ **Voice Input:** Record audio and automatically transcribe to text using Whisper AI
- 📷 **Image Analysis:** Upload images (planners, screenshots, handwritten notes) and extract tasks
- 🤖 **AI-Powered Processing:** Intelligent task extraction from both audio and visual content
- 📝 **Automatic Task Creation:** Directly create tasks in your inbox from multimodal input
- 🌍 **Multi-language Support:** Transcription supports multiple languages

## 🏗️ Architecture

### Backend Components

```
backend/
├── multimodal/
│   ├── __init__.py
│   ├── audio_service.py      # OpenAI Whisper integration
│   └── vision_service.py     # GPT-4o Vision integration
├── api/routes/
│   └── multimodal.py         # API endpoints
└── database/
    ├── models.py             # Attachment model
    └── migrations/versions/
        └── 008_add_multimodal_attachments.py
```

### Frontend Components

```
interfaces/web/src/
├── components/
│   ├── VoiceInput.tsx        # Voice recording component
│   └── ImageUpload.tsx       # Image upload component
└── services/
    └── multimodalService.ts  # API client
```

## 🔌 API Endpoints

### 1. Transcribe Audio

**Endpoint:** `POST /api/v2/multimodal/transcribe`

**Description:** Transcribe audio file to text using OpenAI Whisper.

**Request:**
```
Content-Type: multipart/form-data

- file: Audio file (mp3, wav, m4a, webm, ogg, flac)
- language: Optional language code (e.g., 'en', 'pt', 'es')
```

**Response:**
```json
{
  "text": "Transcribed text from audio",
  "language": "en",
  "success": true
}
```

**Supported Formats:** mp3, wav, m4a, webm, ogg, flac
**Max File Size:** 25 MB

### 2. Analyze Image

**Endpoint:** `POST /api/v2/multimodal/analyze-image`

**Description:** Analyze image using GPT-4o Vision and extract tasks.

**Request:**
```
Content-Type: multipart/form-data

- file: Image file (png, jpg, jpeg, heic, webp)
- prompt: Optional custom analysis prompt
```

**Response:**
```json
{
  "analysis": "AI-generated analysis of the image content",
  "tasks": [
    {
      "description": "Task extracted from image",
      "source": "image_analysis"
    }
  ],
  "success": true
}
```

**Supported Formats:** png, jpg, jpeg, heic, webp
**Max File Size:** 20 MB

### 3. Process Multimodal Input (Unified)

**Endpoint:** `POST /api/v2/multimodal/process`

**Description:** Unified endpoint that processes audio OR image and optionally creates tasks.

**Request:**
```
Content-Type: multipart/form-data

- file: Audio or image file
- auto_create_tasks: Boolean (default: true)
- big_rock_id: Optional Big Rock ID to associate tasks with
```

**Response:**
```json
{
  "success": true,
  "message": "Processed successfully. Created 3 task(s).",
  "transcription": "Text from audio (if audio file)",
  "analysis": "Analysis from image (if image file)",
  "tasks_created": [123, 124, 125]
}
```

**Workflow:**
1. Detect file type (audio or image)
2. Process with appropriate service (Whisper or Vision)
3. Extract tasks from content
4. Create tasks in database (if `auto_create_tasks=true`)
5. Return processing result with task IDs

## 📊 Database Schema

### Attachment Model

```sql
CREATE TABLE attachments (
    id INTEGER PRIMARY KEY,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,

    -- File information
    file_type VARCHAR(20) CHECK (file_type IN ('audio', 'image', 'document')),
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    file_url VARCHAR(500),
    mime_type VARCHAR(100),

    -- Processing results
    transcription TEXT,
    analysis TEXT,
    processing_status VARCHAR(20) DEFAULT 'completed',
    error_message TEXT,

    -- Metadata
    metadata JSON,

    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## 🎨 Frontend Usage

### VoiceInput Component

```tsx
import { VoiceInput } from '@/components/VoiceInput';

function TaskForm() {
  const handleTranscription = (text: string) => {
    // Use transcribed text
    console.log('Transcription:', text);
  };

  const handleError = (error: string) => {
    console.error('Error:', error);
  };

  return (
    <VoiceInput
      onTranscription={handleTranscription}
      onError={handleError}
      language="pt"
    />
  );
}
```

### ImageUpload Component

```tsx
import { ImageUpload } from '@/components/ImageUpload';

function TaskExtractor() {
  const handleAnalysis = (analysis: string, tasks: any[]) => {
    console.log('Analysis:', analysis);
    console.log('Extracted tasks:', tasks);
  };

  return (
    <ImageUpload
      onAnalysis={handleAnalysis}
      autoAnalyze={true}
      customPrompt="Extract high-priority tasks only"
    />
  );
}
```

### Multimodal Service

```typescript
import { multimodalService } from '@/services/multimodalService';

// Transcribe audio
const audioFile = /* File object */;
const result = await multimodalService.transcribeAudio(audioFile, 'pt');

// Analyze image
const imageFile = /* File object */;
const analysis = await multimodalService.analyzeImage(imageFile);

// Process and auto-create tasks
const processResult = await multimodalService.processMultimodal(file, {
  autoCreateTasks: true,
  bigRockId: 123,
});
```

## 🔐 Environment Variables

Add to `.env`:

```bash
# OpenAI API Key (required for Whisper and Vision)
OPENAI_API_KEY=sk-...
```

## 🧪 Testing

### Run Backend Tests

```bash
cd backend

# Run all multimodal tests
pytest tests/test_multimodal/ -v

# Run specific test file
pytest tests/test_multimodal/test_audio_service.py -v

# Run with coverage
pytest tests/test_multimodal/ --cov=multimodal --cov-report=html
```

### Test Coverage

- ✅ Audio Service: Transcription, format validation, error handling
- ✅ Vision Service: Image analysis, task extraction, resize handling
- ✅ API Endpoints: Request/response validation, authentication
- ✅ Database Models: Attachment creation and relationships

## 🚀 Usage Examples

### Use Case 1: Voice Task Creation

**Scenario:** User records a voice note while driving

```bash
curl -X POST http://localhost:8000/api/v2/multimodal/process \
  -H "Authorization: Bearer <token>" \
  -F "file=@voice_note.mp3" \
  -F "auto_create_tasks=true"
```

**Result:** Task created with description from transcription

### Use Case 2: Handwritten Planner Extraction

**Scenario:** User takes photo of handwritten daily planner

```bash
curl -X POST http://localhost:8000/api/v2/multimodal/process \
  -H "Authorization: Bearer <token>" \
  -F "file=@planner_photo.jpg" \
  -F "auto_create_tasks=true" \
  -F "big_rock_id=5"
```

**Result:** Multiple tasks extracted from image and associated with Big Rock #5

### Use Case 3: Email Screenshot Analysis

**Scenario:** User screenshots important email

```typescript
const screenshot = /* File from screenshot */;

const result = await multimodalService.analyzeImage(
  screenshot,
  "Extract action items and deadlines from this email"
);

// Result contains extracted tasks with deadlines
```

## 📈 Performance Considerations

### Audio Processing
- Max file size: 25 MB
- Average processing time: 2-5 seconds (depending on audio length)
- Supports streaming for real-time feedback

### Image Processing
- Max file size: 20 MB
- Images >4096px are automatically resized
- Average processing time: 3-7 seconds
- Base64 encoding for API transmission

## 🔒 Security

- File type validation (whitelist approach)
- File size limits enforced
- User authentication required for all endpoints
- No file storage (processed in-memory)
- Rate limiting on API endpoints

## 🌟 Future Enhancements

### Planned Features
- [ ] Document processing (PDF, DOCX)
- [ ] Real-time voice streaming
- [ ] Batch image processing
- [ ] Custom AI training for specific use cases
- [ ] Offline transcription (using local models)
- [ ] Multi-speaker detection in audio
- [ ] OCR enhancement for handwriting

### Potential Integrations
- [ ] WhatsApp voice messages
- [ ] Telegram voice/image forwarding
- [ ] Email attachment processing
- [ ] Calendar event extraction from images

## 📚 Additional Resources

- [OpenAI Whisper Documentation](https://platform.openai.com/docs/guides/speech-to-text)
- [GPT-4o Vision Documentation](https://platform.openai.com/docs/guides/vision)
- [Backend Standards](../../standards/BACKEND_STANDARDS.md)
- [Frontend Standards](../../standards/FRONTEND_STANDARDS.md)
- [Testing Standards](../../standards/TESTING_STANDARDS.md)

## 🤝 Contributing

When contributing to this feature:

1. Follow [Backend Standards](../../standards/BACKEND_STANDARDS.md) for Python code
2. Follow [Frontend Standards](../../standards/FRONTEND_STANDARDS.md) for React/TypeScript
3. Write tests for new functionality (target 80%+ coverage)
4. Update this README with any new capabilities
5. Use English for all code, comments, and documentation

## 📝 License

MIT License - See root LICENSE file

---

**Last Updated:** 2025-11-17
**Maintainer:** Samara Cassie
**Status:** ✅ Implementation Complete
