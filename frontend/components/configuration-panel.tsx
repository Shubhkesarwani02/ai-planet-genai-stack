"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Upload, X, Settings } from "lucide-react"

interface Node {
  id: string
  type: string
  position: { x: number; y: number }
  data: any
}

interface ConfigurationPanelProps {
  node: Node | null
  onUpdate: (nodeId: string, data: any) => void
  onClose: () => void
}

export function ConfigurationPanel({ node, onUpdate, onClose }: ConfigurationPanelProps) {
  if (!node) return null

  const handleUpdate = (updates: any) => {
    onUpdate(node.id, updates)
  }

  const renderConfiguration = () => {
    switch (node.type) {
      case "user-query":
        return <UserQueryConfig node={node} onUpdate={handleUpdate} />
      case "llm":
        return <LLMConfig node={node} onUpdate={handleUpdate} />
      case "knowledge-base":
        return <KnowledgeBaseConfig node={node} onUpdate={handleUpdate} />
      case "output":
        return <OutputConfig node={node} onUpdate={handleUpdate} />
      case "web-search":
        return <WebSearchConfig node={node} onUpdate={handleUpdate} />
      default:
        return <div className="p-4 text-center text-muted-foreground">No configuration available</div>
    }
  }

  return (
    <div className="w-80 border-l border-border bg-card h-full overflow-y-auto">
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Settings className="w-4 h-4" />
            <h3 className="font-semibold">Configuration</h3>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="p-4">{renderConfiguration()}</div>
    </div>
  )
}

function UserQueryConfig({ node, onUpdate }: { node: Node; onUpdate: (data: any) => void }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">User Query Configuration</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="query-title">Title</Label>
          <Input
            id="query-title"
            value={node.data.title || "User Query"}
            onChange={(e) => onUpdate({ title: e.target.value })}
            placeholder="Enter component title"
          />
        </div>

        <div>
          <Label htmlFor="query-description">Description</Label>
          <Textarea
            id="query-description"
            value={node.data.description || "Enter point for queries"}
            onChange={(e) => onUpdate({ description: e.target.value })}
            placeholder="Enter component description"
            rows={2}
          />
        </div>

        <div>
          <Label htmlFor="query-placeholder">Placeholder Text</Label>
          <Input
            id="query-placeholder"
            value={node.data.placeholder || "Write your query here"}
            onChange={(e) => onUpdate({ placeholder: e.target.value })}
            placeholder="Enter placeholder text"
          />
        </div>

        <div>
          <Label htmlFor="query-default">Default Query</Label>
          <Textarea
            id="query-default"
            value={node.data.query || ""}
            onChange={(e) => onUpdate({ query: e.target.value })}
            placeholder="Enter default query"
            rows={3}
          />
        </div>
      </CardContent>
    </Card>
  )
}

function LLMConfig({ node, onUpdate }: { node: Node; onUpdate: (data: any) => void }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">LLM Configuration</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="llm-provider">Provider</Label>
          <Select 
            value={node.data.provider || "gemini"} 
            onValueChange={(value) => onUpdate({ provider: value })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select provider" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="gemini">Google Gemini</SelectItem>
              <SelectItem value="openai">OpenAI</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="llm-model">Model</Label>
          <Select 
            value={node.data.model || "gemini-2.0-flash-exp"} 
            onValueChange={(value) => onUpdate({ model: value })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select model" />
            </SelectTrigger>
            <SelectContent>
              {(node.data.provider === "openai" || !node.data.provider) ? (
                <>
                  <SelectItem value="gpt-4o-mini">GPT 4o-Mini</SelectItem>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="gpt-3.5-turbo">GPT-3.5-Turbo</SelectItem>
                </>
              ) : (
                <>
                  <SelectItem value="gemini-2.0-flash-exp">Gemini 2.0 Flash</SelectItem>
                  <SelectItem value="gemini-1.5-pro">Gemini 1.5 Pro</SelectItem>
                  <SelectItem value="gemini-1.5-flash">Gemini 1.5 Flash</SelectItem>
                </>
              )}
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="llm-prompt">System Prompt</Label>
          <Textarea
            id="llm-prompt"
            value={node.data.prompt || "You are a helpful AI assistant that answers questions based on the provided context from documents."}
            onChange={(e) => onUpdate({ prompt: e.target.value })}
            placeholder="Enter system prompt"
            rows={4}
          />
        </div>

        <div>
          <Label htmlFor="llm-temperature">Temperature: {node.data.temperature || 0.7}</Label>
          <Slider
            id="llm-temperature"
            min={0}
            max={2}
            step={0.1}
            value={[node.data.temperature || 0.7]}
            onValueChange={(value) => onUpdate({ temperature: value[0] })}
            className="mt-2"
          />
        </div>

        <div>
          <Label htmlFor="llm-max-tokens">Max Tokens</Label>
          <Input
            id="llm-max-tokens"
            type="number"
            value={node.data.maxTokens || 1000}
            onChange={(e) => onUpdate({ maxTokens: Number.parseInt(e.target.value) })}
            placeholder="1000"
          />
        </div>

        <div className="flex items-center space-x-2">
          <Switch
            id="llm-stream"
            checked={node.data.stream || false}
            onCheckedChange={(checked) => onUpdate({ stream: checked })}
          />
          <Label htmlFor="llm-stream">Enable Streaming</Label>
        </div>
      </CardContent>
    </Card>
  )
}

function KnowledgeBaseConfig({ node, onUpdate }: { node: Node; onUpdate: (data: any) => void }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Knowledge Base Configuration</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="kb-file">Upload File</Label>
          <div className="mt-2 flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Upload className="w-4 h-4 mr-2" />
              Choose File
            </Button>
            {node.data.fileName && <span className="text-sm text-muted-foreground">{node.data.fileName}</span>}
          </div>
        </div>

        <div>
          <Label htmlFor="kb-embedding-provider">Embedding Provider</Label>
          <Select 
            value={node.data.embeddingProvider || "gemini"} 
            onValueChange={(value) => onUpdate({ embeddingProvider: value })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select embedding provider" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="gemini">Google Gemini</SelectItem>
              <SelectItem value="openai">OpenAI</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="kb-embedding-model">Embedding Model</Label>
          <Select 
            value={node.data.embeddingModel || "models/embedding-001"} 
            onValueChange={(value) => onUpdate({ embeddingModel: value })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select embedding model" />
            </SelectTrigger>
            <SelectContent>
              {(node.data.embeddingProvider === "openai") ? (
                <>
                  <SelectItem value="text-embedding-3-large">text-embedding-3-large</SelectItem>
                  <SelectItem value="text-embedding-3-small">text-embedding-3-small</SelectItem>
                  <SelectItem value="text-embedding-ada-002">text-embedding-ada-002</SelectItem>
                </>
              ) : (
                <>
                  <SelectItem value="models/embedding-001">Gemini Embedding 001</SelectItem>
                  <SelectItem value="models/text-embedding-004">Gemini Text Embedding 004</SelectItem>
                </>
              )}
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="kb-top-k">Number of Results (Top K)</Label>
          <Input
            id="kb-top-k"
            type="number"
            value={node.data.topK || 5}
            onChange={(e) => onUpdate({ topK: Number.parseInt(e.target.value) })}
            placeholder="5"
            min="1"
            max="20"
          />
        </div>

        <div>
          <Label htmlFor="kb-chunk-size">Chunk Size</Label>
          <Input
            id="kb-chunk-size"
            type="number"
            value={node.data.chunkSize || 800}
            onChange={(e) => onUpdate({ chunkSize: Number.parseInt(e.target.value) })}
            placeholder="800"
          />
        </div>

        <div>
          <Label htmlFor="kb-overlap">Chunk Overlap</Label>
          <Input
            id="kb-overlap"
            type="number"
            value={node.data.chunkOverlap || 100}
            onChange={(e) => onUpdate({ chunkOverlap: Number.parseInt(e.target.value) })}
            placeholder="100"
          />
        </div>

        <div>
          <Label htmlFor="kb-similarity-threshold">Similarity Threshold: {node.data.similarityThreshold || 0.7}</Label>
          <Slider
            id="kb-similarity-threshold"
            min={0}
            max={1}
            step={0.1}
            value={[node.data.similarityThreshold || 0.7]}
            onValueChange={(value) => onUpdate({ similarityThreshold: value[0] })}
            className="mt-2"
          />
        </div>

        <div className="flex items-center space-x-2">
          <Switch
            id="kb-fallback-text-search"
            checked={node.data.fallbackTextSearch !== false}  // Default to true
            onCheckedChange={(checked) => onUpdate({ fallbackTextSearch: checked })}
          />
          <Label htmlFor="kb-fallback-text-search">Enable Text Search Fallback</Label>
        </div>
      </CardContent>
    </Card>
  )
}

function OutputConfig({ node, onUpdate }: { node: Node; onUpdate: (data: any) => void }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Output Configuration</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="output-format">Output Format</Label>
          <Select value={node.data.format || "text"} onValueChange={(value) => onUpdate({ format: value })}>
            <SelectTrigger>
              <SelectValue placeholder="Select output format" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="text">Plain Text</SelectItem>
              <SelectItem value="markdown">Markdown</SelectItem>
              <SelectItem value="json">JSON</SelectItem>
              <SelectItem value="html">HTML</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="output-template">Output Template</Label>
          <Textarea
            id="output-template"
            value={node.data.template || ""}
            onChange={(e) => onUpdate({ template: e.target.value })}
            placeholder="Enter output template (optional)"
            rows={4}
          />
        </div>

        <div className="flex items-center space-x-2">
          <Switch
            id="output-save"
            checked={node.data.saveToFile || false}
            onCheckedChange={(checked) => onUpdate({ saveToFile: checked })}
          />
          <Label htmlFor="output-save">Save to File</Label>
        </div>

        {node.data.saveToFile && (
          <div>
            <Label htmlFor="output-filename">Filename</Label>
            <Input
              id="output-filename"
              value={node.data.filename || "output.txt"}
              onChange={(e) => onUpdate({ filename: e.target.value })}
              placeholder="output.txt"
            />
          </div>
        )}

        <div>
          <Label htmlFor="output-preview">Preview</Label>
          <Textarea
            id="output-preview"
            value={node.data.text || "Output will be generated based on query"}
            readOnly
            className="bg-muted"
            rows={4}
          />
        </div>
      </CardContent>
    </Card>
  )
}

function WebSearchConfig({ node, onUpdate }: { node: Node; onUpdate: (data: any) => void }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Web Search Configuration</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="ws-tool">Search Tool</Label>
          <Select value={node.data.tool} onValueChange={(value) => onUpdate({ tool: value })}>
            <SelectTrigger>
              <SelectValue placeholder="Select search tool" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="SERF API">SERF API</SelectItem>
              <SelectItem value="Google Search">Google Search</SelectItem>
              <SelectItem value="Bing Search">Bing Search</SelectItem>
              <SelectItem value="DuckDuckGo">DuckDuckGo</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="ws-api-key">API Key</Label>
          <Input
            id="ws-api-key"
            type="password"
            value={node.data.apiKey || ""}
            onChange={(e) => onUpdate({ apiKey: e.target.value })}
            placeholder="Enter your API key"
          />
        </div>

        <div>
          <Label htmlFor="ws-results-count">Number of Results</Label>
          <Input
            id="ws-results-count"
            type="number"
            value={node.data.resultsCount || 10}
            onChange={(e) => onUpdate({ resultsCount: Number.parseInt(e.target.value) })}
            placeholder="10"
            min="1"
            max="50"
          />
        </div>

        <div>
          <Label htmlFor="ws-region">Search Region</Label>
          <Select value={node.data.region || "us"} onValueChange={(value) => onUpdate({ region: value })}>
            <SelectTrigger>
              <SelectValue placeholder="Select region" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="us">United States</SelectItem>
              <SelectItem value="uk">United Kingdom</SelectItem>
              <SelectItem value="ca">Canada</SelectItem>
              <SelectItem value="au">Australia</SelectItem>
              <SelectItem value="de">Germany</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="ws-language">Language</Label>
          <Select value={node.data.language || "en"} onValueChange={(value) => onUpdate({ language: value })}>
            <SelectTrigger>
              <SelectValue placeholder="Select language" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="en">English</SelectItem>
              <SelectItem value="es">Spanish</SelectItem>
              <SelectItem value="fr">French</SelectItem>
              <SelectItem value="de">German</SelectItem>
              <SelectItem value="zh">Chinese</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center space-x-2">
          <Switch
            id="ws-safe-search"
            checked={node.data.safeSearch || true}
            onCheckedChange={(checked) => onUpdate({ safeSearch: checked })}
          />
          <Label htmlFor="ws-safe-search">Safe Search</Label>
        </div>
      </CardContent>
    </Card>
  )
}
