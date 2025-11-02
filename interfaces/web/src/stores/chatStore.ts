import { create } from 'zustand';
import { chatService } from '../services/chatService';
import type { ChatRequest, ChatResponse } from '@/services/chatService';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatState {
  messages: Message[];
  loading: boolean;
  error: string | null;
  isTyping: boolean;
  sessionId: string | null;

  // Actions
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  clearMessages: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setIsTyping: (isTyping: boolean) => void;

  // API Actions
  sendMessage: (content: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [
    {
      id: '1',
      role: 'assistant',
      content:
        'Olá! 👋 Sou a Charlee, sua assistente pessoal. Como posso ajudá-la hoje? Posso auxiliar com planejamento de tarefas, análise do seu ciclo menstrual, organização dos seus Big Rocks e muito mais!',
      timestamp: new Date(),
    },
  ],
  loading: false,
  error: null,
  isTyping: false,
  sessionId: null,

  setMessages: (messages) => set({ messages }),

  addMessage: (messageData) => {
    const newMessage: Message = {
      ...messageData,
      id: crypto.randomUUID(),
      timestamp: new Date(),
    };
    set((state) => ({ messages: [...state.messages, newMessage] }));
  },

  clearMessages: () => set({ 
    messages: [{
      id: '1',
      role: 'assistant',
      content: 'Olá! 👋 Sou a Charlee. Como posso ajudar?',
      timestamp: new Date(),
    }],
    sessionId: null 
  }),

  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setIsTyping: (isTyping) => set({ isTyping }),

  sendMessage: async (content) => {
    const { addMessage, setIsTyping, setError, sessionId } = get();

    // Add user message
    addMessage({
      role: 'user',
      content,
    });

    // Set typing indicator
    setIsTyping(true);
    setError(null);

    try {
      // Call real API
      const request: ChatRequest = {
        message: content,
        user_id: 'samara',
      };

      if (sessionId) {
        request.session_id = sessionId;
      }

      const response: ChatResponse = await chatService.sendMessage(request);

      // Update session ID
      set({ sessionId: response.session_id });

      // Add assistant response
      addMessage({
        role: 'assistant',
        content: response.response,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(`Erro ao enviar mensagem: ${errorMessage}`);
      
      // Add error message to chat
      addMessage({
        role: 'assistant',
        content: 'Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.',
      });
      
      console.error('Error sending message:', err);
      throw err;
    } finally {
      setIsTyping(false);
    }
  },
}));