"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Bot, ArrowLeft, Send, User, Loader2, Settings, Play, Save, ZoomIn, ZoomOut } from "lucide-react"
import Link from "next/link"
import { ProtectedRoute } from "@/components/ProtectedRoute"
import { apiClient, type Workspace, type ChatMessage as ApiChatMessage, type ChatResponse } from "@/lib/api"

interface Message {
  id: string
  type: "user" | "assistant" | "system"
  content: string
  timestamp: Date
  context_chunks?: string[]
}

interface ChatSidebarProps {
  stackId: string
}

function ChatSidebar({ stackId }: ChatSidebarProps) {
  return (
    <div className="w-80 border-r border-border bg-card p-4 overflow-y-auto">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground mb-2">Chat With AI</h2>
        <div className="space-y-3">
          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-2">Agents</h3>
            <div className="space-y-1">
              <div className="flex items-center gap-2 p-2 rounded-lg bg-muted/50">
                <Bot className="w-4 h-4 text-blue-600" />
                <span className="text-sm">AI Assistant</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-2">Tools</h3>
            <div className="space-y-1">
              <div className="flex items-center gap-2 p-2 rounded-lg bg-muted/50">
                <Settings className="w-4 h-4 text-green-600" />
                <span className="text-sm">Knowledge Base</span>
              </div>
              <div className="flex items-center gap-2 p-2 rounded-lg bg-muted/50">
                <Settings className="w-4 h-4 text-purple-600" />
                <span className="text-sm">Web Search</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-2">LLMs</h3>
            <div className="space-y-1">
              <div className="flex items-center gap-2 p-2 rounded-lg bg-blue-50 border border-blue-200">
                <Bot className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium">Gemini Pro</span>
              </div>
              <div className="flex items-center gap-2 p-2 rounded-lg bg-muted/50">
                <Bot className="w-4 h-4 text-gray-600" />
                <span className="text-sm">Gemini Flash</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center gap-1 bg-muted rounded-lg p-1">
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <ZoomOut className="w-4 h-4" />
          </Button>
          <span className="text-sm font-medium px-2 min-w-[3rem] text-center">100%</span>
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <ZoomIn className="w-4 h-4" />
          </Button>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="flex-1 bg-transparent">
            <Play className="w-4 h-4 mr-1" />
            Run
          </Button>
          <Button variant="outline" size="sm" className="flex-1 bg-transparent">
            <Save className="w-4 h-4 mr-1" />
            Save
          </Button>
        </div>
      </div>
    </div>
  )
}

export default function ChatInterface({ params }: { params: { id: string } }) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "system",
      content: "Start a conversation to ask questions about your uploaded documents",
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [workspace, setWorkspace] = useState<any>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    loadWorkspace()
    loadChatHistory()
  }, [params.id])

  const loadWorkspace = async () => {
    try {
      const workspaceData = await apiClient.getWorkspace(params.id)
      setWorkspace(workspaceData)
    } catch (error) {
      console.error('Failed to load workspace:', error)
    }
  }

  const loadChatHistory = async () => {
    try {
      const history = await apiClient.getChatHistory(params.id)
      const chatMessages: Message[] = history.map((chat: any) => [
        {
          id: `${chat.id}-user`,
          type: "user" as const,
          content: chat.query,
          timestamp: new Date(chat.created_at)
        },
        {
          id: `${chat.id}-assistant`,
          type: "assistant" as const,
          content: chat.response,
          timestamp: new Date(chat.created_at),
          context_chunks: []
        }
      ]).flat()
      
      setMessages(prev => [
        ...prev.filter(m => m.type === "system"),
        ...chatMessages
      ])
    } catch (error) {
      console.error('Failed to load chat history:', error)
    }
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const query = inputValue
    setInputValue("")
    setIsLoading(true)

    try {
      const response = await apiClient.sendMessage(params.id, query)
      
      const aiResponse: Message = {
        id: response.chat_log.id,
        type: "assistant",
        content: response.response,
        timestamp: new Date(response.chat_log.created_at),
        context_chunks: response.context_chunks || []
      }
      
      setMessages((prev) => [...prev, aiResponse])
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: "Sorry, I encountered an error processing your message. Please try again.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorResponse])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <ProtectedRoute>
      <div className="h-screen flex flex-col bg-background">
        {/* Header */}
        <header className="border-b border-border bg-card px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href={`/builder/${params.id}`}>
                <Button variant="ghost" size="icon">
                  <ArrowLeft className="w-4 h-4" />
                </Button>
              </Link>
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-8 h-8 bg-blue-600 rounded-lg">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-xl font-semibold text-foreground">GenAI Stack Chat</h1>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-8 h-8 bg-muted rounded-full">
                <span className="text-sm font-medium">S</span>
              </div>
            </div>
          </div>
        </header>

        <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <ChatSidebar stackId={params.id} />

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`flex gap-3 max-w-3xl ${message.type === "user" ? "flex-row-reverse" : "flex-row"}`}>
                  <div
                    className={`flex items-center justify-center w-8 h-8 rounded-full flex-shrink-0 ${
                      message.type === "user"
                        ? "bg-blue-600 text-white"
                        : message.type === "system"
                          ? "bg-muted text-muted-foreground"
                          : "bg-green-600 text-white"
                    }`}
                  >
                    {message.type === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>

                  <Card
                    className={`${
                      message.type === "user"
                        ? "bg-blue-600 text-white border-blue-600"
                        : message.type === "system"
                          ? "bg-muted border-muted"
                          : "bg-card border-border"
                    }`}
                  >
                    <CardContent className="p-4">
                      <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</div>
                      <div
                        className={`text-xs mt-2 ${
                          message.type === "user"
                            ? "text-blue-100"
                            : message.type === "system"
                              ? "text-muted-foreground"
                              : "text-muted-foreground"
                        }`}
                      >
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="flex gap-3 max-w-3xl">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-green-600 text-white flex-shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                  <Card className="bg-card border-border">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Thinking...
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-border bg-card p-4">
            <div className="flex gap-3 max-w-4xl mx-auto">
              <div className="flex-1 relative">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Send a message"
                  className="pr-12"
                  disabled={isLoading}
                />
                <Button
                  size="icon"
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  className="absolute right-1 top-1 h-8 w-8 bg-blue-600 hover:bg-blue-700 text-white"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
      </div>
    </ProtectedRoute>
  )
}
