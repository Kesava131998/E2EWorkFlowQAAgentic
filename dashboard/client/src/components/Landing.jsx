import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GitPullRequest, X, Info } from 'lucide-react'
import { InnocitoLogo } from './Header.jsx'

// ─── Animated background grid ────────────────────────────────────────────────

function GridBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <div
        className="absolute inset-0 opacity-[0.06]"
        style={{
          backgroundImage: 'radial-gradient(circle, #ffffff 1px, transparent 1px)',
          backgroundSize: '32px 32px',
        }}
      />
      <div className="absolute -top-32 -left-32 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl" />
      <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-600/5 rounded-full blur-3xl" />
    </div>
  )
}

// ─── Connection dot ───────────────────────────────────────────────────────────

function ConnectionStatus({ connected }) {
  return (
    <div className="absolute top-6 right-8 flex items-center gap-2">
      <span className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400 animate-pulse' : 'bg-red-500'}`} />
      <span className="text-[11px] font-mono text-gray-500">
        {connected ? 'localhost:8765' : 'server offline'}
      </span>
    </div>
  )
}

// ─── PR Detected Modal ────────────────────────────────────────────────────────

function PrDetectedModal({ pr, onRunHeal, onDismiss, launching }) {
  return (
    <AnimatePresence>
      {pr && (
        <>
          {/* Backdrop */}
          <motion.div
            key="backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            onClick={onDismiss}
          />

          {/* Modal — centering handled by flex wrapper, not transforms, to avoid
               conflict with framer-motion's own y/scale transform */}
          <div className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none">
          <motion.div
            key="modal"
            initial={{ opacity: 0, y: -20, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -12, scale: 0.97 }}
            transition={{ duration: 0.22, ease: 'easeOut' }}
            className="w-full max-w-lg mx-4 pointer-events-auto"
          >
            <div className="rounded-2xl border border-purple-500/30 bg-[#0d0d10]/95 backdrop-blur-xl shadow-2xl shadow-black/60 overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between px-5 py-4 border-b border-white/[0.06]">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-purple-500/20 border border-purple-500/30 flex items-center justify-center">
                    <GitPullRequest className="w-4 h-4 text-purple-300" />
                  </div>
                  <div>
                    <div className="text-[11px] font-semibold text-purple-200 flex items-center gap-1.5">
                      <motion.span
                        className="w-1.5 h-1.5 rounded-full bg-purple-400 inline-block"
                        animate={{ opacity: [1, 0.3, 1] }}
                        transition={{ duration: 0.9, repeat: Infinity }}
                      />
                      PR Detected
                    </div>
                    <div className="text-[9px] font-mono text-gray-600">Webhook event from consumer repo</div>
                  </div>
                </div>
                <button
                  onClick={onDismiss}
                  className="w-6 h-6 rounded-lg flex items-center justify-center text-gray-600 hover:text-gray-300 hover:bg-white/5 transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>

              {/* PR details */}
              <div className="px-5 py-4 space-y-3">
                <div>
                  <div className="text-[9px] font-mono text-gray-600 mb-1">TITLE</div>
                  <div className="text-sm text-white font-medium leading-snug">{pr.title}</div>
                </div>
                <div className="flex gap-4">
                  <div>
                    <div className="text-[9px] font-mono text-gray-600 mb-1">PR</div>
                    <div className="text-[11px] font-mono text-purple-300">#{pr.number}</div>
                  </div>
                  <div className="flex-1">
                    <div className="text-[9px] font-mono text-gray-600 mb-1">BRANCH</div>
                    <div className="text-[11px] font-mono text-indigo-300 truncate">{pr.branch}</div>
                  </div>
                </div>
                <p className="text-[11px] text-gray-500 leading-relaxed">
                  Regression tests will run against this branch. If any locators fail, the self-heal
                  agent will inspect the DOM, call Claude, and patch the Page Object Model.
                </p>
              </div>

              {/* Actions */}
              <div className="px-5 py-4 border-t border-white/[0.05] flex gap-3">
                <motion.button
                  whileTap={{ scale: 0.97 }}
                  onClick={onRunHeal}
                  disabled={launching}
                  className={[
                    'flex-1 py-2.5 rounded-xl text-sm font-semibold tracking-wide transition-all duration-200 flex items-center justify-center gap-2 border',
                    launching
                      ? 'bg-purple-900/30 border-purple-700/30 cursor-wait opacity-70 text-purple-200'
                      : 'bg-purple-500/20 border-purple-500/30 hover:bg-purple-500/30 hover:border-purple-400/40 text-white',
                  ].join(' ')}
                >
                  {launching ? (
                    <>
                      <motion.span
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                        className="w-3.5 h-3.5 border-2 border-purple-400/30 border-t-purple-300 rounded-full inline-block"
                      />
                      Launching…
                    </>
                  ) : (
                    <>🩹 Run Self-Heal</>
                  )}
                </motion.button>
                <button
                  onClick={onDismiss}
                  className="px-4 py-2.5 rounded-xl text-sm font-medium text-gray-500 hover:text-gray-300 hover:bg-white/5 border border-white/[0.06] transition-colors"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}

// ─── Phase guide data ─────────────────────────────────────────────────────────

const E2E_STEPS = [
  { icon: '🎫', label: 'Fetch Ticket',    desc: 'Reads the Jira ticket, acceptance criteria, and priority to scope what needs testing.' },
  { icon: '🌿', label: 'Create Branch',   desc: 'Creates a feature branch in Git named after the ticket ID.' },
  { icon: '🔍', label: 'API Discovery',   desc: 'Scans Swagger/OpenAPI docs to find endpoints relevant to the ticket scope.' },
  { icon: '📋', label: 'Test Cases',      desc: 'Generates a structured test plan — UI and API cases mapped to acceptance criteria.' },
  { icon: '⚙️',  label: 'Generate Tests',  desc: 'Writes Playwright Python test scripts for all generated test cases.' },
  { icon: '🧪', label: 'Run Tests',       desc: 'Executes the test suite and captures results with Allure reporting.' },
  { icon: '📦', label: 'Commit & Push',   desc: 'Stages test files and commits them to the feature branch with a conventional message.' },
  { icon: '🔀', label: 'Raise PR',        desc: 'Opens a GitHub pull request with a test coverage summary attached.' },
  { icon: '✅', label: 'Update Jira',     desc: 'Transitions the Jira ticket status and adds a comment linking to the PR.' },
  { icon: '🔎', label: 'PR Review',       desc: 'Posts an AI-generated code review on the PR highlighting gaps or issues.' },
]

const SELF_HEAL_STEPS = [
  { icon: '🔀', label: 'Fetch PR Diff',   desc: 'Fetches the GitHub PR diff to understand exactly what UI changes were made to the app.' },
  { icon: '🧪', label: 'Run Regression',  desc: 'Runs the Playwright regression suite against the updated branch — expects locator failures if UI changed.' },
  { icon: '🔬', label: 'Inspect DOM',     desc: 'Claude uses the Playwright MCP to open the live page and inspect the DOM for matching selectors.' },
  { icon: '🩹', label: 'Claude Heals',    desc: 'Claude reasons about the correct selector and patches the Page Object Model file automatically.' },
  { icon: '✅', label: 'Verify Heal',     desc: 'Re-runs the regression suite to confirm all tests pass with the healed POM. If regression passed, this stage is skipped.' },
  { icon: '🔀', label: 'Raise Heal PR',   desc: 'Commits the POM patch to a new branch and raises a GitHub PR with the fix details.' },
]

// ─── Steps phase guide modal ──────────────────────────────────────────────────

function StepsModal({ steps, title, accent, onClose }) {
  return (
    <>
      <motion.div
        key="steps-backdrop"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40"
        onClick={onClose}
      />
      <div className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none">
        <motion.div
          key="steps-panel"
          initial={{ opacity: 0, y: -16, scale: 0.96 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -10, scale: 0.97 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
          className="w-full max-w-md mx-4 pointer-events-auto"
        >
          <div className={`rounded-2xl border ${accent.border} bg-[#0d0d10]/95 backdrop-blur-xl shadow-2xl shadow-black/60 overflow-hidden`}>
            <div className="flex items-center justify-between px-5 py-4 border-b border-white/[0.06]">
              <span className={`text-sm font-semibold ${accent.text}`}>{title}</span>
              <button
                onClick={onClose}
                className="w-6 h-6 rounded-lg flex items-center justify-center text-gray-600 hover:text-gray-300 hover:bg-white/5 transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
            <div className="px-5 py-4 space-y-3.5 max-h-[60vh] overflow-y-auto custom-scrollbar">
              {steps.map((step, i) => (
                <div key={i} className="flex gap-3 items-start">
                  <div className={`w-7 h-7 rounded-full ${accent.bg} border ${accent.border} flex items-center justify-center text-sm shrink-0 mt-0.5`}>
                    {step.icon}
                  </div>
                  <div>
                    <div className="text-[11px] font-semibold text-gray-200 mb-0.5">{step.label}</div>
                    <div className="text-[11px] text-gray-500 leading-relaxed">{step.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </>
  )
}

// ─── Mode card ────────────────────────────────────────────────────────────────

function ModeCard({ mode, title, subtitle, description, stages, accentClass, glowClass, icon, emoji, onMockRun, onShowSteps, disabled, launching }) {
  const [hovered, setHovered] = useState(false)

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      onHoverStart={() => setHovered(true)}
      onHoverEnd={() => setHovered(false)}
      className="relative flex flex-col rounded-2xl border border-white/[0.08] bg-white/[0.02] backdrop-blur-sm overflow-hidden cursor-default"
      style={{ minHeight: 420 }}
    >
      {/* Glow top edge */}
      <motion.div
        animate={{ opacity: hovered ? 1 : 0 }}
        transition={{ duration: 0.3 }}
        className={`absolute top-0 left-0 right-0 h-px ${glowClass}`}
      />

      {/* Corner accent */}
      <div className={`absolute top-0 right-0 w-32 h-32 opacity-10 rounded-bl-full ${accentClass}`} />

      <div className="flex flex-col flex-1 p-8 relative z-10">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <div className="text-3xl mb-3">{emoji}</div>
            <h2 className="text-xl font-semibold text-white tracking-tight">{title}</h2>
            <p className={`text-xs font-mono mt-1 ${accentClass.replace('bg-', 'text-').replace('/10', '/80')}`}>
              {subtitle}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {/* Phase guide icon */}
            <button
              onClick={(e) => { e.stopPropagation(); onShowSteps?.() }}
              className="w-7 h-7 rounded-lg flex items-center justify-center text-gray-600 hover:text-gray-300 hover:bg-white/5 border border-white/[0.06] hover:border-white/10 transition-colors"
              title="View phase guide"
            >
              <Info className="w-3.5 h-3.5" />
            </button>
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center border border-white/10 ${accentClass.replace('/10', '/20')}`}>
              {icon}
            </div>
          </div>
        </div>

        {/* Description */}
        <p className="text-sm text-gray-400 leading-relaxed mb-6">{description}</p>

        {/* Stage pills */}
        <div className="flex flex-wrap gap-2 mb-8">
          {stages.map((s, i) => (
            <motion.span
              key={s}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.04 }}
              className="text-[10px] font-mono px-2.5 py-1 rounded-full border border-white/[0.08] bg-white/[0.04] text-gray-400"
            >
              {s}
            </motion.span>
          ))}
        </div>

        <div className="flex-1" />

        {/* Mock Run button */}
        <motion.button
          id={`mock-run-${mode}`}
          whileTap={{ scale: 0.97 }}
          onClick={() => onMockRun(mode)}
          disabled={disabled || launching}
          className={[
            'w-full py-3.5 rounded-xl text-sm font-semibold tracking-wide transition-all duration-200 flex items-center justify-center gap-2.5 border',
            disabled
              ? 'opacity-40 cursor-not-allowed bg-white/5 text-gray-500 border-white/10'
              : launching
              ? `${accentClass.replace('/10', '/20')} border-white/10 cursor-wait opacity-70 text-white`
              : `${accentClass.replace('/10', '/20')} border-white/10 hover:${accentClass.replace('/10', '/30')} hover:border-white/20 text-white`,
          ].join(' ')}
        >
          {launching ? (
            <>
              <motion.span
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full inline-block"
              />
              Launching…
            </>
          ) : disabled ? (
            <>⏳ Running</>
          ) : (
            <>▶ Mock Run</>
          )}
        </motion.button>

        {/* Hint for Claude Code users */}
        <p className="text-center text-[10px] font-mono text-gray-700 mt-3">
          or run <span className="text-gray-500">/{mode === 'e2e' ? 'e2e-workflow' : 'self-heal-pr'}</span> in Claude Code
        </p>
      </div>
    </motion.div>
  )
}

// ─── Landing root ─────────────────────────────────────────────────────────────

export function Landing({ connected, onMockRun, runStatus, pendingPr, onDismissPr }) {
  const [launchingMode, setLaunchingMode] = useState(null)
  const [prLaunching, setPrLaunching] = useState(false)
  const [error, setError] = useState(null)
  const [stepsModalMode, setStepsModalMode] = useState(null) // null | 'e2e' | 'self_heal'

  const handleMockRun = async (mode) => {
    setLaunchingMode(mode)
    setError(null)
    try {
      await onMockRun(mode)
    } catch (err) {
      setError(err.message || 'Failed to start workflow')
      setLaunchingMode(null)
    }
  }

  const handleRunHeal = async () => {
    setPrLaunching(true)
    setError(null)
    try {
      await onMockRun('self_heal', pendingPr)
      onDismissPr()
    } catch (err) {
      setError(err.message || 'Failed to start self-heal')
      setPrLaunching(false)
    }
  }

  const anyRunning = runStatus === 'running' || runStatus === 'launching'

  return (
    <div className="relative h-screen w-full flex flex-col items-center justify-center bg-gray-950 overflow-hidden">
      <GridBackground />
      <ConnectionStatus connected={connected} />

      {/* PR detected modal */}
      <PrDetectedModal
        pr={pendingPr}
        onRunHeal={handleRunHeal}
        onDismiss={onDismissPr}
        launching={prLaunching}
      />

      {/* Phase guide modal */}
      <AnimatePresence>
        {stepsModalMode && (
          <StepsModal
            key={stepsModalMode}
            steps={stepsModalMode === 'e2e' ? E2E_STEPS : SELF_HEAL_STEPS}
            title={stepsModalMode === 'e2e' ? 'E2E Workflow — Phase Guide' : 'Self-Heal Demo — Phase Guide'}
            accent={stepsModalMode === 'e2e'
              ? { border: 'border-indigo-500/30', text: 'text-indigo-300', bg: 'bg-indigo-500/10' }
              : { border: 'border-purple-500/30', text: 'text-purple-300', bg: 'bg-purple-500/10' }
            }
            onClose={() => setStepsModalMode(null)}
          />
        )}
      </AnimatePresence>

      <div className="relative z-10 w-full max-w-4xl px-8">
        {/* Logo + headline */}
        <motion.div
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="text-center mb-12"
        >
          <div className="flex justify-center mb-6">
            <InnocitoLogo />
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight mb-2">
            AI Test Workflow Dashboard
          </h1>
          <p className="text-gray-500 text-sm font-mono">
            Run a mock demo · or trigger a flow from Claude Code
          </p>
        </motion.div>

        {/* Mode cards */}
        <div className="grid grid-cols-2 gap-6">
          <ModeCard
            mode="e2e"
            title="E2E Workflow"
            subtitle="JIRA → TESTS → PR"
            description="Watch the AI agent pick up a Jira ticket, discover API endpoints, generate Playwright test scripts, run them, and raise a pull request — end to end."
            emoji="🎭"
            icon={<span className="text-indigo-400 text-lg">⚡</span>}
            stages={['Fetch Ticket', 'Create Branch', 'API Discovery', 'Test Cases', 'Generate Tests', 'Run Tests', 'Commit & PR']}
            accentClass="bg-indigo-500/10"
            glowClass="bg-gradient-to-r from-transparent via-indigo-500/60 to-transparent"
            onMockRun={handleMockRun}
            onShowSteps={() => setStepsModalMode('e2e')}
            disabled={anyRunning}
            launching={launchingMode === 'e2e' && runStatus === 'launching'}
          />

          <ModeCard
            mode="self_heal"
            title="Self-Heal Demo"
            subtitle="PR → FAIL → HEAL → PASS"
            description="A UI PR renames a CSS class. Regression tests fail. The AI agent inspects the DOM, reads the diff, calls Claude to reason a new selector, patches the POM, and re-runs to confirm."
            emoji="🩹"
            icon={<span className="text-purple-400 text-lg">🔧</span>}
            stages={['Fetch PR Diff', 'Run Regression', 'Inspect DOM', 'Claude Heals', 'Verify Heal', 'Raise Heal PR']}
            accentClass="bg-purple-500/10"
            glowClass="bg-gradient-to-r from-transparent via-purple-500/60 to-transparent"
            onMockRun={handleMockRun}
            onShowSteps={() => setStepsModalMode('self_heal')}
            disabled={anyRunning}
            launching={launchingMode === 'self_heal' && runStatus === 'launching'}
          />
        </div>

        {/* Error toast */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              className="mt-6 text-center text-sm font-mono text-red-400 bg-red-950/40 border border-red-700/40 rounded-lg px-4 py-2.5"
            >
              ✗ {error}
            </motion.div>
          )}
        </AnimatePresence>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="text-center text-[11px] font-mono text-gray-700 mt-8"
        >
          Powered by Playwright · Claude API · FastAPI · React
        </motion.p>
      </div>
    </div>
  )
}
