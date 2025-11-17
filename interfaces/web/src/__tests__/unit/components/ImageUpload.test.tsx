import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ImageUpload } from '@/components/ImageUpload';
import * as multimodalService from '@/services/multimodalService';

// Mock the multimodal service
vi.mock('@/services/multimodalService');

// Mock URL.createObjectURL
global.URL.createObjectURL = vi.fn(() => 'mock-object-url');
global.URL.revokeObjectURL = vi.fn();

describe('ImageUpload', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render upload area', () => {
    const onAnalysis = vi.fn();
    const onError = vi.fn();

    render(<ImageUpload onAnalysis={onAnalysis} onError={onError} />);

    expect(screen.getByText('Upload image')).toBeInTheDocument();
  });

  it('should handle file selection via input', async () => {
    const onAnalysis = vi.fn();
    const onError = vi.fn();

    const mockAnalysisResponse = {
      analysis: 'Test analysis',
      tasks: ['Task 1', 'Task 2'],
    };

    vi.mocked(multimodalService.multimodalService.analyzeImage).mockResolvedValue(
      mockAnalysisResponse
    );

    render(<ImageUpload onAnalysis={onAnalysis} onError={onError} autoAnalyze={true} />);

    // Create a fake image file
    const file = new File(['fake image content'], 'test.png', { type: 'image/png' });

    // Find the file input (it's hidden, so use data-testid or similar)
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    expect(input).toBeTruthy();

    // Simulate file selection
    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(input);

    await waitFor(() => {
      expect(multimodalService.multimodalService.analyzeImage).toHaveBeenCalledWith(
        file,
        undefined
      );
      expect(onAnalysis).toHaveBeenCalledWith(mockAnalysisResponse.analysis, mockAnalysisResponse.tasks);
    });
  });

  it('should show image preview after selection', async () => {
    const onAnalysis = vi.fn();
    const onError = vi.fn();

    vi.mocked(multimodalService.multimodalService.analyzeImage).mockResolvedValue({
      analysis: 'Test',
      tasks: [],
    });

    render(<ImageUpload onAnalysis={onAnalysis} onError={onError} autoAnalyze={false} />);

    const file = new File(['fake image'], 'test.png', { type: 'image/png' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(input);

    await waitFor(() => {
      const img = screen.getByAltText('Preview');
      expect(img).toBeInTheDocument();
      expect(img).toHaveAttribute('src', 'mock-object-url');
    });
  });

  it('should validate file type', async () => {
    const onAnalysis = vi.fn();
    const onError = vi.fn();

    render(<ImageUpload onAnalysis={onAnalysis} onError={onError} />);

    // Create an invalid file type
    const file = new File(['fake content'], 'test.txt', { type: 'text/plain' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    // Simulate file selection
    fireEvent.change(input, {
      target: { files: [file] },
    });

    await waitFor(() => {
      expect(onError).toHaveBeenCalled();
    });
  });

  it('should validate file size', async () => {
    const onAnalysis = vi.fn();
    const onError = vi.fn();

    render(<ImageUpload onAnalysis={onAnalysis} onError={onError} />);

    // Create a file larger than 20MB
    const largeFile = new File(['x'.repeat(21 * 1024 * 1024)], 'large.png', {
      type: 'image/png',
    });

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    // Simulate file selection
    fireEvent.change(input, {
      target: { files: [largeFile] },
    });

    await waitFor(() => {
      expect(onError).toHaveBeenCalled();
    });
  });

  it('should handle drag and drop', async () => {
    const onAnalysis = vi.fn();
    const onError = vi.fn();

    vi.mocked(multimodalService.multimodalService.analyzeImage).mockResolvedValue({
      analysis: 'Test analysis',
      tasks: [],
    });

    render(<ImageUpload onAnalysis={onAnalysis} onError={onError} autoAnalyze={true} />);

    const dropZone = screen.getByText('Upload image').closest('div');
    expect(dropZone).toBeTruthy();

    const file = new File(['fake image'], 'test.png', { type: 'image/png' });

    const dropEvent = new Event('drop', { bubbles: true });
    Object.defineProperty(dropEvent, 'dataTransfer', {
      value: {
        files: [file],
      },
    });

    fireEvent(dropZone!, dropEvent);

    await waitFor(() => {
      expect(multimodalService.multimodalService.analyzeImage).toHaveBeenCalled();
    });
  });

  it('should show analyzing state', async () => {
    const onAnalysis = vi.fn();
    const onError = vi.fn();

    let resolveAnalysis: any;
    const analysisPromise = new Promise((resolve) => {
      resolveAnalysis = resolve;
    });

    vi.mocked(multimodalService.multimodalService.analyzeImage).mockReturnValue(
      analysisPromise as any
    );

    render(<ImageUpload onAnalysis={onAnalysis} onError={onError} autoAnalyze={true} />);

    const file = new File(['fake image'], 'test.png', { type: 'image/png' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(input);

    await waitFor(() => {
      expect(screen.getByText('Analyzing...')).toBeInTheDocument();
    });

    // Resolve analysis
    resolveAnalysis({ analysis: 'Test', tasks: [] });

    await waitFor(() => {
      expect(onAnalysis).toHaveBeenCalled();
    });
  });

  it('should handle analysis errors', async () => {
    const onAnalysis = vi.fn();
    const onError = vi.fn();

    vi.mocked(multimodalService.multimodalService.analyzeImage).mockRejectedValue(
      new Error('Analysis failed')
    );

    render(<ImageUpload onAnalysis={onAnalysis} onError={onError} autoAnalyze={true} />);

    const file = new File(['fake image'], 'test.png', { type: 'image/png' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    Object.defineProperty(input, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(input);

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith(expect.stringContaining('Analysis failed'));
    });
  });

  it('should allow manual analysis with custom prompt', async () => {
    const onAnalysis = vi.fn();
    const onError = vi.fn();
    const customPrompt = 'Describe this image in detail';

    vi.mocked(multimodalService.multimodalService.analyzeImage).mockResolvedValue({
      analysis: 'Detailed description',
      tasks: [],
    });

    render(
      <ImageUpload
        onAnalysis={onAnalysis}
        onError={onError}
        autoAnalyze={false}
        customPrompt={customPrompt}
      />
    );

    const file = new File(['fake image'], 'test.png', { type: 'image/png' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    // Simulate file selection
    fireEvent.change(input, {
      target: { files: [file] },
    });

    // Wait for preview to appear
    await waitFor(() => {
      expect(screen.getByAltText('Preview')).toBeInTheDocument();
    });

    // Click analyze button
    const analyzeButton = screen.getByText('Analyze Image');
    fireEvent.click(analyzeButton);

    await waitFor(() => {
      expect(multimodalService.multimodalService.analyzeImage).toHaveBeenCalledWith(
        file,
        customPrompt
      );
      expect(onAnalysis).toHaveBeenCalled();
    });
  });

  it('should clean up object URL on unmount', async () => {
    const onAnalysis = vi.fn();
    const onError = vi.fn();

    const { unmount } = render(<ImageUpload onAnalysis={onAnalysis} onError={onError} />);

    const file = new File(['fake image'], 'test.png', { type: 'image/png' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    // Simulate file selection
    fireEvent.change(input, {
      target: { files: [file] },
    });

    await waitFor(() => {
      expect(URL.createObjectURL).toHaveBeenCalled();
    });

    unmount();

    expect(URL.revokeObjectURL).toHaveBeenCalledWith('mock-object-url');
  });

  it('should support multiple image formats', async () => {
    const onAnalysis = vi.fn();
    const onError = vi.fn();

    vi.mocked(multimodalService.multimodalService.analyzeImage).mockResolvedValue({
      analysis: 'Test',
      tasks: [],
    });

    const formats = ['png', 'jpg', 'jpeg', 'webp', 'heic'];

    for (const format of formats) {
      render(<ImageUpload onAnalysis={onAnalysis} onError={onError} autoAnalyze={true} />);

      const file = new File(['fake image'], `test.${format}`, { type: `image/${format}` });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });

      fireEvent.change(input);

      await waitFor(() => {
        expect(multimodalService.multimodalService.analyzeImage).toHaveBeenCalled();
      });

      vi.clearAllMocks();
    }
  });
});
