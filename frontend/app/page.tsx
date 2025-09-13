"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Plus, Bot, Edit3, MessageSquare, LogOut, User, Upload, FileText } from "lucide-react"
import Link from "next/link"
import { ProtectedRoute } from "@/components/ProtectedRoute"
import { useAuth } from "@/contexts/AuthContext"
import { apiClient, type Workspace } from "@/lib/api"

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false)
  const [newWorkspaceName, setNewWorkspaceName] = useState("")
  const [newWorkspaceDescription, setNewWorkspaceDescription] = useState("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadWorkspaceName, setUploadWorkspaceName] = useState("")
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    loadWorkspaces()
  }, [])

  const loadWorkspaces = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getWorkspaces()
      setWorkspaces(response)
    } catch (error) {
      console.error('Failed to load workspaces:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateWorkspace = async () => {
    if (!newWorkspaceName.trim()) return
    
    try {
      setCreating(true)
      await apiClient.createWorkspace(
        newWorkspaceName.trim(),
        newWorkspaceDescription.trim()
      )
      
      // Reset form and close modal
      setNewWorkspaceName("")
      setNewWorkspaceDescription("")
      setIsCreateModalOpen(false)
      
      // Reload workspaces
      await loadWorkspaces()
    } catch (error) {
      console.error('Failed to create workspace:', error)
      alert('Failed to create workspace. Please try again.')
    } finally {
      setCreating(false)
    }
  }

  const handleFileUpload = async () => {
    if (!selectedFile) return
    
    try {
      setUploading(true)
      
      await apiClient.uploadDocument(selectedFile)
      
      // Reset form and close modal
      setSelectedFile(null)
      setUploadWorkspaceName("")
      setIsUploadModalOpen(false)
      
      // Reload workspaces
      await loadWorkspaces()
    } catch (error) {
      console.error('Failed to upload file:', error)
      alert('Failed to upload file. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <Bot className="h-8 w-8 text-purple-600" />
                <h1 className="ml-2 text-xl font-bold text-gray-900">GenAI Stack</h1>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center text-sm text-gray-600">
                  <User className="h-4 w-4 mr-1" />
                  {user?.email || user?.name}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLogout}
                  className="flex items-center"
                >
                  <LogOut className="h-4 w-4 mr-1" />
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome to your AI Workspace
            </h2>
            <p className="text-gray-600">
              Create workspaces, upload documents, and chat with your AI assistant
            </p>
          </div>

          {/* Action Buttons */}
          <div className="mb-8 flex flex-wrap gap-4">
            <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
              <DialogTrigger asChild>
                <Button className="flex items-center bg-purple-600 hover:bg-purple-700">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Workspace
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New Workspace</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="workspace-name">Workspace Name</Label>
                    <Input
                      id="workspace-name"
                      value={newWorkspaceName}
                      onChange={(e) => setNewWorkspaceName(e.target.value)}
                      placeholder="Enter workspace name"
                      disabled={creating}
                    />
                  </div>
                  <div>
                    <Label htmlFor="workspace-description">Description (Optional)</Label>
                    <Textarea
                      id="workspace-description"
                      value={newWorkspaceDescription}
                      onChange={(e) => setNewWorkspaceDescription(e.target.value)}
                      placeholder="Enter workspace description"
                      disabled={creating}
                    />
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button
                      variant="outline"
                      onClick={() => setIsCreateModalOpen(false)}
                      disabled={creating}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleCreateWorkspace}
                      disabled={creating || !newWorkspaceName.trim()}
                    >
                      {creating ? "Creating..." : "Create"}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>

            <Dialog open={isUploadModalOpen} onOpenChange={setIsUploadModalOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" className="flex items-center">
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Document
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Upload Document</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="file-upload">Select PDF File</Label>
                    <Input
                      id="file-upload"
                      type="file"
                      accept=".pdf"
                      onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                      disabled={uploading}
                    />
                    <p className="text-sm text-gray-500 mt-1">
                      Upload a PDF document to create a new workspace
                    </p>
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button
                      variant="outline"
                      onClick={() => setIsUploadModalOpen(false)}
                      disabled={uploading}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleFileUpload}
                      disabled={uploading || !selectedFile}
                    >
                      {uploading ? "Uploading..." : "Upload"}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          {/* Workspaces Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {loading ? (
              // Loading skeleton
              Array.from({ length: 6 }).map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardHeader>
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </CardHeader>
                  <CardContent>
                    <div className="h-20 bg-gray-200 rounded"></div>
                  </CardContent>
                </Card>
              ))
            ) : workspaces.length === 0 ? (
              <div className="col-span-full text-center py-12">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No workspaces yet</h3>
                <p className="text-gray-600 mb-4">
                  Create your first workspace or upload a document to get started
                </p>
              </div>
            ) : (
              workspaces.map((workspace) => (
                <Card key={workspace.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="truncate">{workspace.name}</span>
                      <Bot className="h-5 w-5 text-purple-600" />
                    </CardTitle>
                    <CardDescription className="text-sm text-gray-600">
                      {workspace.description || "No description"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="text-xs text-gray-500">
                        Created: {new Date(workspace.created_at).toLocaleDateString()}
                      </div>
                      <div className="flex space-x-2">
                        <Link href={`/chat/${workspace.id}`} className="flex-1">
                          <Button className="w-full bg-purple-600 hover:bg-purple-700">
                            <MessageSquare className="h-4 w-4 mr-2" />
                            Chat
                          </Button>
                        </Link>
                        <Link href={`/builder/${workspace.id}`}>
                          <Button variant="outline" size="sm">
                            <Edit3 className="h-4 w-4" />
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}