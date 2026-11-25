// API配置 - 使用相对路径，通过 Vite 代理转发到后端
// 开发模式走 Vite proxy (/api → localhost:2024)
// 生产模式由 LangGraph runtime 直接服务
export const API_BASE_URL = "";

// 模型配置接口
export interface ModelConfig {
  model_id: string;
  display_name: string;
  icon: string;
  icon_color: string;
}

/** 历史会话列表项 */
export interface ThreadSummary {
  thread_id: string;
  title: string;
  status: string;
  created_at: string | null;
  updated_at: string | null;
  has_report: boolean;
}

/** 会话动作响应 */
export interface SessionActResult {
  ok?: boolean;
  intent?: string;
  reply?: string;
  action?: string;
  delegate?: string;
  error?: string;
  tool_result?: Record<string, unknown>;
}

// 获取可用模型列表
export async function fetchAvailableModels(): Promise<ModelConfig[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models`, {
      credentials: "include",
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.models || [];
  } catch (error) {
    console.error("获取模型列表失败:", error);
    return [
      { model_id: "deepseek-flash", display_name: "DeepSeek-Flash", icon: "Zap", icon_color: "blue-400" },
      { model_id: "deepseek-v4-pro", display_name: "DeepSeek-V4-Pro", icon: "Cpu", icon_color: "purple-400" },
    ];
  }
}

/** 拉取当前用户历史会话列表 */
export async function fetchThreads(limit = 50): Promise<ThreadSummary[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/threads?limit=${limit}`,
    { credentials: "include" },
  );
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }
  return Array.isArray(data.threads) ? data.threads : [];
}

/** 删除一条历史会话索引 */
export async function deleteThread(threadId: string): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/threads/${encodeURIComponent(threadId)}`,
    { method: "DELETE", credentials: "include" },
  );
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }
}

/** 研究完成后的会话动作（导出 / 查看 / 问答） */
export async function sessionAct(params: {
  message: string;
  taskId: string;
  reasoningModel?: string;
}): Promise<SessionActResult> {
  const response = await fetch(`${API_BASE_URL}/api/session/act`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      message: params.message,
      task_id: params.taskId,
      reasoning_model: params.reasoningModel || "",
    }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }
  return data;
}

/** 将当前浏览器 URL 同步为 ?task_id=（不产生历史栈噪音） */
export function syncTaskIdToUrl(taskId: string | null) {
  const url = new URL(window.location.href);
  if (taskId) {
    url.searchParams.set("task_id", taskId);
  } else {
    url.searchParams.delete("task_id");
  }
  window.history.replaceState({}, "", url.pathname + url.search);
}
