// API client for GenAI Stack backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
}

interface Workspace {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  workflow_json?: any;
  document_filename?: string;
  created_at: string;
  updated_at: string;
}

interface ChatMessage {
  id: string;
  workspace_id: string;
  user_message: string;
  ai_response: string;
  timestamp: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include', // Include cookies in requests
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Authentication
  async signup(email: string, password: string, name?: string) {
    const response = await this.request('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    });
    return response;
  }

  async login(email: string, password: string) {
    const response = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    return response;
  }

  async getCurrentUser(): Promise<User> {
    return this.request('/api/auth/me');
  }

  async logout() {
    return this.request('/api/auth/logout', {
      method: 'POST',
    });
  }

  // Workspaces
  async createWorkspace(name: string, description?: string): Promise<Workspace> {
    return this.request('/api/workspaces/create', {
      method: 'POST',
      body: JSON.stringify({ name, description }),
    });
  }

  async uploadDocument(file: File, name: string, description?: string): Promise<Workspace> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);
    if (description) {
      formData.append('description', description);
    }

    const url = `${this.baseUrl}/api/workspaces/upload-document`;

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
      credentials: 'include', // Include cookies
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getWorkspaces(): Promise<Workspace[]> {
    return this.request('/api/workspaces/');
  }

  async getWorkspace(id: string): Promise<Workspace> {
    return this.request(`/api/workspaces/${id}`);
  }

  async updateWorkflow(id: string, workflow: any): Promise<Workspace> {
    return this.request(`/api/workspaces/${id}/workflow`, {
      method: 'PUT',
      body: JSON.stringify({ workflow_json: workflow }),
    });
  }

  async getWorkspaceInfo(id: string) {
    return this.request(`/api/workspaces/${id}/info`);
  }

  // Chat
  async sendMessage(workspaceId: string, message: string): Promise<ChatMessage> {
    return this.request('/api/chat/', {
      method: 'POST',
      body: JSON.stringify({
        workspace_id: workspaceId,
        query: message,
      }),
    });
  }

  async getChatHistory(workspaceId: string): Promise<ChatMessage[]> {
    return this.request(`/api/chat/${workspaceId}/history`);
  }

  async testLLM(): Promise<any> {
    return this.request('/api/chat/test-llm', {
      method: 'POST',
    });
  }

  // Health check
  async health() {
    return this.request('/health');
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient;

// Export types
export type { User, Workspace, ChatMessage };