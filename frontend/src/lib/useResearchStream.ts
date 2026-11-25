// 基于 SSE 的研究流 hook
// 与 @langchain/langgraph-sdk 的 useStream 并存，用于异步任务场景

import { useState, useRef, useCallback } from "react";
import { syncTaskIdToUrl } from "@/lib/api";

const API_BASE_URL = "";

interface ResearchEvent {
  generate_plan?: { plan: string };
  generate_query?: { search_query: string[] };
  web_research?: { sources_gathered: any[] };
  reflection?: any;
  finalize_answer?: any;
  task_paused?: boolean;
  token?: { text: string; node: string };
  error?: string;
}

interface UseResearchStreamReturn {
  events: ResearchEvent[];
  messages: any[];
  isLoading: boolean;
  /** 是否已收到 finalize_answer 终稿（勿用文本长度判断，plan 也会很长） */
  hasFinalReport: boolean;
  /** 当前正在流式输出的节点名称（null 表示非流式状态） */
  streamingNode: string | null;
  /** 当前节点已流式输出的累计文本 */
  streamingContent: string;
  /** 当前研究任务 ID（导出/恢复用） */
  taskId: string;
  submit: (input: string, effort: string, model: string, extra?: { plan?: string; planStatus?: string }) => Promise<void>;
  stop: () => void;
  /** 按 task_id 从后端快照恢复会话（刷新后可继续查看报告） */
  restore: (taskId: string) => Promise<{ status: string; error?: string }>;
  /** 追加一条本地消息（会话动作回复等） */
  appendMessage: (msg: { type: string; content: string }) => void;
  /** 清空当前会话，回到欢迎页 */
  reset: () => void;
}

export function useResearchStream(): UseResearchStreamReturn {
  const [events, setEvents] = useState<ResearchEvent[]>([]);
  const [messages, setMessages] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasFinalReport, setHasFinalReport] = useState(false);
  const [streamingNode, setStreamingNode] = useState<string | null>(null);
  const [streamingContent, setStreamingContent] = useState("");
  const [taskId, setTaskId] = useState("");
  const eventSourceRef = useRef<EventSource | null>(null);
  const messageIdCounter = useRef(0);
  const planRef = useRef("");  // 缓存 generate_plan 中的计划内容
  const taskIdRef = useRef<string>("");  // 保存首次任务响应的 task_id，后续提交复用
  const messagesRef = useRef<any[]>([]);
  const lastEventIdRef = useRef<string>("0");
  const hasFinalReportRef = useRef(false);

  // 流式状态 refs（避免闭包过期问题）
  const streamingNodeRef = useRef<string | null>(null);
  const streamingContentRef = useRef("");

  /** 重置流式状态 */
  const _resetStreaming = useCallback(() => {
    streamingNodeRef.current = null;
    streamingContentRef.current = "";
    setStreamingNode(null);
    setStreamingContent("");
  }, []);

  const stop = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
    setIsLoading(false);
    _resetStreaming();
  }, [_resetStreaming]);

  const reset = useCallback(() => {
    stop();
    setEvents([]);
    setMessages([]);
    messagesRef.current = [];
    setTaskId("");
    taskIdRef.current = "";
    planRef.current = "";
    lastEventIdRef.current = "0";
    hasFinalReportRef.current = false;
    setHasFinalReport(false);
    messageIdCounter.current = 0;
    syncTaskIdToUrl(null);
  }, [stop]);

  const submit = useCallback(
    async (input: string, effort: string, model: string, extra?: { plan?: string; planStatus?: string }) => {
      if (!input.trim()) return;

      // 停止之前的连接
      stop();

      setIsLoading(true);
      setEvents([]);
      planRef.current = "";
      _resetStreaming();

      const currentMessages = messagesRef.current;
      // 首次提交时清空 taskIdRef，让后端生成新 task_id
      const isFirstSubmit = currentMessages.length === 0;
      if (isFirstSubmit) {
        taskIdRef.current = "";
        lastEventIdRef.current = "0";
        hasFinalReportRef.current = false;
        setHasFinalReport(false);
      }

      const humanMsg = {
        type: "human",
        content: input,
        id: String(++messageIdCounter.current),
      };
      const nextMessages = [...currentMessages, humanMsg];
      messagesRef.current = nextMessages;
      setMessages(nextMessages);

      let initial_search_query_count: number;
      let max_research_loops: number;
      switch (effort) {
        case "low":
          initial_search_query_count = 1;
          max_research_loops = 1;
          break;
        case "medium":
        default:
          initial_search_query_count = 3;
          max_research_loops = 3;
          break;
        case "high":
          initial_search_query_count = 5;
          max_research_loops = 10;
          break;
      }

      try {
        // 构建请求体（包含完整对话历史和 plan 状态）
        const body: any = {
          messages: nextMessages,
          initial_search_query_count,
          max_research_loops,
          reasoning_model: model,
        };
        if (extra?.plan) {
          body.plan = extra.plan;
          body.plan_status = extra.planStatus || "confirmed";
        }
        // 后续提交回传同一个 task_id，使后端复用 LangGraph checkpoint
        if (taskIdRef.current) {
          body.task_id = taskIdRef.current;
        }

        // 1. 提交任务，立即拿到 task_id
        const res = await fetch(`${API_BASE_URL}/api/research`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(body),
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.error || `HTTP ${res.status}`);
        }

        const { stream_url, task_id } = await res.json();

        // 保存 task_id 供后续提交复用，并同步到 URL（刷新可恢复）
        if (task_id) {
          taskIdRef.current = task_id;
          setTaskId(task_id);
          syncTaskIdToUrl(task_id);
        }

        // 复用 task_id 时后端会清空旧事件流；新连接应从 0 读本轮事件
        const isResume = Boolean(body.task_id);
        if (isResume) {
          lastEventIdRef.current = "0";
        }

        // 2. 建立 SSE 连接接收事件（带 after 以支持断线后续读）
        const after = lastEventIdRef.current && lastEventIdRef.current !== "0"
          ? `?after=${encodeURIComponent(lastEventIdRef.current)}`
          : "";
        const es = new EventSource(`${API_BASE_URL}${stream_url}${after}`);
        eventSourceRef.current = es;

        es.onmessage = (e) => {
          try {
            if (e.lastEventId) {
              lastEventIdRef.current = e.lastEventId;
            }
            const raw = JSON.parse(e.data);

            // ── 处理 token 流式事件 ──────────────────────────
            if (raw.token) {
              const { text, node } = raw.token as { text: string; node: string };
              if (node !== streamingNodeRef.current) {
                // 新节点开始流式
                streamingNodeRef.current = node;
                streamingContentRef.current = text;
                setStreamingNode(node);
                setStreamingContent(text);
              } else {
                // 同一节点继续追加
                streamingContentRef.current += text;
                setStreamingContent(prev => prev + text);
              }
              return; // token 事件不需要进一步处理
            }

            const event: ResearchEvent = raw;

            if (event.error) {
              setIsLoading(false);
              setEvents(prev => [...prev, event]);
              _resetStreaming();
              es.close();
              return;
            }

            setEvents(prev => [...prev, event]);

            // 节点完成事件到达 → 清空对应节点的流式 buffer
            if (event.generate_plan) {
              planRef.current = event.generate_plan.plan || "";
              if (streamingNodeRef.current === "generate_plan") {
                _resetStreaming();
              }
            }

            // finalize_answer 时结束
            if (event.finalize_answer) {
              setIsLoading(false);
              hasFinalReportRef.current = true;
              setHasFinalReport(true);
              // 使用后端 Post.extract_pattern 清洗后的内容（不含 markdown fence）
              const finalContent = (event.finalize_answer as any)?.messages?.[0]?.content || "";
              setMessages(prev => {
                const next = [
                  ...prev,
                  {
                    type: "ai",
                    content: finalContent,
                    id: String(++messageIdCounter.current),
                  },
                ];
                messagesRef.current = next;
                return next;
              });
              _resetStreaming();
              es.close();
            }

            // task_paused 时结束（等待 Plan 确认，后续继续用本 hook 提交确认）
            if (event.task_paused) {
              setIsLoading(false);
              _resetStreaming();
              // 从缓存的 generate_plan 事件中获取计划内容；已展示过则不重复追加
              const planContent = planRef.current;
              if (planContent) {
                setMessages(prev => {
                  const lastAi = [...prev].reverse().find((m) => m.type === "ai");
                  if (lastAi && lastAi.content === planContent) {
                    messagesRef.current = prev;
                    return prev;
                  }
                  const next = [
                    ...prev,
                    {
                      type: "ai",
                      content: planContent,
                      id: String(++messageIdCounter.current),
                    },
                  ];
                  messagesRef.current = next;
                  return next;
                });
              }
              es.close();
            }
          } catch {
            // 忽略解析错误
          }
        };

        es.onerror = () => {
          setIsLoading(false);
          _resetStreaming();
          es.close();
        };
      } catch (err: any) {
        setIsLoading(false);
        _resetStreaming();
        setEvents(prev => [
          ...prev,
          { error: err.message || "提交失败" } as ResearchEvent,
        ]);
      }
    },
    [_resetStreaming, stop]
  );

  const restore = useCallback(async (restoreTaskId: string) => {
    if (!restoreTaskId.trim()) {
      return { status: "error", error: "缺少 task_id" };
    }
    stop();
    setIsLoading(true);
    setEvents([]);
    _resetStreaming();
    try {
      const res = await fetch(
        `${API_BASE_URL}/api/research/${encodeURIComponent(restoreTaskId)}/snapshot`,
        { credentials: "include" },
      );
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || `HTTP ${res.status}`);
      }
      if (data.status === "not_found") {
        setIsLoading(false);
        return { status: "not_found", error: data.error || "任务不存在" };
      }
      taskIdRef.current = restoreTaskId;
      setTaskId(restoreTaskId);
      syncTaskIdToUrl(restoreTaskId);
      lastEventIdRef.current = "0";
      const restoredMessages = Array.isArray(data.messages) ? data.messages : [];
      messagesRef.current = restoredMessages;
      setMessages(restoredMessages);
      messageIdCounter.current = restoredMessages.length;
      const restoredHasFinal = Boolean(data.has_final) || data.status === "completed";
      hasFinalReportRef.current = restoredHasFinal;
      setHasFinalReport(restoredHasFinal);
      if (data.error) {
        setEvents([{ error: String(data.error) }]);
      }
      setIsLoading(false);
      return { status: data.status || "ok", error: data.error };
    } catch (err: any) {
      setIsLoading(false);
      const msg = err?.message || "恢复失败";
      setEvents([{ error: msg }]);
      return { status: "error", error: msg };
    }
  }, [_resetStreaming, stop]);

  const appendMessage = useCallback((msg: { type: string; content: string }) => {
    setMessages((prev) => {
      const next = [
        ...prev,
        {
          type: msg.type,
          content: msg.content,
          id: String(++messageIdCounter.current),
        },
      ];
      messagesRef.current = next;
      return next;
    });
  }, []);

  return {
    events,
    messages,
    isLoading,
    hasFinalReport,
    streamingNode,
    streamingContent,
    taskId,
    submit,
    stop,
    restore,
    appendMessage,
    reset,
  };
}
