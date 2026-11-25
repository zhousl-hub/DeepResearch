import { useCallback, useEffect, useState } from "react";
import { LogOut, Plus, Trash2, PanelLeftClose, PanelLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import { deleteThread, fetchThreads, type ThreadSummary } from "@/lib/api";

interface SessionSidebarProps {
  activeThreadId: string;
  onSelect: (threadId: string) => void;
  onNewSession: () => void;
  /** 外部触发刷新列表（如新研究提交后） */
  refreshKey?: number;
}

function formatTime(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  const now = new Date();
  const sameDay =
    d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate();
  if (sameDay) {
    return d.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
  }
  return d.toLocaleDateString("zh-CN", { month: "2-digit", day: "2-digit" });
}

function statusMeta(status: string): { label: string; className: string } {
  switch (status) {
    case "completed":
      return { label: "已完成", className: "text-emerald-400/90" };
    case "paused":
      return { label: "待确认", className: "text-amber-400/90" };
    case "failed":
      return { label: "失败", className: "text-red-400/90" };
    case "running":
      return { label: "进行中", className: "text-sky-400/90" };
    default:
      return { label: status || "", className: "text-neutral-500" };
  }
}

export function SessionSidebar({
  activeThreadId,
  onSelect,
  onNewSession,
  refreshKey = 0,
}: SessionSidebarProps) {
  const { username, logout } = useAuth();
  const [threads, setThreads] = useState<ThreadSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [collapsed, setCollapsed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await fetchThreads(80);
      setThreads(list);
    } catch (err: any) {
      setError(err?.message || "加载历史失败");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load, refreshKey]);

  const handleDelete = async (e: React.MouseEvent, threadId: string, title: string) => {
    e.preventDefault();
    e.stopPropagation();
    const label = (title || "该会话").slice(0, 40);
    if (!window.confirm(`确定删除历史会话「${label}」？删除后不可从列表恢复。`)) {
      return;
    }
    try {
      setError(null);
      setDeletingId(threadId);
      await deleteThread(threadId);
      setThreads((prev) => prev.filter((t) => t.thread_id !== threadId));
      if (activeThreadId === threadId) {
        onNewSession();
      }
    } catch (err: any) {
      setError(err?.message || "删除失败");
    } finally {
      setDeletingId(null);
    }
  };

  const handleLogout = async () => {
    await logout();
    window.location.href = "/login";
  };

  if (collapsed) {
    return (
      <aside className="h-full w-14 shrink-0 border-r border-neutral-700/80 bg-neutral-950 flex flex-col items-center py-3 gap-2">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="text-neutral-300 hover:text-white hover:bg-neutral-800"
          onClick={() => setCollapsed(false)}
          title="展开会话列表"
        >
          <PanelLeft className="h-4 w-4" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="text-neutral-300 hover:text-white hover:bg-neutral-800"
          onClick={onNewSession}
          title="新专题"
        >
          <Plus className="h-4 w-4" />
        </Button>
      </aside>
    );
  }

  return (
    <aside className="h-full w-[280px] shrink-0 border-r border-neutral-700/80 bg-neutral-950 flex flex-col min-w-0 overflow-hidden">
      <div className="flex items-center justify-between gap-2 px-3 py-3 border-b border-neutral-800 shrink-0">
        <div className="text-sm font-semibold tracking-wide text-neutral-100 truncate">
          DeepResearch
        </div>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="text-neutral-400 hover:text-neutral-100 hover:bg-neutral-800 h-8 w-8 shrink-0"
          onClick={() => setCollapsed(true)}
          title="收起"
        >
          <PanelLeftClose className="h-4 w-4" />
        </Button>
      </div>

      <div className="px-3 py-3 shrink-0">
        <Button
          type="button"
          className="w-full justify-start gap-2 bg-neutral-800 hover:bg-neutral-700 text-neutral-50 border border-neutral-700"
          onClick={onNewSession}
        >
          <Plus className="h-4 w-4" />
          新专题
        </Button>
      </div>

      <div className="px-4 pb-2 text-[11px] uppercase tracking-wider text-neutral-500 shrink-0">
        历史会话
      </div>

      {/* 不用 Radix ScrollArea：其 viewport 不约束子元素宽度，会把删除按钮挤出可视区 */}
      <div className="flex-1 min-h-0 overflow-y-auto overflow-x-hidden px-2 pb-2">
        {loading && (
          <div className="px-2 py-4 text-xs text-neutral-500">加载中...</div>
        )}
        {error && (
          <div className="mx-1 mb-2 rounded-md bg-red-950/60 px-2 py-2 text-xs text-red-300">
            {error}
          </div>
        )}
        {!loading && threads.length === 0 && !error && (
          <div className="px-2 py-4 text-xs text-neutral-500">暂无历史会话</div>
        )}
        <div className="flex flex-col gap-1 w-full min-w-0">
          {threads.map((t) => {
            const active = t.thread_id === activeThreadId;
            const status = statusMeta(t.status);
            const busy = deletingId === t.thread_id;
            return (
              <div
                key={t.thread_id}
                className={`w-full min-w-0 max-w-full rounded-lg border transition-colors ${
                  active
                    ? "bg-neutral-800 border-neutral-600"
                    : "bg-transparent border-transparent hover:bg-neutral-900 hover:border-neutral-800"
                }`}
              >
                <div className="flex items-stretch w-full min-w-0">
                  <button
                    type="button"
                    onClick={() => onSelect(t.thread_id)}
                    className="flex-1 min-w-0 text-left px-2.5 py-2 cursor-pointer"
                    title={t.title}
                  >
                    <div className="text-[13px] leading-snug text-neutral-100 truncate">
                      {t.title}
                    </div>
                    <div className="mt-1 flex items-center gap-2 text-[11px] text-neutral-500 min-w-0">
                      <span className="shrink-0">
                        {formatTime(t.updated_at || t.created_at)}
                      </span>
                      <span className={`shrink-0 ${status.className}`}>
                        {status.label}
                      </span>
                    </div>
                  </button>
                  <button
                    type="button"
                    className="shrink-0 self-center mr-1.5 inline-flex h-8 w-8 items-center justify-center rounded-md border border-neutral-700 bg-neutral-900 text-neutral-300 hover:border-red-500/50 hover:bg-red-950/50 hover:text-red-300 disabled:opacity-50"
                    title="删除会话"
                    aria-label={`删除会话 ${t.title}`}
                    disabled={busy}
                    onClick={(e) => handleDelete(e, t.thread_id, t.title)}
                  >
                    <Trash2 className="h-4 w-4" strokeWidth={2} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="border-t border-neutral-800 px-3 py-2.5 flex items-center justify-between gap-2 shrink-0">
        <div className="text-xs text-neutral-400 truncate" title={username || ""}>
          {username || "用户"}
        </div>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-neutral-400 hover:text-neutral-100 hover:bg-neutral-800 shrink-0"
          onClick={handleLogout}
          title="退出登录"
        >
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </aside>
  );
}
