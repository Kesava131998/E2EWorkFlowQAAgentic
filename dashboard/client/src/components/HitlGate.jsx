import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const SERVER_URL = 'http://localhost:8765'

const ARTIFACT_META = {
  csv:       { icon: '📋', color: 'text-cyan-400',   border: 'border-cyan-700/60',   bg: 'bg-cyan-900/20'   },
  python:    { icon: '🐍', color: 'text-green-400',  border: 'border-green-700/60',  bg: 'bg-green-900/20'  },
  markdown:  { icon: '📄', color: 'text-purple-400', border: 'border-purple-700/60', bg: 'bg-purple-900/20' },
  json:      { icon: '{}', color: 'text-amber-400',  border: 'border-amber-700/60',  bg: 'bg-amber-900/20'  },
  report:    { icon: '📊', color: 'text-rose-400',   border: 'border-rose-700/60',   bg: 'bg-rose-900/20'   },
  testcases: { icon: '🃏', color: 'text-cyan-400',   border: 'border-cyan-700/60',   bg: 'bg-cyan-900/20'   },
  default:   { icon: '📁', color: 'text-gray-400',   border: 'border-gray-700',      bg: 'bg-gray-900/20'   },
}

function openArtifact(artifact, onOpenArtifact) {
  if (artifact.type === 'report') {
    window.open(`${SERVER_URL}/${artifact.path}/`, '_blank')
  } else {
    onOpenArtifact?.(artifact)
  }
}

const VARIANT_STYLES = {
  success:  'bg-emerald-600 hover:bg-emerald-500 text-white border border-emerald-500 shadow-[0_0_12px_#10b98144]',
  danger:   'bg-red-900/60 hover:bg-red-800 text-red-200 border border-red-700',
  warning:  'bg-amber-900/60 hover:bg-amber-800 text-amber-200 border border-amber-700',
  feedback: 'bg-blue-900/50 hover:bg-blue-800/60 text-blue-200 border border-blue-700',
  default:  'bg-gray-700/60 hover:bg-gray-600 text-white border border-gray-600',
}

// Options with these variants expand a textarea instead of responding immediately
const FEEDBACK_VARIANTS = new Set(['feedback', 'warning'])

export function HitlGate({ checkpoint, onRespond, onOpenArtifact }) {
  const [feedbackOpt, setFeedbackOpt]   = useState(null)
  const [feedbackText, setFeedbackText] = useState('')

  if (!checkpoint) return null

  const options = checkpoint.options || [
    { id: 'approve', label: 'Approve & Continue', variant: 'success' },
    { id: 'reject',  label: 'Request Changes',    variant: 'feedback' },
  ]

  const contextEntries = Object.entries(checkpoint.data || {}).filter(
    ([k, v]) => v !== null && v !== undefined && v !== '' && k !== 'artifacts'
  )

  const handleOptionClick = (opt) => {
    if (FEEDBACK_VARIANTS.has(opt.variant)) {
      setFeedbackOpt(opt)
      setFeedbackText('')
      return
    }
    onRespond(checkpoint.checkpoint_id, opt.id, null)
  }

  const handleFeedbackSubmit = () => {
    if (!feedbackOpt) return
    onRespond(checkpoint.checkpoint_id, feedbackOpt.id, feedbackText.trim() || null)
    setFeedbackOpt(null)
    setFeedbackText('')
  }

  const handleFeedbackCancel = () => {
    setFeedbackOpt(null)
    setFeedbackText('')
  }

  return (
    <AnimatePresence>
      <motion.div
        key="hitl-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center"
        style={{ background: 'rgba(2, 6, 23, 0.85)', backdropFilter: 'blur(6px)' }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          transition={{ type: 'spring', damping: 20, stiffness: 300 }}
          className="relative w-full max-w-lg mx-4 bg-gray-900 border border-amber-500/40 rounded-xl overflow-hidden shadow-[0_0_60px_#ffb80033]"
        >
          {/* Top accent bar */}
          <div className="h-1 bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 animate-pulse" />

          <div className="p-6">
            {/* Header */}
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center shrink-0">
                <span className="text-amber-400 text-lg">⏸</span>
              </div>
              <div>
                <div className="text-[10px] text-amber-400/80 font-mono uppercase tracking-widest">
                  Human Review Required
                </div>
                <div className="text-xs text-gray-500 font-mono">{checkpoint.checkpoint_id}</div>
              </div>
            </div>

            {/* Message */}
            <p className="text-white font-mono text-sm leading-relaxed mb-5">
              {checkpoint.message}
            </p>

            {/* Context */}
            {contextEntries.length > 0 && (
              <div className="mb-5 bg-gray-800/60 rounded-lg p-3 border border-gray-700">
                <div className="text-[10px] text-gray-500 font-mono uppercase tracking-wider mb-2">Context</div>
                <div className="space-y-1 max-h-40 overflow-y-auto">
                  {contextEntries.map(([key, value]) => (
                    <div key={key} className="flex gap-3 text-xs font-mono">
                      <span className="text-gray-500 min-w-[110px] shrink-0">{key}</span>
                      <span className="text-gray-300 break-all">{JSON.stringify(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Artifact chips — shown when checkpoint data includes viewable artifacts */}
            {checkpoint.data?.artifacts?.length > 0 && (
              <div className="mb-5">
                <div className="text-[10px] text-gray-500 font-mono uppercase tracking-wider mb-2">
                  Review artifacts
                </div>
                <div className="flex flex-wrap gap-2">
                  {checkpoint.data.artifacts.map((artifact) => {
                    const meta = ARTIFACT_META[artifact.type] || ARTIFACT_META.default
                    return (
                      <motion.button
                        key={artifact.label}
                        whileHover={{ scale: 1.03 }}
                        whileTap={{ scale: 0.97 }}
                        onClick={() => openArtifact(artifact, onOpenArtifact)}
                        className={[
                          'flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-mono',
                          'hover:brightness-125 cursor-pointer transition-colors duration-150',
                          meta.color, meta.border, meta.bg,
                        ].join(' ')}
                      >
                        <span>{meta.icon}</span>
                        <span>{artifact.label}</span>
                        <span className="text-[9px] opacity-60 ml-0.5">↗</span>
                      </motion.button>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Feedback textarea — expands when a feedback-type option is clicked */}
            <AnimatePresence>
              {feedbackOpt && (
                <motion.div
                  key="feedback-area"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                  className="mb-4 overflow-hidden"
                >
                  <div className="text-[10px] text-blue-400 font-mono uppercase tracking-wider mb-2">
                    Your feedback for Claude
                  </div>
                  <textarea
                    autoFocus
                    value={feedbackText}
                    onChange={e => setFeedbackText(e.target.value)}
                    onKeyDown={e => {
                      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleFeedbackSubmit()
                      if (e.key === 'Escape') handleFeedbackCancel()
                    }}
                    placeholder='e.g. "Add 2 more negative cases for AC3, rename TC5 to be more descriptive"'
                    rows={3}
                    className="w-full bg-gray-800 border border-blue-700/60 rounded-lg px-3 py-2 text-sm font-mono
                               text-gray-200 placeholder-gray-600 resize-none focus:outline-none
                               focus:border-blue-500 focus:shadow-[0_0_0_2px_#3b82f620] transition-all"
                  />
                  <p className="text-[10px] text-gray-600 font-mono mt-1">
                    ⌘ Enter to submit · Esc to cancel
                  </p>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Action buttons */}
            <div className="flex flex-col gap-2">
              {feedbackOpt ? (
                <>
                  <motion.button
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleFeedbackSubmit}
                    className={`w-full py-3 rounded-lg font-mono text-sm font-medium transition-all duration-200 ${VARIANT_STYLES.feedback}`}
                  >
                    Send feedback to Claude →
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleFeedbackCancel}
                    className="w-full py-2 rounded-lg font-mono text-xs text-gray-500 hover:text-gray-300 transition-colors"
                  >
                    ← back to options
                  </motion.button>
                </>
              ) : (
                options.map((opt) => (
                  <motion.button
                    key={opt.id}
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleOptionClick(opt)}
                    className={`w-full py-3 rounded-lg font-mono text-sm font-medium transition-all duration-200 ${VARIANT_STYLES[opt.variant] || VARIANT_STYLES.default}`}
                  >
                    {opt.label}
                  </motion.button>
                ))
              )}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
