import { useStream } from "@langchain/langgraph-sdk/react";
import { useResearchStream } from "@/lib/useResearchStream";
import type { Message } from "@langchain/langgraph-sdk";
import { useState, useEffect, useRef, useCallback } from "react";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { ChatMessagesView } from "@/components/ChatMessagesView";
import { ResearchStreamChatView } from "@/components/ResearchStreamChatView";
import { SessionSidebar } from "@/components/SessionSidebar";
import { Button } from "@/components/ui/button";
import { sessionAct } from "@/lib/api";

export default function App() {
  const [processedEventsTimeline, setProcessedEventsTimeline] = useState<
    ProcessedEvent[]
  >([]);
  const [historicalActivities, setHistoricalActivities] = useState<
    Record<string, ProcessedEvent[]>
  >({});
  const [awaitingPlanConfirmation, setAwaitingPlanConfirmation] = useState("unconfirmed");
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const hasFinalizeEventOccurredRef = useRef(false);
  const [error, setError] = useState<string | null>(null);
  const [savedEffort, setSavedEffort] = useState("medium");
  const [savedModel, setSavedModel] = useState("deepseek-flash");
  const [sessionActing, setSessionActing] = useState(false);
  const [sidebarRefreshKey, setSidebarRefreshKey] = useState(0);
  const thread = useStream<{
    messages: Message[];
    initial_search_query_count: number;
    max_research_loops: number;
    reasoning_model: string;
    plan_status: string;
  }>({
    apiUrl: "",
    assistantId: "agent",
    messagesKey: "messages",
    onUpdateEvent: (event: any) => {
      let processedEvent: ProcessedEvent | null = null;
      if (event.generate_plan){
        processedEvent = {
          title: "生成计划",
          data: event.generate_plan?.plan || "No Plan to generate"
        }
        setAwaitingPlanConfirmation("unconfirmed");
        hasFinalizeEventOccurredRef.current = true;
      }
      else if (event.generate_query) {
        processedEvent = {
          title: "生成搜索查询",
          data: event.generate_query?.search_query?.join(", ") || "",
        };
      } else if (event.web_research) {
        const sources = event.web_research.sources_gathered || [];
        const numSources = sources.length;
        const uniqueLabels = [
          ...new Set(sources.map((s: any) => s.label).filter(Boolean)),
        ];
        const exampleLabels = uniqueLabels.slice(0, 3).join(", ");
        processedEvent = {
          title: "网络研究",
          data: `Gathered ${numSources} sources. Related to: ${
            exampleLabels || "N/A"
          }.`,
        };
      } else if (event.reflection) {
        processedEvent = {
          title: "反思和分析",
          data: "Analysing Web Research Results",
        };
      } else if (event.finalize_answer) {
        processedEvent = {
          title: "最终确定答案",
          data: "Composing and presenting the final answer.",
        };
        hasFinalizeEventOccurredRef.current = true;
      }
      if (processedEvent) {
        setProcessedEventsTimeline((prevEvents) => [
          ...prevEvents,
          processedEvent!,
        ]);
      }
    },
    onError: (error: any) => {
      setError(error.message);
    },
  });

  // 异步任务通道（首次提交走此通道，Plan 确认后切回 useStream）
  const researchStream = useResearchStream();

  // 支持 ?task_id=xxx 刷新后恢复研究报告展示
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const taskId = params.get("task_id");
    if (!taskId) return;
    researchStream.restore(taskId).then((result) => {
      if (result.status === "failed" || result.status === "error" || result.status === "not_found") {
        setError(result.error || "恢复会话失败");
      }
    });
    // 仅在挂载时按 URL 恢复一次
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 任务 ID 变化时刷新侧边栏（新研究入库）
  useEffect(() => {
    if (researchStream.taskId) {
      setSidebarRefreshKey((k) => k + 1);
    }
  }, [researchStream.taskId]);

  // 研究结束（有终稿）后再刷一次，同步 status/title
  useEffect(() => {
    if (!researchStream.isLoading && researchStream.taskId && researchStream.hasFinalReport) {
      setSidebarRefreshKey((k) => k + 1);
    }
  }, [researchStream.isLoading, researchStream.taskId, researchStream.hasFinalReport]);

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [thread.messages, researchStream.messages]);

  useEffect(() => {
    if (
      hasFinalizeEventOccurredRef.current &&
      !thread.isLoading &&
      thread.messages.length > 0
    ) {
      const lastMessage = thread.messages[thread.messages.length - 1];
      if (lastMessage && lastMessage.type === "ai" && lastMessage.id) {
        setHistoricalActivities((prev) => ({
          ...prev,
          [lastMessage.id!]: [...processedEventsTimeline],
        }));
      }
      hasFinalizeEventOccurredRef.current = false;
    }
  }, [thread.messages, thread.isLoading, processedEventsTimeline]);

  // 将异步通道的事件汇入 ActivityTimeline（只处理新增事件，避免重复追加）
  const processedEventCountRef = useRef(0);
  useEffect(() => {
    const events = researchStream.events;
    if (events.length < processedEventCountRef.current) {
      // submit 清空了 events，重置游标
      processedEventCountRef.current = 0;
    }
    const fresh = events.slice(processedEventCountRef.current);
    processedEventCountRef.current = events.length;
    for (const event of fresh) {
      let processedEvent: ProcessedEvent | null = null;
      if (event.generate_plan) {
        processedEvent = {
          title: "生成计划",
          data: event.generate_plan.plan || "No Plan to generate",
        };
        setAwaitingPlanConfirmation("unconfirmed");
      } else if (event.generate_query) {
        processedEvent = {
          title: "生成搜索查询",
          data: (event.generate_query as any)?.search_query?.join(", ") || "",
        };
      } else if (event.web_research) {
        const sources = (event.web_research as any)?.sources_gathered || [];
        const uniqueLabels = [
          ...new Set(sources.map((s: any) => s.label).filter(Boolean)),
        ];
        processedEvent = {
          title: "网络研究",
          data: `Gathered ${sources.length} sources. Related to: ${uniqueLabels.slice(0, 3).join(", ") || "N/A"}.`,
        };
      } else if (event.reflection) {
        processedEvent = {
          title: "反思和分析",
          data: "Analysing Web Research Results",
        };
      } else if (event.finalize_answer) {
        processedEvent = {
          title: "最终确定答案",
          data: "Composing and presenting the final answer.",
        };
        hasFinalizeEventOccurredRef.current = true;
        setAwaitingPlanConfirmation("confirmed");
      }
      if (processedEvent) {
        setProcessedEventsTimeline(prev => [...prev, processedEvent]);
      }
    }
  }, [researchStream.events]);

  const handleNewSession = useCallback(() => {
    researchStream.reset();
    setProcessedEventsTimeline([]);
    setHistoricalActivities({});
    setError(null);
    setAwaitingPlanConfirmation("unconfirmed");
    hasFinalizeEventOccurredRef.current = false;
  }, [researchStream]);

  const handleSelectSession = useCallback(
    async (threadId: string) => {
      if (threadId === researchStream.taskId) return;
      setError(null);
      setProcessedEventsTimeline([]);
      setHistoricalActivities({});
      const result = await researchStream.restore(threadId);
      if (result.status === "failed" || result.status === "error" || result.status === "not_found") {
        setError(result.error || "恢复会话失败");
      }
    },
    [researchStream]
  );

  const handleSubmit = useCallback(
    async (submittedInputValue: string, effort: string, model: string) => {
      console.log('handleSubmit exectued.....', submittedInputValue, effort, model);
      if (!submittedInputValue.trim()) return;
      // 研究进行中禁止重复提交，避免同 task 二次入队冲掉正在推送的 SSE
      if (researchStream.isLoading || sessionActing || thread.isLoading) return;
      setProcessedEventsTimeline([]);
      hasFinalizeEventOccurredRef.current = false;
      setError(null);

      // 保存 effort/model 以备后续使用
      if (effort) setSavedEffort(effort);
      if (model) setSavedModel(model);

      // 场景 1: 首次提交 → 走 task queue / SSE 通道
      if (thread.messages.length === 0 && researchStream.messages.length === 0) {
        researchStream.submit(submittedInputValue, effort, model);
        return;
      }

      // 场景 1.5: 已有终稿时，先走会话动作（导出 / 查看 / 报告问答）
      // 注意：plan 文本通常也 >800 字，不能用长度误判为报告
      const taskId =
        researchStream.taskId ||
        new URLSearchParams(window.location.search).get("task_id") ||
        "";
      if (researchStream.hasFinalReport && taskId) {
        setSessionActing(true);
        try {
          const data = await sessionAct({
            message: submittedInputValue,
            taskId,
            reasoningModel: model || savedModel,
          });
          if (data.delegate === "research") {
            // 意图是继续研究：交给后续 researchStream 流程（下方场景 3）
            setSessionActing(false);
          } else {
            // 导出 / 查看 / 报告问答：本地追加对话，不触发新研究任务
            researchStream.appendMessage({ type: "human", content: submittedInputValue });
            researchStream.appendMessage({
              type: "ai",
              content: data.reply || "已处理。",
            });
            if (data.action === "scroll_to_report") {
              requestAnimationFrame(() => {
                document
                  .querySelector("[data-report-anchor='true']")
                  ?.scrollIntoView({ behavior: "smooth", block: "start" });
              });
            }
            setSidebarRefreshKey((k) => k + 1);
            setSessionActing(false);
            return;
          }
        } catch (err: any) {
          researchStream.appendMessage({ type: "human", content: submittedInputValue });
          researchStream.appendMessage({
            type: "ai",
            content: `会话动作失败：${err?.message || err}`,
          });
          setSessionActing(false);
          return;
        }
      }

      // 场景 2: Plan 确认（用户点击"需求确认"或输入"需求确认"）→ 传递 "confirmed" 让后端进入研究
      if (researchStream.messages.length > 0
          && (submittedInputValue.includes("需求确认") || submittedInputValue.includes("开始研究"))
          && researchStream.messages.some(m => m.type === "ai")) {
        const lastAiMsg = [...researchStream.messages].reverse().find(m => m.type === "ai");
        const planContent = lastAiMsg?.content || "";
        researchStream.submit(submittedInputValue, savedEffort, savedModel, {
          plan: planContent,
          planStatus: "confirmed",
        });
        return;
      }

      // 场景 3: 后续追问/需求补充 → 传递已有 plan + confirmed，跳过 generate_plan，进入 confirm_plan 评估
      if (researchStream.messages.length > 0) {
        const lastAiMsg = [...researchStream.messages].reverse().find(m => m.type === "ai");
        const planContent = lastAiMsg?.content || "";
        researchStream.submit(submittedInputValue, savedEffort, savedModel, {
          plan: planContent,
          planStatus: "confirmed",
        });
        return;
      }

      // 场景 4: thread 通道的后续对话（已废弃，保留作为 fallback）
      let initial_search_query_count = 0;
      let max_research_loops = 0;
      switch (savedEffort) {
        case "low":
          initial_search_query_count = 1;
          max_research_loops = 1;
          break;
        case "medium":
          initial_search_query_count = 3;
          max_research_loops = 3;
          break;
        case "high":
          initial_search_query_count = 5;
          max_research_loops = 10;
          break;
      }

      const newMessages: Message[] = [
        ...(thread.messages || []),
        {
          type: "human",
          content: submittedInputValue,
          id: Date.now().toString(),
        },
      ];
      console.log('handleSubmit submit:', newMessages);
      thread.submit({
        messages: newMessages,
        initial_search_query_count: initial_search_query_count,
        max_research_loops: max_research_loops,
        reasoning_model: savedModel,
        plan_status: awaitingPlanConfirmation,
      } as any);
    },
    [thread, researchStream, savedEffort, savedModel, awaitingPlanConfirmation]
  );

  const handleCancel = useCallback(() => {
    thread.stop();
    window.location.reload();
  }, [thread]);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-neutral-900 text-neutral-100 font-sans antialiased">
      <SessionSidebar
        activeThreadId={researchStream.taskId}
        onSelect={handleSelectSession}
        onNewSession={handleNewSession}
        refreshKey={sidebarRefreshKey}
      />
      <main className="h-full flex-1 min-w-0 overflow-hidden bg-neutral-800">
        <div className="h-full w-full max-w-4xl mx-auto">
          {thread.messages.length === 0 && researchStream.messages.length === 0 ? (
            <WelcomeScreen
              handleSubmit={handleSubmit}
              isLoading={thread.isLoading}
              onCancel={handleCancel}
            />
          ) : thread.messages.length > 0 ? (
            error ? (
              <div className="flex flex-col items-center justify-center h-full">
                <div className="flex flex-col items-center justify-center gap-4">
                  <h1 className="text-2xl text-red-400 font-bold">错误：</h1>
                  <p className="text-red-400">{JSON.stringify(error)}</p>
                  <Button
                    variant="destructive"
                    onClick={() => window.location.reload()}
                  >
                    重试，或请联系你的系统管理员
                  </Button>
                </div>
              </div>
            ) : (
              <ChatMessagesView
                messages={thread.messages}
                isLoading={thread.isLoading}
                scrollAreaRef={scrollAreaRef}
                onSubmit={handleSubmit}
                onCancel={handleCancel}
                liveActivityEvents={processedEventsTimeline}
                historicalActivities={historicalActivities}
              />
            )
          ) : (
            // researchStream 通道显示（首次 plan 生成 + plan 确认后的后续流程）
            <ResearchStreamChatView
              messages={researchStream.messages}
              isLoading={researchStream.isLoading || sessionActing}
              hasFinalReport={researchStream.hasFinalReport}
              liveActivityEvents={processedEventsTimeline}
              streamingNode={researchStream.streamingNode}
              streamingContent={researchStream.streamingContent}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              onNewTopic={handleNewSession}
              scrollAreaRef={scrollAreaRef}
            />
          )}
          {error && (
            <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50 max-w-md px-4 py-2 rounded-lg bg-red-900/90 text-red-100 text-sm shadow-lg">
              {error}
              <button
                type="button"
                className="ml-3 underline text-red-200"
                onClick={() => setError(null)}
              >
                关闭
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
