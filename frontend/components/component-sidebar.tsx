"use client"

import type React from "react"

import { Card, CardContent } from "@/components/ui/card"
import { MessageSquare, Bot, Database, FileText, Search } from "lucide-react"

interface ComponentSidebarProps {
  onAddNode: (type: string, position: { x: number; y: number }) => void
}

export function ComponentSidebar({ onAddNode }: ComponentSidebarProps) {
  const components = [
    {
      id: "user-query",
      name: "User Query",
      description: "Enter point for queries",
      icon: MessageSquare,
      color: "bg-blue-100 text-blue-600",
    },
    {
      id: "llm",
      name: "LLM (OpenAI)",
      description: "Run a query with OpenAI LLM",
      icon: Bot,
      color: "bg-purple-100 text-purple-600",
    },
    {
      id: "knowledge-base",
      name: "Knowledge Base",
      description: "Let LLM search info in your file",
      icon: Database,
      color: "bg-green-100 text-green-600",
    },
    {
      id: "output",
      name: "Output",
      description: "Output of the result nodes as text",
      icon: FileText,
      color: "bg-orange-100 text-orange-600",
    },
    {
      id: "web-search",
      name: "Web Search",
      description: "Search the web for information",
      icon: Search,
      color: "bg-red-100 text-red-600",
    },
  ]

  const handleDragStart = (e: React.DragEvent, componentType: string) => {
    e.dataTransfer.setData("application/reactflow", componentType)
    e.dataTransfer.effectAllowed = "move"
  }

  return (
    <div className="w-80 border-r border-border bg-card p-4 overflow-y-auto">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground mb-2">Chat With AI</h2>
        <h3 className="text-sm font-medium text-muted-foreground mb-4">Components</h3>
      </div>

      <div className="space-y-3">
        {components.map((component) => {
          const IconComponent = component.icon
          return (
            <Card
              key={component.id}
              className="cursor-grab active:cursor-grabbing hover:shadow-md transition-shadow"
              draggable
              onDragStart={(e) => handleDragStart(e, component.id)}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-lg ${component.color}`}>
                    <IconComponent className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-sm text-foreground mb-1">{component.name}</h4>
                    <p className="text-xs text-muted-foreground leading-relaxed">{component.description}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
