"use client"

import type React from "react"

import { useCallback, useRef, useState } from "react"
import { WorkflowNode } from "@/components/workflow-node"

interface Node {
  id: string
  type: string
  position: { x: number; y: number }
  data: any
}

interface Connection {
  id: string
  source: string
  target: string
}

interface WorkflowCanvasProps {
  nodes: Node[]
  connections: Connection[]
  selectedNode: string | null
  zoom: number
  onNodeSelect: (nodeId: string | null) => void
  onNodeMove: (nodeId: string, position: { x: number; y: number }) => void
  onNodeUpdate: (nodeId: string, data: any) => void
  onConnect: (sourceId: string, targetId: string) => void
  onAddNode: (type: string, position: { x: number; y: number }) => void
}

export function WorkflowCanvas({
  nodes,
  connections,
  selectedNode,
  zoom,
  onNodeSelect,
  onNodeMove,
  onNodeUpdate,
  onConnect,
  onAddNode,
}: WorkflowCanvasProps) {
  const canvasRef = useRef<HTMLDivElement>(null)
  const [draggedNode, setDraggedNode] = useState<string | null>(null)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const [isConnecting, setIsConnecting] = useState(false)
  const [connectionStart, setConnectionStart] = useState<string | null>(null)

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()

      const reactFlowBounds = canvasRef.current?.getBoundingClientRect()
      if (!reactFlowBounds) return

      const type = e.dataTransfer.getData("application/reactflow")
      if (!type) return

      const position = {
        x: (e.clientX - reactFlowBounds.left - 150) / (zoom / 100),
        y: (e.clientY - reactFlowBounds.top - 50) / (zoom / 100),
      }

      onAddNode(type, position)
    },
    [onAddNode, zoom],
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = "move"
  }, [])

  const handleMouseDown = (e: React.MouseEvent, nodeId: string) => {
    e.stopPropagation()

    if (e.shiftKey) {
      // Shift+click to start connection
      if (!isConnecting) {
        setIsConnecting(true)
        setConnectionStart(nodeId)
      } else if (connectionStart && connectionStart !== nodeId) {
        // Complete connection
        onConnect(connectionStart, nodeId)
        setIsConnecting(false)
        setConnectionStart(null)
      }
      return
    }

    // Regular drag mode
    setDraggedNode(nodeId)

    const node = nodes.find((n) => n.id === nodeId)
    if (node) {
      setDragOffset({
        x: e.clientX - node.position.x * (zoom / 100),
        y: e.clientY - node.position.y * (zoom / 100),
      })
    }

    onNodeSelect(nodeId)
  }

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!draggedNode) return

      const newPosition = {
        x: (e.clientX - dragOffset.x) / (zoom / 100),
        y: (e.clientY - dragOffset.y) / (zoom / 100),
      }

      onNodeMove(draggedNode, newPosition)
    },
    [draggedNode, dragOffset, onNodeMove, zoom],
  )

  const handleMouseUp = useCallback(() => {
    setDraggedNode(null)
  }, [])

  const handleCanvasClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onNodeSelect(null)
      if (isConnecting) {
        setIsConnecting(false)
        setConnectionStart(null)
      }
    }
  }

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape" && isConnecting) {
        setIsConnecting(false)
        setConnectionStart(null)
      }
    },
    [isConnecting],
  )

  useState(() => {
    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [handleKeyDown])

  return (
    <div
      ref={canvasRef}
      className="w-full h-full bg-gray-50 relative overflow-hidden"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onClick={handleCanvasClick}
    >
      {/* Grid Pattern */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(to right, #e5e7eb 1px, transparent 1px),
            linear-gradient(to bottom, #e5e7eb 1px, transparent 1px)
          `,
          backgroundSize: `${20 * (zoom / 100)}px ${20 * (zoom / 100)}px`,
        }}
      />

      {/* Canvas Content */}
      <div
        className="relative w-full h-full"
        style={{ transform: `scale(${zoom / 100})`, transformOrigin: "top left" }}
      >
        {/* Connections */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          {connections.map((connection) => {
            const sourceNode = nodes.find((n) => n.id === connection.source)
            const targetNode = nodes.find((n) => n.id === connection.target)

            if (!sourceNode || !targetNode) return null

            const sourceX = sourceNode.position.x + 320 // Node width
            const sourceY = sourceNode.position.y + 60 // Node height / 2
            const targetX = targetNode.position.x
            const targetY = targetNode.position.y + 60

            const midX = (sourceX + targetX) / 2
            const controlPoint1X = sourceX + (midX - sourceX) * 0.5
            const controlPoint2X = targetX - (targetX - midX) * 0.5

            return (
              <path
                key={connection.id}
                d={`M ${sourceX} ${sourceY} C ${controlPoint1X} ${sourceY}, ${controlPoint2X} ${targetY}, ${targetX} ${targetY}`}
                stroke="#6b7280"
                strokeWidth="2"
                fill="none"
                markerEnd="url(#arrowhead)"
                className="hover:stroke-blue-500 transition-colors"
              />
            )
          })}

          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#6b7280" />
            </marker>
          </defs>
        </svg>

        {/* Nodes */}
        {nodes.map((node) => (
          <div
            key={node.id}
            className="absolute"
            style={{
              left: node.position.x,
              top: node.position.y,
              zIndex: selectedNode === node.id ? 10 : 1,
            }}
            onMouseDown={(e) => handleMouseDown(e, node.id)}
          >
            <WorkflowNode
              node={node}
              isSelected={selectedNode === node.id}
              isConnecting={isConnecting && connectionStart === node.id}
              onUpdate={(data) => onNodeUpdate(node.id, data)}
            />
          </div>
        ))}

        {/* Empty State */}
        {nodes.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-4xl text-muted-foreground mb-4">+</div>
              <p className="text-lg text-muted-foreground">Drag & drop to get started</p>
              <p className="text-sm text-muted-foreground mt-2">Shift+click nodes to connect them</p>
            </div>
          </div>
        )}

        {/* Connection Instructions */}
        {isConnecting && (
          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg">
            <p className="text-sm">Click another node to connect, or press Escape to cancel</p>
          </div>
        )}
      </div>
    </div>
  )
}
