"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Plus, Bot, Edit3, MessageSquare } from "lucide-react"
import Link from "next/link"

interface Stack {
  id: string
  name: string
  description: string
}

export default function Dashboard() {
  const [stacks, setStacks] = useState<Stack[]>([
    {
      id: "1",
      name: "Chat With AI",
      description: "Chat with a smart AI",
    },
    {
      id: "2",
      name: "Content Writer",
      description: "Helps you write content",
    },
    {
      id: "3",
      name: "Content Summarizer",
      description: "Helps you summarize content",
    },
    {
      id: "4",
      name: "Information Finder",
      description: "Helps you find relevant information",
    },
  ])

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [newStackName, setNewStackName] = useState("")
  const [newStackDescription, setNewStackDescription] = useState("")

  const handleCreateStack = () => {
    if (newStackName.trim()) {
      const newStack: Stack = {
        id: Date.now().toString(),
        name: newStackName,
        description: newStackDescription,
      }
      setStacks([...stacks, newStack])
      setNewStackName("")
      setNewStackDescription("")
      setIsCreateModalOpen(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-8 h-8 bg-blue-600 rounded-lg">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-semibold text-foreground">GenAI Stack</h1>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center w-8 h-8 bg-muted rounded-full">
                <span className="text-sm font-medium">S</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-semibold text-foreground">My Stacks</h2>
          <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
            <DialogTrigger asChild>
              <Button className="bg-green-600 hover:bg-green-700 text-white">
                <Plus className="w-4 h-4 mr-2" />
                New Stack
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Create New Stack</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={newStackName}
                    onChange={(e) => setNewStackName(e.target.value)}
                    placeholder="Enter stack name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={newStackDescription}
                    onChange={(e) => setNewStackDescription(e.target.value)}
                    placeholder="Enter stack description"
                    rows={3}
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setIsCreateModalOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateStack} className="bg-green-600 hover:bg-green-700 text-white">
                  Create
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Empty State */}
        {stacks.length === 0 && (
          <div className="text-center py-12">
            <div className="mb-6">
              <div className="flex items-center justify-center w-16 h-16 bg-muted rounded-full mx-auto mb-4">
                <Bot className="w-8 h-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-medium text-foreground mb-2">Create New Stack</h3>
              <p className="text-muted-foreground max-w-md mx-auto">
                Start building your generative AI apps with our essential tools and frameworks
              </p>
            </div>
            <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
              <DialogTrigger asChild>
                <Button size="lg" className="bg-green-600 hover:bg-green-700 text-white">
                  <Plus className="w-4 h-4 mr-2" />
                  New Stack
                </Button>
              </DialogTrigger>
            </Dialog>
          </div>
        )}

        {/* Stacks Grid */}
        {stacks.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {stacks.map((stack) => (
              <Card key={stack.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <CardTitle className="text-lg">{stack.name}</CardTitle>
                  <CardDescription>{stack.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-2">
                    <Link href={`/builder/${stack.id}`} className="flex-1">
                      <Button variant="outline" className="w-full bg-transparent">
                        <Edit3 className="w-4 h-4 mr-2" />
                        Edit Stack
                      </Button>
                    </Link>
                    <Link href={`/chat/${stack.id}`}>
                      <Button size="icon" variant="outline">
                        <MessageSquare className="w-4 h-4" />
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))}

            {/* Add New Stack Card */}
            <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
              <DialogTrigger asChild>
                <Card className="border-dashed border-2 hover:border-green-600 transition-colors cursor-pointer">
                  <CardContent className="flex flex-col items-center justify-center py-12">
                    <Plus className="w-8 h-8 text-muted-foreground mb-2" />
                    <span className="text-sm font-medium text-muted-foreground">New Stack</span>
                  </CardContent>
                </Card>
              </DialogTrigger>
            </Dialog>
          </div>
        )}
      </main>
    </div>
  )
}
