"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { MessageSquare, Bot, Database, FileText, Search, Upload, Link } from "lucide-react"

interface Node {
  id: string
  type: string
  position: { x: number; y: number }
  data: any
}

interface WorkflowNodeProps {
  node: Node
  isSelected: boolean
  isConnecting?: boolean
  onUpdate: (data: any) => void
}

export function WorkflowNode({ node, isSelected, isConnecting = false, onUpdate }: WorkflowNodeProps) {
  const getNodeConfig = () => {
    switch (node.type) {
      case "user-query":
        return {
          title: "User Query",
          icon: MessageSquare,
          color: "border-blue-500",
          bgColor: "bg-blue-50",
        }
      case "llm":
        return {
          title: "LLM (OpenAI)",
          icon: Bot,
          color: "border-purple-500",
          bgColor: "bg-purple-50",
        }
      case "knowledge-base":
        return {
          title: "Knowledge Base",
          icon: Database,
          color: "border-green-500",
          bgColor: "bg-green-50",
        }
      case "output":
        return {
          title: "Output",
          icon: FileText,
          color: "border-orange-500",
          bgColor: "bg-orange-50",
        }
      case "web-search":
        return {
          title: "Web Search",
          icon: Search,
          color: "border-red-500",
          bgColor: "bg-red-50",
        }
      default:
        return {
          title: "Unknown",
          icon: MessageSquare,
          color: "border-gray-500",
          bgColor: "bg-gray-50",
        }
    }
  }

  const config = getNodeConfig()
  const IconComponent = config.icon

  const renderNodeContent = () => {
    switch (node.type) {
      case "user-query":
        return (
          <div className="space-y-3">
            <div>
              <Label className="text-xs text-muted-foreground">User Query</Label>
              <Textarea
                placeholder={node.data.placeholder}
                value={node.data.query}
                onChange={(e) => onUpdate({ query: e.target.value })}
                className="mt-1 text-sm"
                rows={2}
              />
            </div>
          </div>
        )

      case "llm":
        return (
          <div className="space-y-3">
            <div>
              <Label className="text-xs text-muted-foreground">Model</Label>
              <Select value={node.data.model} onValueChange={(value) => onUpdate({ model: value })}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="GPT 4o-Mini">GPT 4o-Mini</SelectItem>
                  <SelectItem value="GPT-4">GPT-4</SelectItem>
                  <SelectItem value="GPT-3.5-Turbo">GPT-3.5-Turbo</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs text-muted-foreground">API Key</Label>
              <Input
                type="password"
                placeholder="******************"
                value={node.data.apiKey}
                onChange={(e) => onUpdate({ apiKey: e.target.value })}
                className="mt-1 text-sm"
              />
            </div>
            <div>
              <Label className="text-xs text-muted-foreground">Prompt</Label>
              <Textarea
                value={node.data.prompt}
                onChange={(e) => onUpdate({ prompt: e.target.value })}
                className="mt-1 text-sm"
                rows={3}
              />
            </div>
            <div>
              <Label className="text-xs text-muted-foreground">Temperature</Label>
              <Input
                type="number"
                min="0"
                max="2"
                step="0.1"
                value={node.data.temperature}
                onChange={(e) => onUpdate({ temperature: Number.parseFloat(e.target.value) })}
                className="mt-1 text-sm"
              />
            </div>
          </div>
        )

      case "knowledge-base":
        return (
          <div className="space-y-3">
            <div>
              <Label className="text-xs text-muted-foreground">File for Knowledge Base</Label>
              <div className="mt-1 flex items-center gap-2">
                <Button variant="outline" size="sm" className="text-xs bg-transparent">
                  <Upload className="w-3 h-3 mr-1" />
                  Upload File
                </Button>
                {node.data.fileName && <span className="text-xs text-muted-foreground">{node.data.fileName}</span>}
              </div>
            </div>
            <div>
              <Label className="text-xs text-muted-foreground">Embedding Model</Label>
              <Select value={node.data.embeddingModel} onValueChange={(value) => onUpdate({ embeddingModel: value })}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="text-embedding-3-large">text-embedding-3-large</SelectItem>
                  <SelectItem value="text-embedding-3-small">text-embedding-3-small</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs text-muted-foreground">API Key</Label>
              <Input
                type="password"
                placeholder="******************"
                value={node.data.apiKey}
                onChange={(e) => onUpdate({ apiKey: e.target.value })}
                className="mt-1 text-sm"
              />
            </div>
          </div>
        )

      case "output":
        return (
          <div className="space-y-3">
            <div>
              <Label className="text-xs text-muted-foreground">Output Text</Label>
              <Textarea
                value={node.data.text}
                onChange={(e) => onUpdate({ text: e.target.value })}
                className="mt-1 text-sm"
                rows={3}
                readOnly
              />
            </div>
          </div>
        )

      case "web-search":
        return (
          <div className="space-y-3">
            <div>
              <Label className="text-xs text-muted-foreground">WebSearch Tool</Label>
              <Select value={node.data.tool} onValueChange={(value) => onUpdate({ tool: value })}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="SERF API">SERF API</SelectItem>
                  <SelectItem value="Google Search">Google Search</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs text-muted-foreground">API Key</Label>
              <Input
                type="password"
                placeholder="******************"
                value={node.data.apiKey}
                onChange={(e) => onUpdate({ apiKey: e.target.value })}
                className="mt-1 text-sm"
              />
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <Card
      className={`w-80 cursor-pointer transition-all relative ${
        isSelected ? `${config.color} shadow-lg` : "border-border"
      } ${config.bgColor} ${isConnecting ? "ring-2 ring-blue-500 ring-opacity-50" : ""}`}
    >
      {isConnecting && (
        <div className="absolute -top-2 -right-2 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
          <Link className="w-3 h-3 text-white" />
        </div>
      )}

      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          <IconComponent className="w-4 h-4" />
          {config.title}
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-0">{renderNodeContent()}</CardContent>
    </Card>
  )
}
