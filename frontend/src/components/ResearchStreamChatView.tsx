// ResearchStreamChatView — 显示 useResearchStream 通道的消息流
// 用于首次 plan 生成 + plan 确认后的研究流程（与 LangGraph SDK 通道共存）

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Copy, CopyCheck, Download } from "lucide-react";
import { InputForm } from "@/components/InputForm";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import {
  ActivityTimeline,
  ProcessedEvent,
} from "@/components/ActivityTimeline";

type MdComponentProps = {
  className?: string;
  children?: React.ReactNode;
  href?: string;
  [key: string]: any;
};

/** 规范化 Markdown 正文：修复字面量 \\n、保证可渲染换行 */
export function normalizeMarkdown(text: string): string {
  if (!text) return "";
  let s = text;
  // 整段被写成字面量 \n 时还原
  if (s.includes("\\n") && (s.match(/\n/g) || []).length < 3) {
    s = s.replace(/\\n/g, "\n").replace(/\\t/g, "\t");
  }
  return s;
}

const mdComponents = {
  h1: ({ className, children, ...props }: MdComponentProps) => (
    <h1 className={cn("text-2xl font-bold mt-6 mb-3 text-neutral-50", className)} {...props}>
      {children}
    </h1>
  ),
  h2: ({ className, children, ...props }: MdComponentProps) => (
    <h2 className={cn("text-xl font-bold mt-5 mb-2 text-neutral-50", className)} {...props}>
      {children}
    </h2>
  ),
  h3: ({ className, children, ...props }: MdComponentProps) => (
    <h3 className={cn("text-lg font-semibold mt-4 mb-2 text-neutral-100", className)} {...props}>
      {children}
    </h3>
  ),
  p: ({ className, children, ...props }: MdComponentProps) => (
    <p className={cn("mb-3 leading-7 text-neutral-200 whitespace-pre-wrap", className)} {...props}>
      {children}
    </p>
  ),
  a: ({ className, children, href, ...props }: MdComponentProps) => (
    <Badge className="text-xs mx-0.5 align-middle">
      <a
        className={cn("text-blue-400 hover:text-blue-300 text-xs", className)}
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        {...props}
      >
        {children}
      </a>
    </Badge>
  ),
  ul: ({ className, children, ...props }: MdComponentProps) => (
    <ul className={cn("list-disc pl-6 mb-3 space-y-1 text-neutral-200", className)} {...props}>
      {children}
    </ul>
  ),
  ol: ({ className, children, ...props }: MdComponentProps) => (
    <ol className={cn("list-decimal pl-6 mb-3 space-y-1 text-neutral-200", className)} {...props}>
      {children}
    </ol>
  ),
  li: ({ className, children, ...props }: MdComponentProps) => (
    <li className={cn("mb-1 leading-7", className)} {...props}>
      {children}
    </li>
  ),
  blockquote: ({ className, children, ...props }: MdComponentProps) => (
    <blockquote
      className={cn(
        "border-l-4 border-neutral-500 pl-4 italic my-3 text-sm text-neutral-300",
        className
      )}
      {...props}
    >
      {children}
    </blockquote>
  ),
  code: ({ className, children, ...props }: MdComponentProps) => (
    <code
      className={cn(
        "bg-neutral-900 rounded px-1 py-0.5 font-mono text-xs text-neutral-100",
        className
      )}
      {...props}
    >
      {children}
    </code>
  ),
  pre: ({ className, children, ...props }: MdComponentProps) => (
    <pre
      className={cn(
        "bg-neutral-900 p-3 rounded-lg overflow-x-auto font-mono text-xs my-3 whitespace-pre",
        className
      )}
      {...props}
    >
      {children}
    </pre>
  ),
  table: ({ className, children, ...props }: MdComponentProps) => (
    <div className="my-4 w-full overflow-x-auto rounded-lg border border-neutral-700">
      <table className={cn("w-full text-sm border-collapse", className)} {...props}>
        {children}
      </table>
    </div>
  ),
  thead: ({ className, children, ...props }: MdComponentProps) => (
    <thead className={cn("bg-neutral-900/80", className)} {...props}>
      {children}
    </thead>
  ),
  th: ({ className, children, ...props }: MdComponentProps) => (
    <th
      className={cn(
        "border border-neutral-700 px-3 py-2 text-left font-semibold text-neutral-100",
        className
      )}
      {...props}
    >
      {children}
    </th>
  ),
  td: ({ className, children, ...props }: MdComponentProps) => (
    <td
      className={cn(
        "border border-neutral-700 px-3 py-2 align-top text-neutral-200",
        className
      )}
      {...props}
    >
      {children}
    </td>
  ),
  hr: ({ className, ...props }: MdComponentProps) => (
    <hr className={cn("border-neutral-600 my-4", className)} {...props} />
  ),
};

function MessageActions({
  text,
  messageId,
  filenameHint,
}: {
  text: string;
  messageId: string;
  filenameHint?: string;
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const body = normalizeMarkdown(text);
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(body);
      } else {
        const ta = document.createElement("textarea");
        ta.value = body;
        ta.style.position = "fixed";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("复制失败: ", err);
      window.prompt("复制失败，请手动全选复制：", body.slice(0, 2000));
    }
  };

  const handleDownload = () => {
    const body = normalizeMarkdown(text);
    const blob = new Blob([body], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "");
    a.href = url;
    a.download = `${filenameHint || "research_report"}_${stamp}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (!text?.trim()) return null;

  return (
    <div className="sticky top-0 z-20 -mx-1 mb-3 flex flex-wrap items-center gap-2 rounded-lg border border-neutral-600 bg-neutral-900/95 px-3 py-2 backdrop-blur">
      <span className="mr-auto text-xs text-neutral-400">研究报告</span>
      <Button
        type="button"
        variant="default"
        size="sm"
        className="cursor-pointer bg-neutral-700 hover:bg-neutral-600 text-neutral-100"
        onClick={handleCopy}
        data-message-id={messageId}
      >
        {copied ? "已复制" : "复制全文"}
        {copied ? <CopyCheck className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
      </Button>
      <Button
        type="button"
        variant="default"
        size="sm"
        className="cursor-pointer bg-blue-700 hover:bg-blue-600 text-white"
        onClick={handleDownload}
      >
        下载 .md
        <Download className="h-4 w-4" />
      </Button>
    </div>
  );
}

interface ResearchStreamChatViewProps {
  messages: Array<{ type: string; content: string; id: string }>;
  isLoading: boolean;
  /** 是否已收到 finalize 终稿（plan 很长也不能当报告） */
  hasFinalReport?: boolean;
  liveActivityEvents: ProcessedEvent[];
  streamingNode: string | null;
  streamingContent: string;
  onSubmit: (inputValue: string, effort: string, model: string) => void;
  onCancel: () => void;
  onNewTopic?: () => void;
  scrollAreaRef: React.RefObject<HTMLDivElement | null>;
}

export function ResearchStreamChatView({
  messages,
  isLoading,
  hasFinalReport = false,
  liveActivityEvents,
  streamingNode,
  streamingContent,
  onSubmit,
  onCancel,
  onNewTopic,
  scrollAreaRef,
}: ResearchStreamChatViewProps) {
  const [researchStarted, setResearchStarted] = useState(false);
  const inputFormRef = React.useRef<any>(null);

  const handleStartResearch = () => {
    if (isLoading || hasFinalReport) return;
    if (inputFormRef.current?.setInputValue && inputFormRef.current?.submitInput) {
      inputFormRef.current.setInputValue("需求确认");
      inputFormRef.current.submitInput("需求确认");
      setResearchStarted(true);
    }
  };

  const lastAiIndex = [...messages].map((m, i) => (m.type === "ai" ? i : -1)).filter((i) => i >= 0).pop();
  // 仅终稿挂操作条；plan 文本很长也不能当成报告
  const reportMessageIndex = hasFinalReport
    ? messages.reduce((best, m, i) => {
        if (m.type !== "ai" || typeof m.content !== "string") return best;
        if (best < 0) return i;
        const bestLen = typeof messages[best].content === "string" ? messages[best].content.length : 0;
        return m.content.length >= bestLen ? i : best;
      }, -1)
    : -1;
  const hasReportInThread = hasFinalReport && reportMessageIndex >= 0;

  return (
    <div className="flex flex-col h-full">
      <ScrollArea className="flex-1 overflow-y-auto" ref={scrollAreaRef}>
        <div className="p-4 md:p-6 space-y-3 max-w-4xl mx-auto pt-8 pb-8">
          {messages.map((message, index) => {
            const content =
              typeof message.content === "string"
                ? normalizeMarkdown(message.content)
                : JSON.stringify(message.content);
            const isLongReport = message.type === "ai" && index === reportMessageIndex;
            const isShortAi = message.type === "ai" && !isLongReport;

            return (
              <div key={message.id || `msg-${index}`} className="space-y-3">
                <div
                  className={`flex items-start gap-3 ${
                    message.type === "human" ? "justify-end" : ""
                  }`}
                >
                  {message.type === "human" ? (
                    <div className="text-white break-words min-h-7 bg-neutral-700 max-w-[100%] sm:max-w-[90%] px-4 py-2.5 rounded-3xl rounded-br-lg whitespace-pre-wrap text-sm">
                      {content}
                    </div>
                  ) : (
                    <div
                      data-report-anchor={isLongReport ? "true" : undefined}
                      className={
                        isShortAi
                          ? "relative max-w-[95%] sm:max-w-[90%] break-words flex flex-col rounded-2xl rounded-bl-md bg-neutral-800/80 px-4 py-2.5"
                          : "relative w-full max-w-full break-words flex flex-col rounded-xl bg-neutral-800/60 border border-neutral-700 p-4"
                      }
                    >
                      {index === lastAiIndex && liveActivityEvents.length > 0 && (
                        <div className="mb-3 border-b border-neutral-700 pb-3 text-xs">
                          <ActivityTimeline
                            processedEvents={liveActivityEvents}
                            isLoading={isLoading}
                            title="researching"
                          />
                        </div>
                      )}
                      {isLongReport && (
                        <MessageActions
                          text={content}
                          messageId={message.id}
                          filenameHint="research_report"
                        />
                      )}
                      <div
                        className={
                          isShortAi
                            ? "markdown-body w-full max-w-none text-sm text-neutral-200 [&_p]:mb-1 [&_p]:leading-6"
                            : "markdown-body w-full max-w-none overflow-x-auto"
                        }
                      >
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm, remarkBreaks]}
                          components={mdComponents}
                        >
                          {content}
                        </ReactMarkdown>
                      </div>
                    </div>
                  )}
                </div>
                {index === messages.length - 1 &&
                  message.type === "ai" &&
                  !researchStarted &&
                  !isLoading &&
                  !hasReportInThread &&
                  !liveActivityEvents.some((e) => e.title === "最终确定答案") && (
                    <div className="flex items-start gap-3">
                      <div className="relative max-w-[85%] md:max-w-[80%] rounded-xl p-3 shadow-sm break-words bg-neutral-800 text-neutral-100">
                        <div className="flex items-center justify-between gap-3">
                          <span className="text-sm text-neutral-400">
                            确认以上研究方向后，点击「需求确认」开始深度研究
                          </span>
                          <Button
                            variant="default"
                            className="bg-neutral-700 hover:bg-neutral-600 cursor-pointer text-sm shrink-0"
                            onClick={handleStartResearch}
                          >
                            需求确认
                          </Button>
                        </div>
                      </div>
                    </div>
                  )}
              </div>
            );
          })}
          {streamingContent && (
            <div className="flex items-start gap-3">
              <div className="relative break-words flex flex-col w-full max-w-[95%] bg-neutral-800 text-neutral-100 rounded-xl rounded-bl-none p-3 shadow-sm border border-neutral-700">
                <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]} components={mdComponents}>
                  {normalizeMarkdown(streamingContent)}
                </ReactMarkdown>
                <span className="text-xs text-neutral-500 mt-1 inline-flex items-center gap-1">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  {streamingNode === "generate_plan"
                    ? "正在生成计划..."
                    : streamingNode === "outline"
                    ? "正在生成提纲..."
                    : streamingNode === "draft"
                    ? "正在撰写草稿..."
                    : streamingNode === "cite_and_polish"
                    ? "正在润色和引用..."
                    : "正在生成..."}
                </span>
              </div>
            </div>
          )}
          {isLoading && !streamingContent && (
            <div className="flex items-start gap-3 mt-3">
              <div className="relative max-w-[85%] md:max-w-[80%] rounded-xl p-3 shadow-sm break-words bg-neutral-800 text-neutral-100 rounded-bl-none w-full min-h-[56px]">
                <div className="flex items-center justify-start h-full">
                  <Loader2 className="h-5 w-5 animate-spin text-neutral-400 mr-2" />
                  <span>处理中...</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
      <InputForm
        ref={inputFormRef}
        onSubmit={onSubmit}
        isLoading={isLoading}
        onCancel={onCancel}
        onNewTopic={onNewTopic}
        hasHistory={messages.length > 0}
        placeholder={
          hasReportInThread
            ? "可追问报告内容，或说「导出报告」「继续研究」"
            : "如何评价DeepSeek成立Harness团队？"
        }
      />
    </div>
  );
}
