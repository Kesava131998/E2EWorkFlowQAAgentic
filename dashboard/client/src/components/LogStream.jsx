import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronRight } from 'lucide-react'
import { LEVEL_COLORS, LEVEL_PREFIXES } from '../constants/stages.js'

function LogEntry({ event }) {
  const time = event.timestamp
    ? new Date(event.timestamp).toLocaleTimeString('en-US', { hour12: false, fractionalSecondDigits: 1 })
    : ''

  const color = LEVEL_COLORS[event.level] || 'text-gray-400'
  const prefix = LEVEL_PREFIXES[event.level] || '  '

  // ── Self-heal: locator diff ─────────────────────────────────────────────
  if (event.type === 'locator_diff') {
    const { file, line, selector_name, broken, healed } = event.data || {}
    return (
      <motion.div
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        className="my-3 rounded-lg overflow-hidden border border-purple-500/30 bg-purple-950/20 shadow-[0_0_18px_#a855f720]"
      >
        {/* Header bar */}
        <div className="flex items-center justify-between px-3 py-1.5 bg-purple-900/30 border-b border-purple-500/20">
          <div className="flex items-center gap-2">
            <span className="text-purple-400 text-[10px] font-mono uppercase tracking-widest">Locator Healed</span>
            {selector_name && (
              <span className="text-[10px] font-mono text-purple-300 bg-purple-900/50 px-2 py-0.5 rounded border border-purple-700/50">
                {selector_name}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 text-[9px] font-mono text-purple-500">
            {file && <span>{file}{line ? `:${line}` : ''}</span>}
            <span className="text-gray-500">{time}</span>
          </div>
        </div>
        {/* Diff body */}
        <div className="px-3 py-2 space-y-1 font-mono text-[12px]">
          <div className="flex items-start gap-2 text-red-400 bg-red-950/30 rounded px-2 py-1">
            <span className="text-red-500 font-bold select-none shrink-0">−</span>
            <span className="break-all opacity-90">{broken || '(unknown)'}</span>
          </div>
          <div className="flex items-start gap-2 text-emerald-400 bg-emerald-950/30 rounded px-2 py-1">
            <span className="text-emerald-500 font-bold select-none shrink-0">+</span>
            <span className="break-all">{healed || '(unknown)'}</span>
          </div>
        </div>
      </motion.div>
    )
  }

  // ── HITL checkpoint ─────────────────────────────────────────────────────
  if (event.type === 'hitl_checkpoint') {
    return (
      <motion.div
        initial={{ opacity: 0, x: -5 }}
        animate={{ opacity: 1, x: 0 }}
        className="py-2.5 px-3 border-l-2 border-amber-500 bg-amber-500/10 my-2 rounded-r-md flex items-start"
      >
        <span className="text-gray-500 text-[11px] font-mono mr-3 mt-0.5 whitespace-nowrap">{time}</span>
        <span className="text-amber-500 font-medium text-sm whitespace-pre-wrap">Action Required: {event.message}</span>
      </motion.div>
    )
  }

  if (event.type === 'hitl_response') {
    const approved = event.choice === 'approve'
    return (
      <motion.div
        initial={{ opacity: 0, x: -5 }}
        animate={{ opacity: 1, x: 0 }}
        className={`py-2 px-3 border-l-2 ${approved ? 'border-emerald-500 bg-emerald-500/10' : 'border-red-500 bg-red-500/10'} my-1 rounded-r-md`}
      >
        <span className="text-gray-500 text-[11px] font-mono mr-3">{time}</span>
        <span className={`font-medium text-sm ${approved ? 'text-emerald-500' : 'text-red-500'}`}>
          {approved ? '✓ Authorization Granted — Resuming' : '✗ Authorization Denied — Halting'}
        </span>
      </motion.div>
    )
  }

  if (event.type === 'stage_start') {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="py-2.5 my-1 border-t border-white/5 mt-3 flex items-center"
      >
        <span className="text-gray-500 text-[11px] font-mono mr-3">{time}</span>
        <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 mr-2" />
        <span className="text-indigo-400 font-semibold text-xs uppercase tracking-wide">
          {event.message || `Starting: ${event.stage}`}
        </span>
      </motion.div>
    )
  }

  if (event.type === 'stage_complete') {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="py-1 my-1 flex items-center"
      >
        <span className="text-gray-500 text-[11px] font-mono mr-3">{time}</span>
        <span className="text-emerald-500 mr-2 font-bold">✓</span>
        <span className="text-gray-300 font-medium text-xs">
          {event.message || `${event.stage} complete`}
        </span>
      </motion.div>
    )
  }

  if (event.type === 'workflow_start') {
    const isSelfHeal = event.data?.mode === 'self_heal'
    return (
      <motion.div
        initial={{ opacity: 0, y: 5 }}
        animate={{ opacity: 1, y: 0 }}
        className={`py-3 px-4 mb-3 border rounded-lg ${isSelfHeal ? 'bg-purple-950/30 border-purple-500/30' : 'bg-white/5 border-white/10'}`}
      >
        <div className={`font-semibold text-sm ${isSelfHeal ? 'text-purple-300' : 'text-gray-200'}`}>
          {isSelfHeal ? '🩹 Self-Heal Demo Started' : 'Workflow Initiated'}
        </div>
        {event.data?.ticket && (
          <div className="text-gray-500 text-xs mt-1">Target: {event.data.ticket}</div>
        )}
      </motion.div>
    )
  }

  if (event.type === 'workflow_complete') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 5 }}
        animate={{ opacity: 1, y: 0 }}
        className="py-3 px-4 mt-4 bg-emerald-500/10 border border-emerald-500/20 rounded-lg flex items-center gap-3"
      >
        <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-500">✓</div>
        <div className="text-emerald-500 font-semibold text-sm">
          {event.data?.mode === 'self_heal' ? '🩹 Self-Heal Complete — All Tests Passing' : 'Workflow Complete'}
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="py-1 px-2 hover:bg-white/[0.02] rounded transition-colors group flex items-start"
    >
      <span className="text-gray-500 text-[11px] font-mono mr-3 mt-0.5 whitespace-nowrap">{time}</span>
      <span className={`font-mono text-[12px] leading-relaxed break-words ${color}`}>
        {prefix}{event.message}
      </span>
    </motion.div>
  )
}

function HitlLogGroup({ block }) {
  const { checkpoint, response } = block

  const time = checkpoint.timestamp
    ? new Date(checkpoint.timestamp).toLocaleTimeString('en-US', { hour12: false, fractionalSecondDigits: 1 })
    : ''

  if (!response) {
    return (
      <motion.div
        initial={{ opacity: 0, x: -5 }}
        animate={{ opacity: 1, x: 0 }}
        className="py-2.5 px-3 border-l-2 border-amber-500 bg-amber-500/10 my-2 rounded-r-md flex items-start"
      >
        <span className="text-gray-500 text-[11px] font-mono mr-3 mt-0.5 whitespace-nowrap">{time}</span>
        <span className="text-amber-500 font-medium text-[13px] whitespace-pre-wrap">Action Required: {checkpoint.message}</span>
      </motion.div>
    )
  }

  const approved = response.choice === 'approve'
  const colorClass = approved ? 'text-emerald-500' : 'text-red-500'
  const bgClass = approved ? 'bg-emerald-500/10 border-emerald-500' : 'bg-red-500/10 border-red-500'
  const icon = approved ? '✓' : '✗'
  const statusText = approved ? 'Authorization Granted' : 'Authorization Denied'

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={`py-2 px-3 border-l-2 my-2 rounded-r-md flex items-center justify-between transition-colors duration-500 ${bgClass}`}
    >
      <div className="flex items-center gap-3 overflow-hidden pr-4">
        <span className="text-gray-500 text-[11px] font-mono shrink-0">{time}</span>
        <span className="text-[12px] text-gray-300 truncate opacity-75 font-medium">
          {checkpoint.message.split('\n')[0]}
        </span>
      </div>
      <div className={`flex items-center gap-1.5 font-bold text-[10px] uppercase tracking-wider shrink-0 px-2.5 py-1 rounded-full border ${approved ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-red-500/10 text-red-400 border-red-500/30'}`}>
        <span>{icon}</span>
        <span>{statusText}</span>
      </div>
    </motion.div>
  )
}

function StageLogGroup({ block }) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const startEvent = block.events[0]
  const isComplete = block.status === 'complete' || block.status === 'error'

  useEffect(() => {
    if (isComplete) {
      const timer = setTimeout(() => setIsCollapsed(true), 500)
      return () => clearTimeout(timer)
    }
  }, [isComplete])

  const time = startEvent.timestamp
    ? new Date(startEvent.timestamp).toLocaleTimeString('en-US', { hour12: false, fractionalSecondDigits: 1 })
    : ''

  // Self-heal stages get a purple accent instead of indigo
  const isSelfHeal = ['baseline_run','inject_decay','detect_failure','inspect_dom','apply_heal','verify_heal'].includes(startEvent.stage)
  const accentClass = isSelfHeal ? 'text-purple-400' : 'text-indigo-400'
  const dotClass    = isSelfHeal ? 'bg-purple-500'   : 'bg-indigo-500'

  return (
    <div className="my-2 border border-white/5 bg-white/[0.01] rounded-lg overflow-hidden">
      <div
        className="py-2.5 px-3 flex items-center cursor-pointer hover:bg-white/[0.03] transition-colors select-none"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <span className="text-gray-500 text-[11px] font-mono mr-3 shrink-0">{time}</span>
        <ChevronRight className={`w-4 h-4 mr-2 transition-transform duration-200 text-gray-500 shrink-0 ${isCollapsed ? '' : 'rotate-90'}`} />
        <span className={`font-semibold text-xs uppercase tracking-wide flex-1 truncate ${accentClass}`}>
          {startEvent.message || `Stage: ${startEvent.stage}`}
        </span>
        {isComplete && isCollapsed && (
          <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${block.status === 'complete' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
            {block.status === 'complete' ? 'COMPLETED' : 'FAILED'}
          </span>
        )}
      </div>

      <AnimatePresence initial={false}>
        {!isCollapsed && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-white/5"
          >
            <div className="p-2 space-y-px">
              {block.events.slice(1).map(e => (
                <LogEntry key={e.id} event={e} />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export function LogStream({ events }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [events.length])

  const visibleEvents = events.filter(e => e.type !== 'reset')

  const blocks = []
  let currentBlock = null

  visibleEvents.forEach((event) => {
    if (event.type === 'workflow_start' || event.type === 'workflow_complete') {
      blocks.push({ type: 'isolated', event })
      return
    }

    if (event.type === 'hitl_checkpoint') {
      currentBlock = { type: 'hitl_group', checkpoint: event, response: null, id: event.id }
      blocks.push(currentBlock)
      return
    }

    if (event.type === 'hitl_response') {
      for (let i = blocks.length - 1; i >= 0; i--) {
        if (blocks[i].type === 'hitl_group' && blocks[i].checkpoint.checkpoint_id === event.checkpoint_id) {
          blocks[i].response = event
          return
        }
      }
      blocks.push({ type: 'isolated', event })
      return
    }

    // locator_diff belongs to current stage group if one is open, else isolated
    if (event.type === 'locator_diff') {
      if (currentBlock?.type === 'stage_group') {
        currentBlock.events.push(event)
      } else {
        blocks.push({ type: 'isolated', event })
      }
      return
    }

    if (event.stage && !event.stage.startsWith('hitl_')) {
      if (event.type === 'stage_start') {
        currentBlock = { type: 'stage_group', stageId: event.stage, events: [event], status: 'active', id: event.id }
        blocks.push(currentBlock)
      } else {
        if (currentBlock && currentBlock.stageId === event.stage) {
          currentBlock.events.push(event)
          if (event.type === 'stage_complete') currentBlock.status = 'complete'
          if (event.type === 'stage_error')    currentBlock.status = 'error'
        } else {
          blocks.push({ type: 'isolated', event })
        }
      }
    } else {
      blocks.push({ type: 'isolated', event })
    }
  })

  return (
    <div className="flex flex-col h-full bg-[#111113]">
      <div className="flex items-center justify-between px-5 py-4 border-b border-white/5 shrink-0">
        <div className="flex items-center gap-2 text-gray-200">
          <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
          </svg>
          <span className="text-sm font-semibold">Console Output</span>
        </div>
        <span className="text-[11px] text-gray-500 font-medium px-2 py-0.5 bg-white/5 rounded-full">{visibleEvents.length} events</span>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 relative z-20 custom-scrollbar">
        <AnimatePresence initial={false}>
          {blocks.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center">
              <div className="text-gray-500 text-sm font-medium animate-pulse">
                Awaiting telemetry...
              </div>
            </div>
          ) : (
            blocks.map((block, i) => {
              if (block.type === 'stage_group') {
                return <StageLogGroup key={block.id || `group-${i}`} block={block} />
              } else if (block.type === 'hitl_group') {
                return <HitlLogGroup key={block.id || `hitl-${i}`} block={block} />
              } else {
                return <LogEntry key={block.event.id || `iso-${i}`} event={block.event} />
              }
            })
          )}
        </AnimatePresence>
        <div ref={bottomRef} className="h-4 shrink-0" />
      </div>
    </div>
  )
}
