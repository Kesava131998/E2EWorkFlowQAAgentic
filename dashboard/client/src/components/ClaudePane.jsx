import { useEffect, useRef, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Minus, ChevronUp, Bot, Cpu, Sparkles } from 'lucide-react'

// ─── Phase config ─────────────────────────────────────────────────────────────

const PHASE_META = {
  prompt: {
    label: 'Prompt',
    bg: 'bg-white/[0.04]',
    border: 'border-white/[0.08]',
    icon: '📤',
    textColor: 'text-gray-300',
    badgeClass: 'bg-gray-800 text-gray-400 border-gray-700',
  },
  thinking: {
    label: 'Thinking…',
    bg: 'bg-purple-950/20',
    border: 'border-purple-500/20',
    icon: '💭',
    textColor: 'text-purple-200',
    badgeClass: 'bg-purple-900/40 text-purple-300 border-purple-700/50',
  },
  response: {
    label: 'Response',
    bg: 'bg-emerald-950/20',
    border: 'border-emerald-500/20',
    icon: '✦',
    textColor: 'text-emerald-100',
    badgeClass: 'bg-emerald-900/40 text-emerald-300 border-emerald-700/50',
  },
  patch: {
    label: 'Patch',
    bg: 'bg-amber-950/20',
    border: 'border-amber-500/20',
    icon: '🩹',
    textColor: 'text-amber-200',
    badgeClass: 'bg-amber-900/40 text-amber-300 border-amber-700/50',
  },
  tool_call: {
    label: 'Tool Call',
    bg: 'bg-blue-950/20',
    border: 'border-blue-500/20',
    icon: '⚙',
    textColor: 'text-blue-200',
    badgeClass: 'bg-blue-900/40 text-blue-300 border-blue-700/50',
  },
}

// ─── Typing cursor ────────────────────────────────────────────────────────────

function TypingCursor() {
  return (
    <motion.span
      animate={{ opacity: [1, 0, 1] }}
      transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
      className="inline-block w-[2px] h-[1em] bg-current align-middle ml-0.5"
    />
  )
}

// ─── Single message bubble ────────────────────────────────────────────────────

function MessageBubble({ activity, isLast, isActive }) {
  const meta = PHASE_META[activity.phase] || PHASE_META.response

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className={`rounded-xl border px-3 py-2.5 space-y-1.5 ${meta.bg} ${meta.border}`}
    >
      {/* Header row */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5">
          <span className="text-[11px]">{meta.icon}</span>
          <span className={`text-[9px] font-mono border px-1.5 py-0.5 rounded ${meta.badgeClass}`}>
            {meta.label}
          </span>
          {activity.model && (
            <span className="text-[9px] font-mono text-gray-600">{activity.model}</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {activity.tokens != null && (
            <span className="text-[9px] font-mono text-gray-600">{activity.tokens} tok</span>
          )}
          {activity.elapsed_ms != null && (
            <span className="text-[9px] font-mono text-gray-600">{activity.elapsed_ms}ms</span>
          )}
        </div>
      </div>

      {/* Content */}
      <pre
        className={`text-[10px] font-mono leading-relaxed whitespace-pre-wrap break-words ${meta.textColor} max-h-48 overflow-y-auto custom-scrollbar`}
      >
        {activity.content}
        {isLast && isActive && <TypingCursor />}
      </pre>
    </motion.div>
  )
}

// ─── Collapsed pill ───────────────────────────────────────────────────────────

function CollapsedPill({ onExpand, hasActivity, isActive }) {
  return (
    <motion.button
      id="claude-pane-toggle"
      layout
      onClick={onExpand}
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      className={[
        'flex items-center gap-2.5 px-4 py-2.5 rounded-2xl border backdrop-blur-md shadow-2xl transition-all duration-300 cursor-pointer',
        isActive
          ? 'bg-purple-950/80 border-purple-500/40 shadow-purple-900/30'
          : 'bg-[#111113]/90 border-white/[0.08]',
      ].join(' ')}
    >
      {/* Animated Claude icon */}
      <div className="relative">
        <Bot className={`w-4 h-4 ${isActive ? 'text-purple-300' : 'text-gray-500'}`} />
        {isActive && (
          <motion.div
            className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-purple-400 rounded-full"
            animate={{ scale: [1, 1.4, 1], opacity: [1, 0.5, 1] }}
            transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
          />
        )}
      </div>
      <span className={`text-[11px] font-mono font-medium ${isActive ? 'text-purple-200' : 'text-gray-500'}`}>
        {isActive ? 'Claude is thinking…' : hasActivity ? 'Claude activity' : 'Claude'}
      </span>
      {hasActivity && !isActive && (
        <span className="text-[9px] font-mono text-gray-600 bg-gray-800 border border-gray-700 px-1.5 py-0.5 rounded">
          {hasActivity} events
        </span>
      )}
      <ChevronUp className="w-3 h-3 text-gray-600" />
    </motion.button>
  )
}

// ─── Claude Pane root ─────────────────────────────────────────────────────────

export function ClaudePane({ activities, isActive }) {
  const [open, setOpen] = useState(false)
  const [minimized, setMinimized] = useState(false)
  const bottomRef = useRef(null)

  // Auto-open when Claude first becomes active in a run
  const prevActiveRef = useRef(false)
  useEffect(() => {
    if (isActive && !prevActiveRef.current) {
      setOpen(true)
      setMinimized(false)
    }
    prevActiveRef.current = isActive
  }, [isActive])

  // Auto-scroll to bottom as new messages arrive
  useEffect(() => {
    if (open && !minimized) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [activities, open, minimized])

  // Reset minimized state on new workflow
  useEffect(() => {
    if (activities.length === 0) {
      setOpen(false)
      setMinimized(false)
    }
  }, [activities.length])

  const hasActivity = activities.length

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-2">
      <AnimatePresence mode="wait">
        {open && !minimized ? (
          /* ── Expanded pane ── */
          <motion.div
            key="expanded"
            initial={{ opacity: 0, y: 16, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.97 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className="w-[420px] max-h-[520px] flex flex-col rounded-2xl border border-white/[0.08] bg-[#0d0d10]/95 backdrop-blur-xl shadow-2xl shadow-black/60 overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/[0.06] shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="relative">
                  <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500/30 to-indigo-500/30 border border-purple-500/30 flex items-center justify-center">
                    <Bot className="w-3.5 h-3.5 text-purple-300" />
                  </div>
                  {isActive && (
                    <motion.div
                      className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-purple-400 rounded-full"
                      animate={{ scale: [1, 1.5, 1], opacity: [1, 0.4, 1] }}
                      transition={{ duration: 1.2, repeat: Infinity }}
                    />
                  )}
                </div>
                <div>
                  <div className="text-[11px] font-semibold text-gray-200">Claude Activity</div>
                  <div className="text-[9px] font-mono text-gray-600 flex items-center gap-1.5">
                    {isActive ? (
                      <>
                        <motion.span
                          className="w-1.5 h-1.5 rounded-full bg-purple-400 inline-block"
                          animate={{ opacity: [1, 0.3, 1] }}
                          transition={{ duration: 0.8, repeat: Infinity }}
                        />
                        Processing…
                      </>
                    ) : (
                      <>{hasActivity} events recorded</>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setMinimized(true)}
                  className="w-6 h-6 rounded-lg flex items-center justify-center text-gray-600 hover:text-gray-300 hover:bg-white/5 transition-colors"
                  title="Minimise"
                >
                  <Minus className="w-3 h-3" />
                </button>
                <button
                  onClick={() => setOpen(false)}
                  className="w-6 h-6 rounded-lg flex items-center justify-center text-gray-600 hover:text-red-400 hover:bg-red-900/20 transition-colors"
                  title="Close"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            </div>

            {/* Message thread */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2.5 custom-scrollbar">
              {activities.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-32 gap-3">
                  <div className="w-10 h-10 rounded-xl bg-purple-900/20 border border-purple-500/20 flex items-center justify-center">
                    <Sparkles className="w-5 h-5 text-purple-400/50" />
                  </div>
                  <p className="text-[11px] font-mono text-gray-600 text-center leading-relaxed">
                    Claude activity will appear here<br />when a workflow is running
                  </p>
                </div>
              ) : (
                activities.map((a, i) => (
                  <MessageBubble
                    key={i}
                    activity={a}
                    isLast={i === activities.length - 1}
                    isActive={isActive}
                  />
                ))
              )}
              <div ref={bottomRef} />
            </div>

            {/* Footer */}
            <div className="shrink-0 px-4 py-2.5 border-t border-white/[0.05] flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <Cpu className="w-3 h-3 text-gray-600" />
                <span className="text-[9px] font-mono text-gray-600">
                  Powered by Anthropic API
                </span>
              </div>
              <span className="text-[9px] font-mono text-gray-700">
                {activities.length} message{activities.length !== 1 ? 's' : ''}
              </span>
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>

      {/* Collapsed pill (always visible as trigger) */}
      {(!open || minimized) && (
        <CollapsedPill
          onExpand={() => { setOpen(true); setMinimized(false) }}
          hasActivity={hasActivity}
          isActive={isActive}
        />
      )}
    </div>
  )
}
