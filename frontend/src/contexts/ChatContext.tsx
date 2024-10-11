import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { AliceTask } from '../types/TaskTypes';
import { AliceChat } from '../types/ChatTypes';
import { MessageType } from '../types/MessageTypes';
import { useAuth } from './AuthContext';
import { useApi } from './ApiContext';
import Logger from '../utils/Logger';
import { globalEventEmitter } from '../utils/EventEmitter';

interface ChatContextType {
    messages: MessageType[];
    setMessages: React.Dispatch<React.SetStateAction<MessageType[]>>;
    pastChats: AliceChat[];
    setPastChats: React.Dispatch<React.SetStateAction<AliceChat[]>>;
    currentChatId: string | null;
    setCurrentChatId: React.Dispatch<React.SetStateAction<string | null>>;
    isGenerating: boolean;
    setIsGenerating: React.Dispatch<React.SetStateAction<boolean>>;
    handleSelectChat: (chatId: string) => Promise<void>;
    handleSendMessage: (currentChatId: string, message: MessageType) => Promise<void>;
    generateResponse: () => Promise<void>;
    handleRegenerateResponse: () => Promise<void>;
    fetchChats: () => Promise<void>;
    currentChat: AliceChat | null;
    addTaskToChat: (taskId: string) => Promise<void>;
    isTaskInChat: (taskId: string) => boolean;
}

const ChatContext = createContext<ChatContextType | null>(null);

interface ChatProviderProps {
    children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
    const { fetchItem, updateItem, sendMessage, generateChatResponse } = useApi();
    const [messages, setMessages] = useState<MessageType[]>([]);
    const [pastChats, setPastChats] = useState<AliceChat[]>([]);
    const [currentChatId, setCurrentChatId] = useState<string | null>(null);
    const [isGenerating, setIsGenerating] = useState<boolean>(false);
    const [currentChat, setCurrentChat] = useState<AliceChat | null>(null);
    const { user } = useAuth();

    const fetchChats = useCallback(async () => {
        try {
            const chats = await fetchItem('chats') as AliceChat[];
            setPastChats(chats);
        } catch (error) {
            Logger.error('Error fetching chats:', error);
        }
    }, [fetchItem]);

    useEffect(() => {
        if (user) {
            fetchChats();
        }
    }, [user, fetchChats]);

    const fetchChatById = useCallback(async (chatId: string): Promise<AliceChat> => {
        try {
            const chatData = await fetchItem('chats', chatId) as AliceChat;
            return chatData;
        } catch (error) {
            Logger.error('Error fetching chat by id:', error);
            throw error;
        }
    }, [fetchItem]);

    const fetchCurrentChat = useCallback(async () => {
        if (!currentChatId) return;
        try {
            const chatData = await fetchChatById(currentChatId)
            setCurrentChat(chatData);
            setMessages(chatData.messages);
        } catch (error) {
            Logger.error('Error fetching current chat:', error);
        }
    }, [currentChatId, fetchChatById]);
    
    useEffect(() => {
        globalEventEmitter.on('created:chats', fetchChats);
        globalEventEmitter.on('updated:chats', fetchCurrentChat);

        return () => {
            globalEventEmitter.off('created:chats', fetchChats);
            globalEventEmitter.off('updated:chats', fetchCurrentChat);
        };
    }, [currentChatId, fetchChats, fetchCurrentChat]);


    const handleSelectChat = async (chatId: string) => {
        try {
            const chatData = await fetchChatById(chatId);
            setCurrentChat(chatData);
            setMessages(chatData.messages);
            setCurrentChatId(chatId);
        } catch (error) {
            Logger.error('Error fetching chat:', error);
        }
    };

    const handleSendMessage = async (currentChatId: string, message: MessageType) => {
        try {
            Logger.debug('Sending message:', message);
            setMessages(prevMessages => [...prevMessages, message]);
            await sendMessage(currentChatId, message);
            await generateResponse();
        } catch (error) {
            Logger.error('Error sending message or generating response:', error);
        }
    };

    const generateResponse = async () => {
        if (!currentChatId) return;
        setIsGenerating(true);
        try {
            const response = await generateChatResponse(currentChatId);
            if (response) {
                await fetchCurrentChat();
            }
        } catch (error) {
            Logger.error('Error generating response:', error);
        } finally {
            setIsGenerating(false);
        }
    };

    const handleRegenerateResponse = async () => {
        if (!currentChatId) return;
        let newMessages = [...messages];
        while (newMessages.length > 0 && newMessages[newMessages.length - 1].role !== 'user') {
            newMessages.pop();
        }
        try {
            await updateItem("chats", currentChatId, { messages: newMessages });
            setMessages(newMessages);
            await generateResponse();
        } catch (error) {
            Logger.error('Error regenerating response:', error);
        }
    };
    const isTaskInChat = (taskId: string): boolean => {
        return currentChat?.functions?.some(task => task._id === taskId) || false;
    };

    const addTaskToChat = async (taskId: string) => {
        if (!currentChatId || !currentChat) return;
        try {
            const task = await fetchItem("tasks", taskId) as AliceTask;
            if (!task) return Logger.error('Task not found', taskId);
            if (isTaskInChat(taskId)) return Logger.warn('Task already in chat');
            const updatedFunctions = [
                ...(currentChat.functions || []), task
            ];
            await updateItem("chats", currentChatId, { functions: updatedFunctions });
            await handleSelectChat(currentChatId);
        } catch (error) {
            Logger.error('Error adding tasks to chat:', error);
        }
    };

    const value: ChatContextType = {
        messages,
        setMessages,
        pastChats,
        setPastChats,
        currentChatId,
        setCurrentChatId,
        isGenerating,
        setIsGenerating,
        handleSelectChat,
        handleSendMessage,
        generateResponse,
        handleRegenerateResponse,
        fetchChats,
        currentChat,
        addTaskToChat,
        isTaskInChat
    };

    return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChat = (): ChatContextType => {
    const context = useContext(ChatContext);
    if (context === null) {
        throw new Error('useChat must be used within a ChatProvider');
    }
    return context;
};