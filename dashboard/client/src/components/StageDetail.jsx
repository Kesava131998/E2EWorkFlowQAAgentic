import { motion, AnimatePresence } from 'framer-motion'
import { STAGES } from '../constants/stages.js'

function DataRow({ label, value }) {
  if (!value) return null
  return (
    <div className="flex flex-col gap-1 py-2 px-1 border-b border-white/5 last:border-0">
      <span className="text-[10px] text-gray-500 font-medium uppercase tracking-wider">{label}</span>
      <span className="text-sm text-gray-200 font-mono break-words">{String(value)}</span>
    </div>
  )
}

export function StageDetail({ events }) {
  const stageEvents = events.filter(e =>
    ['stage_start', 'stage_complete', 'stage_error'].includes(e.type) && e.stage
  )

  const activeEvent = [...stageEvents].reverse().find(e => e.type === 'stage_start') ||
    [...stageEvents].reverse()[0]

  const currentStage = activeEvent
    ? STAGES.find(s => s.id === activeEvent.stage)
    : null

  const latestCompleted = events.filter(e => e.type === 'stage_complete').slice(-4).reverse()

  return (
    <div className="flex flex-col h-full bg-[#111113]">
      <div className="px-5 py-4 border-b border-white/5 flex items-center justify-between">
        <span className="text-sm font-semibold text-gray-200">Properties</span>
        {currentStage && (
          <span className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-primary"></span>
            </span>
            <span className="text-[10px] text-brand-primary font-medium uppercase tracking-wider">Active</span>
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-6 custom-scrollbar">
        <AnimatePresence mode="wait">
          {currentStage ? (
            <motion.div
              key={currentStage.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-xl shadow-sm text-gray-300">
                  {currentStage.icon}
                </div>
                <div className="flex-1 pt-0.5">
                  <div className="text-base font-semibold text-gray-100">{currentStage.label}</div>
                  <div className="text-[11px] text-gray-500 font-medium mt-1 uppercase tracking-wide">
                    {activeEvent.type === 'stage_start' ? 'In Progress' : 'Completed'}
                  </div>
                </div>
              </div>

              {activeEvent.message && (
                <div className="bg-white/5 rounded-lg p-3.5 border border-white/10">
                  <p className="text-sm text-gray-300 leading-relaxed">
                    {activeEvent.message}
                  </p>
                </div>
              )}

              {activeEvent.data && Object.keys(activeEvent.data).length > 0 && (
                <div className="mt-4">
                  <div className="text-[10px] text-gray-500 font-medium uppercase tracking-wider mb-2">Context</div>
                  <div className="bg-white/[0.02] border border-white/5 rounded-lg p-3">
                    {Object.entries(activeEvent.data).map(([k, v]) => (
                      <DataRow key={k} label={k} value={typeof v === 'object' ? JSON.stringify(v) : v} />
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="idle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="h-full flex flex-col items-center justify-center py-12"
            >
              <div className="text-gray-600 mb-4">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="text-sm text-gray-500 font-medium">No active stage selected</div>
            </motion.div>
          )}
        </AnimatePresence>

        {latestCompleted.length > 0 && (
          <div className="pt-6 mt-6 border-t border-white/5">
            <div className="text-[10px] text-gray-500 font-medium uppercase tracking-wider mb-3">Recent History</div>
            <div className="space-y-1.5">
              {latestCompleted.map((ev, i) => {
                const s = STAGES.find(st => st.id === ev.stage)
                return (
                  <motion.div 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    key={i} 
                    className="flex items-center gap-3 px-3 py-2 bg-white/[0.02] rounded border border-white/5 text-sm"
                  >
                    <span className="text-brand-success">✓</span>
                    <span className="text-gray-300 font-medium">{s?.label || ev.stage}</span>
                  </motion.div>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
