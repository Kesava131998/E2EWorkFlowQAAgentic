import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Ticket, GitBranch, Search, FileText, Settings, FlaskConical, Send, Package, GitPullRequest, CheckCircle, Eye, RotateCcw, MessageSquareDot } from 'lucide-react'
import { STAGES, STAGE_STATUS } from '../constants/stages.js'
import { InnocitoLogo } from './Header.jsx'

const CheckIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
  </svg>
)

const CrossIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
  </svg>
)

// ─── Stage-specific rich detail cards ─────────────────────────────────────────

function Chip({ children, color = 'gray' }) {
  const colors = {
    gray:    'bg-gray-800 text-gray-400 border-gray-700',
    cyan:    'bg-cyan-900/40 text-cyan-300 border-cyan-700/50',
    green:   'bg-emerald-900/40 text-emerald-300 border-emerald-700/50',
    red:     'bg-red-900/40 text-red-300 border-red-700/50',
    amber:   'bg-amber-900/40 text-amber-300 border-amber-700/50',
    purple:  'bg-purple-900/40 text-purple-300 border-purple-700/50',
    blue:    'bg-blue-900/40 text-blue-300 border-blue-700/50',
  }
  return (
    <span className={`text-[9px] font-mono border px-1.5 py-0.5 rounded ${colors[color] || colors.gray}`}>
      {children}
    </span>
  )
}

function Card({ children }) {
  return (
    <div className="bg-white/[0.03] border border-white/[0.07] rounded-lg p-2.5 space-y-2">
      {children}
    </div>
  )
}

function Row({ label, children }) {
  return (
    <div className="flex items-center justify-between gap-2 min-w-0">
      <span className="text-[9px] text-gray-600 uppercase tracking-wider shrink-0">{label}</span>
      <span className="text-[10px] font-mono text-gray-300 truncate text-right">{children}</span>
    </div>
  )
}

const STATUS_COLOR = { 'In Progress': 'amber', 'In Review': 'blue', 'Done': 'green', 'To Do': 'gray' }
const PRIORITY_COLOR = { 'High': 'red', 'Medium': 'amber', 'Low': 'gray' }
const DECISION_COLOR = { 'APPROVE': 'green', 'REQUEST_CHANGES': 'red', 'COMMENT': 'amber' }

function JiraFetchCard({ d }) {
  return (
    <Card>
      <div className="flex items-center gap-1.5 flex-wrap">
        <Chip color="purple">{d.ticket}</Chip>
        {d.status  && <Chip color={STATUS_COLOR[d.status]   || 'gray'}>{d.status}</Chip>}
        {d.priority && <Chip color={PRIORITY_COLOR[d.priority] || 'gray'}>{d.priority}</Chip>}
      </div>
      {d.summary && <p className="text-[11px] text-gray-200 font-mono leading-snug">{d.summary}</p>}
      <div className="flex items-center justify-between text-[9px] font-mono text-gray-500">
        {d.assignee && <span>👤 {d.assignee}</span>}
        {d.acs_found && <span>{d.acs_found} ACs</span>}
      </div>
    </Card>
  )
}

function BranchCard({ d }) {
  return (
    <Card>
      <div className="flex items-start gap-1.5">
        <span className="text-emerald-500 mt-0.5 shrink-0">🌿</span>
        <span className="text-[10px] font-mono text-emerald-300 break-all leading-snug">{d.branch}</span>
      </div>
      {d.base && <Row label="from"><span className="text-gray-400">{d.base}</span></Row>}
    </Card>
  )
}

function SwaggerCard({ d }) {
  return (
    <Card>
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-mono text-blue-300">{d.endpoints_found} endpoints</span>
        <Chip color="blue">Swagger</Chip>
      </div>
      {d.base_url && <p className="text-[9px] font-mono text-gray-500 truncate">{d.base_url}</p>}
    </Card>
  )
}

function TestCasesCard({ d }) {
  return (
    <Card>
      <div className="flex items-center justify-between">
        <span className="text-[13px] font-mono text-cyan-300 font-semibold">{d.cases_total}</span>
        <span className="text-[9px] text-gray-500 font-mono">{d.acs_covered} ACs</span>
      </div>
      <div className="flex gap-1.5">
        {d.ui_cases  != null && <Chip color="cyan">{d.ui_cases} UI</Chip>}
        {d.api_cases != null && <Chip color="blue">{d.api_cases} API</Chip>}
      </div>
    </Card>
  )
}

function GenerateTestsCard({ d }) {
  const file = (d.test_file || d.ui_file || '').split('/').pop()
  return (
    <Card>
      <div className="flex items-center justify-between">
        <span className="text-[13px] font-mono text-amber-300 font-semibold">{d.total_functions}</span>
        <Chip color="amber">functions</Chip>
      </div>
      {file && <p className="text-[9px] font-mono text-gray-500 truncate">{file}</p>}
    </Card>
  )
}

function RunTestsCard({ d }) {
  return (
    <Card>
      <div className="flex items-center gap-2 font-mono">
        <span className="text-emerald-400 text-[11px]">✓ {d.passed}</span>
        <span className="text-red-400   text-[11px]">✗ {d.failed}</span>
        <span className="text-gray-500  text-[11px]">⏭ {d.skipped}</span>
        {d.duration_s && <span className="text-gray-600 text-[10px] ml-auto">{d.duration_s}s</span>}
      </div>
      <div className="flex items-center gap-1.5 flex-wrap">
        {d.browser && <Chip color="gray">{d.browser}</Chip>}
        {d.scope   && <Chip color="gray">{d.scope}</Chip>}
      </div>
    </Card>
  )
}

function PostmanCard({ d }) {
  return (
    <Card>
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-mono text-amber-300">{d.requests} requests</span>
        {d.folders && <span className="text-[10px] font-mono text-gray-500">{d.folders} folders</span>}
      </div>
      {d.workspace && (
        <div className="flex items-center gap-1.5">
          <span className="text-[9px] font-mono text-gray-500">{d.workspace} workspace</span>
          <Chip color="green">uploaded ✓</Chip>
        </div>
      )}
    </Card>
  )
}

function CommitCard({ d }) {
  return (
    <Card>
      <div className="flex items-center gap-1.5">
        <Chip color="purple">{(d.commit || '').slice(0, 7)}</Chip>
        {d.files_staged && <span className="text-[9px] font-mono text-gray-500">{d.files_staged} files</span>}
      </div>
      {d.branch && <p className="text-[9px] font-mono text-gray-500 truncate">{d.branch}</p>}
    </Card>
  )
}

function RaisePrCard({ d }) {
  return (
    <Card>
      <div className="flex items-center gap-1.5 flex-wrap">
        {d.pr_number && <Chip color="cyan">PR #{d.pr_number}</Chip>}
        {d.draft != null && <Chip color={d.draft ? 'amber' : 'green'}>{d.draft ? 'Draft' : 'Ready'}</Chip>}
      </div>
      {(d.coverage_before != null && d.coverage_after != null) && (
        <Row label="coverage">
          <span className="text-emerald-400">{d.coverage_before} → {d.coverage_after} tests</span>
        </Row>
      )}
      {d.tests_added && <Row label="added"><span className="text-emerald-400">+{d.tests_added}</span></Row>}
    </Card>
  )
}

function UpdateJiraCard({ d }) {
  return (
    <Card>
      <div className="flex items-center gap-1.5">
        {d.ticket && <Chip color="purple">{d.ticket}</Chip>}
        <span className="text-gray-600 text-[10px]">→</span>
        {d.transition && <Chip color={STATUS_COLOR[d.transition] || 'blue'}>{d.transition}</Chip>}
      </div>
    </Card>
  )
}

function PrReviewCard({ d }) {
  const decision = (d.decision || '').toUpperCase()
  return (
    <Card>
      <Chip color={DECISION_COLOR[decision] || 'gray'}>{decision || 'Reviewed'}</Chip>
      <div className="flex items-center gap-3 text-[9px] font-mono text-gray-500">
        {d.issues_found != null  && <span>{d.issues_found} issues</span>}
        {d.suggestions  != null  && <span>{d.suggestions} suggestions</span>}
      </div>
    </Card>
  )
}

const STAGE_CARDS = {
  jira_fetch:        JiraFetchCard,
  branch_create:     BranchCard,
  swagger_discovery: SwaggerCard,
  test_cases:        TestCasesCard,
  generate_tests:    GenerateTestsCard,
  run_tests:         RunTestsCard,
  postman_export:    PostmanCard,
  commit_push:       CommitCard,
  raise_pr:          RaisePrCard,
  update_jira:       UpdateJiraCard,
  pr_review:         PrReviewCard,
}

function StageProperties({ stage, events }) {
  const stageEvents = events.filter(e =>
    ['stage_start', 'stage_complete', 'stage_error'].includes(e.type) && e.stage === stage.id
  )
  // Prefer stage_complete data over stage_start
  const completeEvent = [...stageEvents].reverse().find(e => e.type === 'stage_complete')
  const activeEvent   = completeEvent || [...stageEvents].reverse()[0]

  if (!activeEvent) return null

  const d = activeEvent.data || {}
  const RichCard = STAGE_CARDS[stage.id]
  const hasRichData = RichCard && Object.keys(d).some(k => k !== 'artifacts')

  return (
    <motion.div
      initial={{ height: 0, opacity: 0 }}
      animate={{ height: 'auto', opacity: 1 }}
      exit={{ height: 0, opacity: 0 }}
      className="overflow-hidden"
    >
      <div className="ml-[17px] pl-5 pb-2 pt-2.5 relative">
        <div className="absolute top-0 left-0 bottom-0 w-[2px] bg-gradient-to-b from-indigo-500/40 via-indigo-400 to-indigo-500/40 animate-pulse" />
        {hasRichData
          ? <RichCard d={d} />
          : activeEvent.message && (
              <div className="bg-white/[0.03] rounded-lg px-2.5 py-2 border border-white/[0.07]">
                <p className="text-[11px] text-gray-300 font-mono leading-relaxed">{activeEvent.message}</p>
              </div>
            )
        }
      </div>
    </motion.div>
  )
}

function VerticalConnector({ leftStatus }) {
  const isComplete = leftStatus === STAGE_STATUS.COMPLETE
  const isActive = leftStatus === STAGE_STATUS.ACTIVE

  return (
    <div className="flex flex-col items-start w-full">
      <div className="relative w-[2px] h-5 bg-white/5 ml-[17px]">
        {isComplete && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: '100%' }}
            className="absolute top-0 left-0 w-full bg-emerald-500/50"
          />
        )}
        {isActive && (
          <motion.div
            className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-indigo-500/40 via-indigo-400 to-indigo-500/40 animate-pulse"
            initial={{ height: '0%' }}
            animate={{ height: '100%' }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        )}
      </div>
    </div>
  )
}

const STAGE_ICONS = {
  jira_fetch: Ticket,
  branch_create: GitBranch,
  swagger_discovery: Search,
  test_cases: FileText,
  generate_tests: Settings,
  run_tests: FlaskConical,
  postman_export: Send,
  commit_push: Package,
  raise_pr: GitPullRequest,
  update_jira: CheckCircle,
  pr_review: Eye,
}

function VerticalStageNode({ stage, status, events }) {
  const isActive = status === STAGE_STATUS.ACTIVE
  const isComplete = status === STAGE_STATUS.COMPLETE
  const isError = status === STAGE_STATUS.ERROR

  const nodeClasses = isActive
    ? 'bg-white text-black shadow-[0_0_15px_rgba(255,255,255,0.15)] ring-1 ring-white/50'
    : isComplete
    ? 'bg-brand-success/10 text-brand-success ring-1 ring-brand-success/30'
    : isError
    ? 'bg-brand-danger/10 text-brand-danger ring-1 ring-brand-danger/30'
    : 'bg-[#111113] text-gray-600 ring-1 ring-white/5'

  const labelClasses = isActive
    ? 'text-gray-100 font-semibold'
    : isComplete
    ? 'text-gray-400'
    : isError
    ? 'text-brand-danger'
    : 'text-gray-600'

  const Icon = STAGE_ICONS[stage.id]

  return (
    <div className="flex flex-col relative z-10 w-full">
      <div className="flex items-center gap-3.5">
        <motion.div
          layout
          className={`relative w-9 h-9 rounded-full flex items-center justify-center text-sm transition-all duration-500 ease-out shrink-0 ${nodeClasses}`}
        >
          {isActive && (
            <motion.div 
              className="absolute inset-0 rounded-full border border-white/20"
              animate={{ scale: [1, 1.4, 1], opacity: [0.5, 0, 0.5] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            />
          )}
          {isError ? (
            <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}>
              <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </motion.div>
          ) : (
            <span className={isActive || isComplete ? 'opacity-100' : 'opacity-50 grayscale'}>
              {Icon && <Icon className="w-4 h-4" />}
            </span>
          )}
        </motion.div>
        
        <div className="flex flex-col">
          <span className={`text-[11px] font-medium tracking-wider uppercase transition-colors duration-500 ${labelClasses}`}>
            {stage.label}
          </span>
          <span className="text-[8px] text-gray-500 tracking-widest uppercase mt-0.5">
            {isActive ? 'In Progress' : isComplete ? 'Completed' : isError ? 'Failed' : 'Pending'}
          </span>
        </div>
      </div>
      
      <AnimatePresence>
        {(isActive || isComplete || isError) && <StageProperties stage={stage} events={events} />}
      </AnimatePresence>
    </div>
  )
}

export function Pipeline({ stageStatuses, events, workflowActive, onReset, onTeamsNotify, connected }) {
  const [confirming, setConfirming] = useState(false)
  const [teamsSending, setTeamsSending] = useState(false)
  const [teamsSent, setTeamsSent] = useState(false)

  const handleTeams = async () => {
    setTeamsSending(true)
    setTeamsSent(false)
    try {
      await onTeamsNotify?.()
      setTeamsSent(true)
      setTimeout(() => setTeamsSent(false), 3000)
    } catch (e) {
      console.error('Teams notify failed:', e)
    } finally {
      setTeamsSending(false)
    }
  }

  const handleReset = () => {
    if (!confirming) { setConfirming(true); return }
    onReset?.()
    setConfirming(false)
  }

  return (
    <div className="w-72 shrink-0 border-r border-white/5 bg-[#111113] h-full flex flex-col z-20 shadow-xl overflow-hidden">
      <div className="px-6 py-5 border-b border-white/5 shrink-0">
        <InnocitoLogo />
      </div>

      <div className="flex-1 overflow-y-auto overflow-x-hidden px-6 py-6 custom-scrollbar">
        <div className="flex flex-col pb-4">
          {STAGES.map((stage, i) => (
            <div key={stage.id} className="flex flex-col">
              <VerticalStageNode stage={stage} status={stageStatuses[stage.id] || STAGE_STATUS.IDLE} events={events} />
              {i < STAGES.length - 1 && (
                <VerticalConnector leftStatus={stageStatuses[stage.id] || STAGE_STATUS.IDLE} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Footer: connection status + Teams notify + reset */}
      <div className="shrink-0 border-t border-white/5 px-4 py-3 flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 flex-1 min-w-0">
            <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${connected ? 'bg-emerald-400 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-[10px] font-mono text-gray-600 truncate">
              {connected ? 'localhost:8765' : 'disconnected'}
            </span>
          </div>
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={handleReset}
            onBlur={() => setConfirming(false)}
            className={[
              'shrink-0 flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[10px] font-mono border transition-all duration-150',
              confirming
                ? 'bg-red-900/40 text-red-300 border-red-700/60 hover:bg-red-900/60'
                : 'bg-white/[0.03] text-gray-500 border-white/5 hover:text-gray-300 hover:border-white/10',
            ].join(' ')}
          >
            <RotateCcw className="w-3 h-3" />
            {confirming ? 'Confirm?' : 'Reset'}
          </motion.button>
        </div>

        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={handleTeams}
          disabled={teamsSending}
          className={[
            'w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-[10px] font-mono border transition-all duration-150',
            teamsSent
              ? 'bg-emerald-900/40 text-emerald-300 border-emerald-700/50'
              : teamsSending
              ? 'bg-indigo-900/20 text-indigo-400 border-indigo-700/30 opacity-60 cursor-not-allowed'
              : 'bg-indigo-900/20 text-indigo-300 border-indigo-700/40 hover:bg-indigo-900/40 hover:border-indigo-500/50',
          ].join(' ')}
        >
          <MessageSquareDot className="w-3.5 h-3.5" />
          {teamsSent ? 'Sent to Teams ✓' : teamsSending ? 'Sending…' : 'Send to Teams'}
        </motion.button>
      </div>
    </div>
  )
}
