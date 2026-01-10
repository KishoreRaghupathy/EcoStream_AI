'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import { sendChat } from '@/services/api';
import { ChatMessage } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { clsx } from 'clsx';

export function AIAnalyst() {
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            id: '1',
            role: 'assistant',
            content: 'Hello! I am your AI Air Quality Analyst. Ask me anything about current trends, forecasts, or potential pollution sources.',
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const mutation = useMutation({
        mutationFn: sendChat,
        onSuccess: (data) => {
            const botMsg: ChatMessage = {
                id: Date.now().toString(),
                role: 'assistant',
                content: data.response,
                sources: data.sources,
                timestamp: new Date()
            };
            setMessages((prev) => [...prev, botMsg]);
        },
        onError: () => {
            const errorMsg: ChatMessage = {
                id: Date.now().toString(),
                role: 'assistant',
                content: 'Sorry, I encountered an error connecting to the analyst service.',
                timestamp: new Date()
            };
            setMessages((prev) => [...prev, errorMsg]);
        }
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date()
        };
        setMessages((prev) => [...prev, userMsg]);
        mutation.mutate(input);
        setInput('');
    };

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <Card className="flex flex-col h-[500px]">
            <CardHeader className="border-b bg-muted/20 pb-4">
                <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-purple-500" />
                    <CardTitle className="text-lg">AI Analyst</CardTitle>
                </div>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={clsx(
                            "flex gap-3 max-w-[90%]",
                            msg.role === 'user' ? "ml-auto flex-row-reverse" : ""
                        )}
                    >
                        <div className={clsx(
                            "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                            msg.role === 'user' ? "bg-primary text-primary-foreground" : "bg-muted"
                        )}>
                            {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                        </div>
                        <div className={clsx(
                            "rounded-lg p-3 text-sm",
                            msg.role === 'user' ? "bg-primary text-primary-foreground" : "bg-muted"
                        )}>
                            <p>{msg.content}</p>
                            {msg.sources && msg.sources.length > 0 && (
                                <div className="mt-2 text-xs opacity-70 border-t border-black/10 pt-1">
                                    Sources: {msg.sources.join(', ')}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {mutation.isPending && (
                    <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center shrink-0">
                            <Bot className="w-4 h-4" />
                        </div>
                        <div className="bg-muted rounded-lg p-3 text-sm flex items-center gap-1">
                            <span className="animate-bounce">.</span>
                            <span className="animate-bounce delay-100">.</span>
                            <span className="animate-bounce delay-200">.</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </CardContent>
            <CardFooter className="p-3 border-t">
                <form onSubmit={handleSubmit} className="flex w-full gap-2">
                    <Input
                        placeholder="Ask about PM2.5 trends..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={mutation.isPending}
                        className="flex-1"
                    />
                    <Button type="submit" size="icon" disabled={mutation.isPending || !input.trim()}>
                        <Send className="w-4 h-4" />
                    </Button>
                </form>
            </CardFooter>
        </Card>
    );
}
