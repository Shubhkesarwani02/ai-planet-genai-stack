"use client"

import { useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Bot, ArrowLeft, Save, Play, ZoomIn, ZoomOut, Settings } from "lucide-react"
import Link from "next/link"
import { WorkflowCanvas } from "@/components/workflow-canvas"
import { ComponentSidebar } from "@/components/component-sidebar"
import { ConfigurationPanel } from "@/components/configuration-panel"

interface WorkflowNode {
  id: string
  type: "user-query" | "llm" | "knowledge-base" | "output" | "web-search"
  position: { x: number; y: number }
  data: any
}

interface WorkflowConnection {
  id: string
  source: string
  target: string
}

export default function WorkflowBuilder({ params }: { params: { id: string } }) {
  const [nodes, setNodes] = useState<WorkflowNode[]>([])
  const [connections, setConnections] = useState<WorkflowConnection[]>([])
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [showConfigPanel, setShowConfigPanel] = useState(false)
  const [zoom, setZoom] = useState(100)

  const loadSampleWorkflow = useCallback(() => {
    const sampleNodes: WorkflowNode[] = [
      {
        id: "user-query-1",
        type: "user-query",
        position: { x: 50, y: 100 },
        data: {
          query: "Can you share stock records of Coca Cola and Pepsi for last 5 years?",
          placeholder: "Write your query here",
          title: "User Query",
          description: "Enter point for queries",
        },
      },
      {
        id: "knowledge-base-1",
        type: "knowledge-base",
        position: { x: 50, y: 300 },
        data: {
          fileName: "AlPlanet_file.pdf",
          embeddingModel: "text-embedding-3-large",
          apiKey: "sk-...",
          chunkSize: 1000,
          chunkOverlap: 200,
          similarityThreshold: 0.7,
        },
      },
      {
        id: "llm-1",
        type: "llm",
        position: { x: 400, y: 200 },
        data: {
          model: "GPT 4o-Mini",
          apiKey: "sk-...",
          prompt:
            "You are a helpful PDF assistant. Use web search if the PDF lacks context\n\nCONTEXT: {context}\nUser Query: {query}",
          temperature: 0.75,
          maxTokens: 1000,
          stream: false,
        },
      },
      {
        id: "web-search-1",
        type: "web-search",
        position: { x: 400, y: 400 },
        data: {
          tool: "SERF API",
          apiKey: "sk-...",
          resultsCount: 10,
          region: "us",
          language: "en",
          safeSearch: true,
        },
      },
      {
        id: "output-1",
        type: "output",
        position: { x: 750, y: 200 },
        data: {
          text: "Output will be generated based on query",
          format: "text",
          template: "",
          saveToFile: false,
          filename: "output.txt",
        },
      },
    ]

    const sampleConnections: WorkflowConnection[] = [
      { id: "user-query-1-llm-1", source: "user-query-1", target: "llm-1" },
      { id: "knowledge-base-1-llm-1", source: "knowledge-base-1", target: "llm-1" },
      { id: "web-search-1-llm-1", source: "web-search-1", target: "llm-1" },
      { id: "llm-1-output-1", source: "llm-1", target: "output-1" },
    ]

    setNodes(sampleNodes)
    setConnections(sampleConnections)
  }, [])

  const handleAddNode = useCallback((type: WorkflowNode["type"], position: { x: number; y: number }) => {
    const newNode: WorkflowNode = {
      id: `${type}-${Date.now()}`,
      type,
      position,
      data: getDefaultNodeData(type),
    }
    setNodes((prev) => [...prev, newNode])
  }, [])

  const handleNodeUpdate = useCallback((nodeId: string, data: any) => {
    setNodes((prev) => prev.map((node) => (node.id === nodeId ? { ...node, data: { ...node.data, ...data } } : node)))
  }, [])

  const handleNodeMove = useCallback((nodeId: string, position: { x: number; y: number }) => {
    setNodes((prev) => prev.map((node) => (node.id === nodeId ? { ...node, position } : node)))
  }, [])

  const handleConnect = useCallback((sourceId: string, targetId: string) => {
    const connectionId = `${sourceId}-${targetId}`
    setConnections((prev) => [...prev, { id: connectionId, source: sourceId, target: targetId }])
  }, [])

  const handleNodeSelect = useCallback((nodeId: string | null) => {
    setSelectedNode(nodeId)
    setShowConfigPanel(!!nodeId)
  }, [])

  const handleSaveWorkflow = useCallback(() => {
    const workflowData = {
      nodes,
      connections,
      lastModified: new Date().toISOString(),
    }
    localStorage.setItem(`workflow-${params.id}`, JSON.stringify(workflowData))
    console.log("Workflow saved:", workflowData)
  }, [nodes, connections, params.id])

  useState(() => {
    const savedWorkflow = localStorage.getItem(`workflow-${params.id}`)
    if (savedWorkflow) {
      try {
        const { nodes: savedNodes, connections: savedConnections } = JSON.parse(savedWorkflow)
        setNodes(savedNodes || [])
        setConnections(savedConnections || [])
      } catch (error) {
        console.error("Failed to load saved workflow:", error)
        loadSampleWorkflow()
      }
    } else {
      loadSampleWorkflow()
    }
  })

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="w-4 h-4" />
              </Button>
            </Link>
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-8 h-8 bg-blue-600 rounded-lg">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-semibold text-foreground">GenAI Stack</h1>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 bg-muted rounded-lg p-1">
              <Button variant="ghost" size="icon" onClick={() => setZoom(Math.max(25, zoom - 25))} className="h-8 w-8">
                <ZoomOut className="w-4 h-4" />
              </Button>
              <span className="text-sm font-medium px-2 min-w-[3rem] text-center">{zoom}%</span>
              <Button variant="ghost" size="icon" onClick={() => setZoom(Math.min(200, zoom + 25))} className="h-8 w-8">
                <ZoomIn className="w-4 h-4" />
              </Button>
            </div>

            <Button variant="outline" onClick={handleSaveWorkflow}>
              <Save className="w-4 h-4 mr-2" />
              Save
            </Button>

            <Link href={`/chat/${params.id}`}>
              <Button className="bg-green-600 hover:bg-green-700 text-white">
                <Play className="w-4 h-4 mr-2" />
                Chat with Stack
              </Button>
            </Link>

            <Button
              variant="outline"
              size="icon"
              onClick={() => setShowConfigPanel(!showConfigPanel)}
              className={showConfigPanel ? "bg-muted" : ""}
            >
              <Settings className="w-4 h-4" />
            </Button>

            <div className="flex items-center justify-center w-8 h-8 bg-muted rounded-full">
              <span className="text-sm font-medium">S</span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <ComponentSidebar onAddNode={handleAddNode} />

        {/* Main Canvas */}
        <div className="flex-1 relative">
          <WorkflowCanvas
            nodes={nodes}
            connections={connections}
            selectedNode={selectedNode}
            zoom={zoom}
            onNodeSelect={handleNodeSelect}
            onNodeMove={handleNodeMove}
            onNodeUpdate={handleNodeUpdate}
            onConnect={handleConnect}
            onAddNode={handleAddNode}
          />
        </div>

        {/* Configuration Panel */}
        {showConfigPanel && (
          <ConfigurationPanel
            node={nodes.find((n) => n.id === selectedNode) || null}
            onUpdate={handleNodeUpdate}
            onClose={() => {
              setShowConfigPanel(false)
              setSelectedNode(null)
            }}
          />
        )}
      </div>
    </div>
  )
}

function getDefaultNodeData(type: WorkflowNode["type"]) {
  switch (type) {
    case "user-query":
      return {
        query: "",
        placeholder: "Write your query here",
        title: "User Query",
        description: "Enter point for queries",
      }
    case "llm":
      return {
        model: "GPT 4o-Mini",
        apiKey: "",
        prompt: "You are a helpful PDF assistant. Use web search if the PDF lacks context",
        temperature: 0.75,
        maxTokens: 1000,
        stream: false,
      }
    case "knowledge-base":
      return {
        fileName: null,
        embeddingModel: "text-embedding-3-large",
        apiKey: "",
        chunkSize: 1000,
        chunkOverlap: 200,
        similarityThreshold: 0.7,
      }
    case "output":
      return {
        text: "Output will be generated based on query",
        format: "text",
        template: "",
        saveToFile: false,
        filename: "output.txt",
      }
    case "web-search":
      return {
        tool: "SERF API",
        apiKey: "",
        resultsCount: 10,
        region: "us",
        language: "en",
        safeSearch: true,
      }
    default:
      return {}
  }
}
