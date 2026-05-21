import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Table, Code2, FileJson, FileText, Folder, X, PieChart, LayoutList, ChevronDown, ChevronRight, Download } from 'lucide-react'

const API = 'http://localhost:8765'

// ─── CSV renderer ────────────────────────────────────────────────────────────

function parseCsvRow(line) {
  const cells = []
  let cur = ''
  let inQuotes = false
  for (let i = 0; i < line.length; i++) {
    const ch = line[i]
    if (ch === '"') { inQuotes = !inQuotes }
    else if (ch === ',' && !inQuotes) { cells.push(cur.trim()); cur = '' }
    else { cur += ch }
  }
  cells.push(cur.trim())
  return cells
}

function ResizableHeader({ name }) {
  const [width, setWidth] = useState(150)
  const isResizing = useRef(false)
  const startX = useRef(0)
  const startW = useRef(0)

  const onPointerDown = (e) => {
    e.preventDefault()
    e.stopPropagation()
    isResizing.current = true
    startX.current = e.clientX
    startW.current = width
    
    const onPointerMove = (eMove) => {
      if (!isResizing.current) return
      const diff = eMove.clientX - startX.current
      setWidth(Math.max(40, startW.current + diff))
    }
    
    const onPointerUp = () => {
      isResizing.current = false
      document.removeEventListener('pointermove', onPointerMove)
      document.removeEventListener('pointerup', onPointerUp)
      document.body.style.cursor = ''
    }
    
    document.addEventListener('pointermove', onPointerMove)
    document.addEventListener('pointerup', onPointerUp)
    document.body.style.cursor = 'col-resize'
  }

  return (
    <th 
      className="bg-[#f8f9fa] border border-[#dee2e6] text-[#212529] px-3 py-1.5 font-semibold text-left whitespace-nowrap shadow-[0_1px_0_#dee2e6] relative align-middle group"
      style={{ width, minWidth: width, maxWidth: width }}
    >
      <div className="overflow-hidden text-ellipsis select-none">{name}</div>
      <div
        onPointerDown={onPointerDown}
        className="absolute right-0 top-0 bottom-0 w-2 cursor-col-resize hover:bg-blue-400 z-10 touch-none opacity-0 group-hover:opacity-100 transition-opacity"
        style={{ transform: 'translateX(50%)' }}
      />
    </th>
  )
}

function CsvViewer({ text }) {
  const lines = text.split('\n').filter(l => l.trim())
  if (!lines.length) return <p className="text-gray-500 text-xs font-mono p-4">Empty file</p>

  const headers = parseCsvRow(lines[0])
  const rows = lines.slice(1).map(parseCsvRow)

  return (
    <div className="overflow-auto h-full bg-white text-black p-4 custom-scrollbar">
      <table className="w-max min-w-full text-[13px] font-sans border-collapse select-text bg-white shadow-sm">
        <thead className="sticky top-0 z-10">
          <tr>
            <th className="bg-[#f8f9fa] border border-[#dee2e6] text-[#495057] px-2 py-1.5 font-normal w-12 text-center select-none shadow-[0_1px_0_#dee2e6]">
              
            </th>
            {headers.map((h, i) => (
              <ResizableHeader key={i} name={h} />
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri} className="hover:bg-[#f1f3f5] transition-colors group">
              <td className="bg-[#f8f9fa] border border-[#dee2e6] text-[#adb5bd] px-2 py-1.5 text-center select-none font-mono text-xs group-hover:bg-[#e9ecef] transition-colors">
                {ri + 1}
              </td>
              {headers.map((_, ci) => {
                const val = row[ci] ?? ''
                return (
                  <td key={ci} className="border border-[#dee2e6] px-3 py-1.5 whitespace-nowrap text-[#212529] overflow-hidden text-ellipsis max-w-0" title={val}>
                    {val}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ─── Python / code renderer ──────────────────────────────────────────────────

const PY_KEYWORDS = /\b(def|class|import|from|return|if|else|elif|for|while|with|as|in|not|and|or|True|False|None|pass|raise|try|except|finally|yield|lambda|assert|del|global|nonlocal|async|await)\b/g
const PY_DECORATOR = /(@[\w.]+)/g
const PY_STRING = /("""[\s\S]*?"""|'''[\s\S]*?'''|"[^"\n]*"|'[^'\n]*')/g
const PY_COMMENT = /(#.*$)/gm
const PY_NUMBER = /\b(\d+\.?\d*)\b/g

function highlightPython(code) {
  // Escape HTML first
  let s = code
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // Order matters — strings and comments first to avoid re-highlighting their contents
  const segments = []
  let last = 0

  // We'll use a simple line-by-line approach for comments and then token for the rest
  const lines = s.split('\n').map(line => {
    // Comment
    line = line.replace(/(#.*)$/, '<span class="text-gray-500 italic">$1</span>')
    // Decorators
    line = line.replace(/(@[\w.]+)/g, '<span class="text-yellow-400">$1</span>')
    // Strings (simple — won't handle multiline perfectly but good enough)
    line = line.replace(/(&quot;[^&]*&quot;|&#39;[^&]*&#39;)/g, '<span class="text-amber-300">$1</span>')
    // Keywords
    line = line.replace(/\b(def|class|import|from|return|if|else|elif|for|while|with|as|in|not|and|or|True|False|None|pass|raise|try|except|finally|yield|lambda|assert|del|global|nonlocal|async|await)\b/g,
      '<span class="text-purple-400">$1</span>')
    // Numbers
    line = line.replace(/\b(\d+\.?\d*)\b/g, '<span class="text-cyan-300">$1</span>')
    return line
  })

  return lines.join('\n')
}

function CodeViewer({ text, language = 'python' }) {
  const lines = text.split('\n')
  const html = language === 'python' ? highlightPython(text) : text
  const htmlLines = html.split('\n')

  return (
    <div className="overflow-auto h-full flex">
      {/* Line numbers */}
      <div className="select-none shrink-0 text-right pr-4 py-4 pl-4 text-gray-600 text-xs font-mono leading-5 bg-gray-900/50 border-r border-gray-800">
        {lines.map((_, i) => (
          <div key={i}>{i + 1}</div>
        ))}
      </div>
      {/* Code */}
      <pre
        className="flex-1 text-xs font-mono leading-5 p-4 text-gray-300 overflow-x-auto"
        dangerouslySetInnerHTML={{ __html: htmlLines.join('\n') }}
      />
    </div>
  )
}

// ─── JSON renderer ────────────────────────────────────────────────────────────

function JsonViewer({ text }) {
  try {
    const parsed = JSON.parse(text)
    const pretty = JSON.stringify(parsed, null, 2)
    return <CodeViewer text={pretty} language="json" />
  } catch {
    return <CodeViewer text={text} language="text" />
  }
}

// ─── Markdown renderer (simple) ───────────────────────────────────────────────

function MarkdownViewer({ text }) {
  // Very simple md → html: headings, bold, code, horizontal rule
  const html = text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/^#{3} (.+)$/gm, '<h3 class="text-cyan-400 font-bold mt-4 mb-1 text-sm">$1</h3>')
    .replace(/^#{2} (.+)$/gm, '<h2 class="text-brand-cyan font-bold mt-5 mb-2 text-base">$1</h2>')
    .replace(/^# (.+)$/gm,    '<h1 class="text-white font-bold mt-6 mb-2 text-lg">$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>')
    .replace(/`([^`]+)`/g,     '<code class="bg-gray-800 px-1 rounded text-amber-300 text-[11px]">$1</code>')
    .replace(/^---$/gm,        '<hr class="border-gray-700 my-3"/>')
    .replace(/^- (.+)$/gm,     '<li class="ml-4 text-gray-300 list-disc">$1</li>')
    .replace(/\n/g, '<br/>')

  return (
    <div
      className="p-5 text-gray-300 text-xs font-mono leading-relaxed overflow-auto h-full"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}

// ─── Test Cases card viewer ───────────────────────────────────────────────────

function parseTestCases(csvText) {
  const lines = csvText.split('\n').filter(l => l.trim())
  if (lines.length < 2) return []
  const rows = lines.slice(1).map(parseCsvRow)
  const cases = []
  let current = null
  for (const row of rows) {
    const [tcNum, ac, type, priority, scenario, preConditions, testData, step, expected, , , layer] = row
    if (tcNum?.trim()) {
      current = {
        id: tcNum.trim(),
        ac: ac?.trim() || '',
        type: type?.trim() || '',
        priority: priority?.trim() || '',
        scenario: scenario?.trim() || '',
        preConditions: preConditions?.trim() || '',
        testData: testData?.trim() || '',
        layer: layer?.trim() || 'UI',
        steps: [],
      }
      if (step?.trim()) current.steps.push({ step: step.trim(), expected: expected?.trim() || '' })
      cases.push(current)
    } else if (current && step?.trim()) {
      current.steps.push({ step: step.trim(), expected: expected?.trim() || '' })
    }
  }
  return cases
}

const TYPE_BADGE = {
  'Happy Path': 'bg-emerald-900/50 text-emerald-300 border-emerald-700/50',
  'Negative':   'bg-red-900/50    text-red-300    border-red-700/50',
  'Edge Case':  'bg-amber-900/50  text-amber-300  border-amber-700/50',
  'RBAC':       'bg-purple-900/50 text-purple-300 border-purple-700/50',
  'API':        'bg-blue-900/50   text-blue-300   border-blue-700/50',
}
const PRIORITY_BADGE = {
  'High':   'bg-red-900/40    text-red-300    border-red-700/40',
  'Medium': 'bg-amber-900/40  text-amber-300  border-amber-700/40',
  'Low':    'bg-gray-800      text-gray-400   border-gray-700',
}

function TestCaseCard({ tc, defaultOpen }) {
  const [open, setOpen] = useState(defaultOpen)
  const typeCls     = TYPE_BADGE[tc.type]     || 'bg-gray-800 text-gray-400 border-gray-700'
  const priorityCls = PRIORITY_BADGE[tc.priority] || 'bg-gray-800 text-gray-400 border-gray-700'

  return (
    <div className="border border-gray-700/60 rounded-lg bg-gray-900/60 overflow-hidden">
      {/* Card header — always visible */}
      <button
        className="w-full flex items-center gap-2.5 px-4 py-3 hover:bg-white/[0.03] transition-colors text-left"
        onClick={() => setOpen(o => !o)}
      >
        <span className="shrink-0 text-gray-600">
          {open ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
        </span>
        <span className="font-mono text-[11px] text-cyan-400 bg-cyan-900/20 border border-cyan-700/40 px-2 py-0.5 rounded shrink-0">
          TC-{tc.id}
        </span>
        <span className={`text-[10px] font-mono border px-2 py-0.5 rounded shrink-0 ${typeCls}`}>
          {tc.type.toUpperCase()}
        </span>
        <span className={`text-[10px] font-mono border px-2 py-0.5 rounded shrink-0 ${priorityCls}`}>
          {tc.priority.toUpperCase()}
        </span>
        <span className="text-gray-200 text-xs font-mono truncate flex-1">{tc.scenario}</span>
        <span className="text-[10px] text-gray-600 font-mono shrink-0">{tc.ac}</span>
      </button>

      {/* Expanded body */}
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="body"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.18 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-3 border-t border-gray-800">
              {tc.preConditions && (
                <div className="pt-3">
                  <div className="text-[10px] text-gray-500 font-mono uppercase tracking-wider mb-1.5">Pre-conditions</div>
                  <div className="text-xs text-gray-300 font-mono pl-3 border-l-2 border-gray-700">{tc.preConditions}</div>
                </div>
              )}
              {tc.testData && tc.testData !== 'N/A' && (
                <div>
                  <div className="text-[10px] text-gray-500 font-mono uppercase tracking-wider mb-1.5">Test Data</div>
                  <div className="text-xs text-gray-300 font-mono pl-3 border-l-2 border-gray-700">{tc.testData}</div>
                </div>
              )}
              {tc.steps.length > 0 && (
                <div>
                  <div className="text-[10px] text-gray-500 font-mono uppercase tracking-wider mb-1.5">Test Steps</div>
                  <div className="space-y-1 pl-3 border-l-2 border-cyan-900/60">
                    {tc.steps.map((s, i) => (
                      <div key={i} className="text-xs text-gray-300 font-mono">{s.step}</div>
                    ))}
                  </div>
                </div>
              )}
              {tc.steps.some(s => s.expected) && (
                <div>
                  <div className="text-[10px] text-gray-500 font-mono uppercase tracking-wider mb-1.5">Expected Result</div>
                  <div className="space-y-1 pl-3 border-l-2 border-emerald-900/60">
                    {tc.steps.filter(s => s.expected).map((s, i) => (
                      <div key={i} className="text-xs text-gray-300 font-mono">{s.expected}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

function TestCaseCardsViewer({ csvText }) {
  const cases = parseTestCases(csvText)
  if (!cases.length) return <p className="text-gray-500 text-xs font-mono p-6">No test cases found.</p>

  // Group by AC
  const groups = {}
  for (const tc of cases) {
    const key = tc.ac || 'Other'
    if (!groups[key]) groups[key] = []
    groups[key].push(tc)
  }

  return (
    <div className="overflow-auto h-full p-5 space-y-6">
      {Object.entries(groups).map(([ac, tcs]) => (
        <div key={ac}>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-[11px] font-mono text-gray-400 bg-gray-800 border border-gray-700 px-2.5 py-1 rounded-md">{ac}</span>
            <span className="text-[10px] text-gray-600 font-mono">{tcs.length} cases</span>
          </div>
          <div className="space-y-2">
            {tcs.map((tc, i) => (
              <TestCaseCard key={tc.id} tc={tc} defaultOpen={i === 0} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

const TABS = [
  { id: 'cards',    label: 'Cards',    icon: LayoutList },
  { id: 'table',    label: 'Table',    icon: Table      },
  { id: 'markdown', label: 'Markdown', icon: FileText   },
]

function TestCasesViewer({ csvPath, mdPath }) {
  const [tab, setTab]         = useState('cards')
  const [csvText, setCsvText] = useState(null)
  const [mdText, setMdText]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  // Fetch whichever file the current tab needs
  useEffect(() => {
    const needsCsv = tab === 'cards' || tab === 'table'
    const needsMd  = tab === 'markdown'

    if (needsCsv && csvPath && !csvText) {
      setLoading(true); setError(null)
      fetch(`${API}/artifact?path=${encodeURIComponent(csvPath)}`)
        .then(r => { if (!r.ok) throw new Error(`${r.status}`); return r.text() })
        .then(t => { setCsvText(t); setLoading(false) })
        .catch(e => { setError(e.message); setLoading(false) })
    } else if (needsMd && mdPath && !mdText) {
      setLoading(true); setError(null)
      fetch(`${API}/artifact?path=${encodeURIComponent(mdPath)}`)
        .then(r => { if (!r.ok) throw new Error(`${r.status}`); return r.text() })
        .then(t => { setMdText(t); setLoading(false) })
        .catch(e => { setError(e.message); setLoading(false) })
    }
  }, [tab, csvPath, mdPath])

  const currentLoading = loading && (
    (tab !== 'markdown' && !csvText) || (tab === 'markdown' && !mdText)
  )

  const renderTab = () => {
    if (currentLoading) return (
      <div className="flex items-center justify-center h-full">
        <motion.div
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="text-cyan-400 font-mono text-sm"
        >Loading...</motion.div>
      </div>
    )
    if (error) return (
      <div className="flex items-center justify-center h-full">
        <p className="text-red-400 font-mono text-sm">✗ {error}</p>
      </div>
    )
    if (tab === 'cards')    return csvText ? <TestCaseCardsViewer csvText={csvText} /> : null
    if (tab === 'table')    return csvText ? <CsvViewer text={csvText} /> : null
    if (tab === 'markdown') return mdText  ? <MarkdownViewer text={mdText} /> : null
  }

  const caseCount = csvText ? parseTestCases(csvText).length : null

  return (
    <div className="flex flex-col h-full">
      {/* Tab bar */}
      <div className="flex items-center gap-1 px-5 pt-3 pb-0 border-b border-gray-800 shrink-0">
        {TABS.map(t => {
          const Icon = t.icon
          const active = tab === t.id
          return (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={[
                'flex items-center gap-1.5 px-3 py-2 text-xs font-mono rounded-t-md border-b-2 transition-all',
                active
                  ? 'text-cyan-400 border-cyan-500 bg-cyan-900/10'
                  : 'text-gray-500 border-transparent hover:text-gray-300 hover:border-gray-600',
              ].join(' ')}
            >
              <Icon className="w-3.5 h-3.5" />
              {t.label}
              {t.id === 'cards' && caseCount !== null && (
                <span className="text-[9px] bg-cyan-900/40 text-cyan-500 border border-cyan-800/50 px-1.5 py-0.5 rounded-full ml-0.5">
                  {caseCount}
                </span>
              )}
            </button>
          )
        })}
      </div>
      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {renderTab()}
      </div>
    </div>
  )
}

// ─── Main viewer component ────────────────────────────────────────────────────

const TYPE_LABELS = { csv: 'CSV', python: 'Python', json: 'JSON', markdown: 'Markdown', testcases: 'Test Cases' }

export function ArtifactViewer({ artifact, onClose }) {
  const [content, setContent] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!artifact) return
    // testcases and report types manage their own data fetching
    if (artifact.type === 'testcases' || artifact.type === 'html' || artifact.type === 'report') {
      setContent('delegated')
      setLoading(false)
      setError(null)
      return
    }
    setLoading(true)
    setError(null)
    setContent(null)
    fetch(`${API}/artifact?path=${encodeURIComponent(artifact.path)}`)
      .then(r => {
        if (!r.ok) throw new Error(`${r.status} ${r.statusText}`)
        return r.text()
      })
      .then(text => { setContent(text); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [artifact?.path, artifact?.csvPath])

  const renderContent = () => {
    if (loading) return (
      <div className="flex items-center justify-center h-full">
        <motion.div
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="text-brand-cyan font-mono text-sm"
        >
          Loading {artifact?.label}...
        </motion.div>
      </div>
    )
    if (error) return (
      <div className="flex items-center justify-center h-full">
        <p className="text-red-400 font-mono text-sm">✗ {error}</p>
      </div>
    )
    if (!content) return null

    switch (artifact.type) {
      case 'testcases': return <TestCasesViewer csvPath={artifact.csvPath} mdPath={artifact.mdPath} />
      case 'csv':       return <CsvViewer text={content} />
      case 'python':    return <CodeViewer text={content} language="python" />
      case 'json':      return <JsonViewer text={content} />
      case 'markdown':  return <MarkdownViewer text={content} />
      case 'html':      return <iframe src={`${API}/${artifact.path}`} className="w-full h-full bg-white border-0" title={artifact.label} />
      default:          return <CodeViewer text={content} language="text" />
    }
  }

  // Line/row count badge
  const statsBadge = () => {
    if (!content || content === 'delegated') return null
    const lines = content.split('\n').filter(l => l.trim()).length
    if (artifact.type === 'csv') return `${lines - 1} rows`
    return `${lines} lines`
  }

  return (
    <AnimatePresence>
      {artifact && (
        <motion.div
          key="artifact-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-6 sm:p-8 md:p-12"
          style={{ background: 'rgba(0, 0, 0, 0.75)', backdropFilter: 'blur(8px)' }}
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="w-full h-full max-w-[95vw] lg:max-w-[90vw] xl:max-w-7xl bg-[#111113] border border-white/10 rounded-2xl flex flex-col shadow-2xl overflow-hidden ring-1 ring-white/5"
            onClick={e => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/[0.02] shrink-0">
              <div className="flex items-center gap-3.5 min-w-0">
                <span className="text-gray-400 flex items-center justify-center bg-white/5 p-2 rounded-lg border border-white/5">
                  {artifact.type === 'testcases' ? <LayoutList className="w-5 h-5 text-cyan-400" /> :
                   artifact.type === 'csv'        ? <Table      className="w-5 h-5 text-cyan-400" /> :
                   artifact.type === 'python'     ? <Code2      className="w-5 h-5 text-green-400" /> :
                   artifact.type === 'json'       ? <FileJson   className="w-5 h-5 text-amber-400" /> :
                   artifact.type === 'markdown'   ? <FileText   className="w-5 h-5 text-purple-400" /> :
                   artifact.type === 'html'       ? <PieChart   className="w-5 h-5 text-pink-400" /> :
                   <Folder className="w-5 h-5" />}
                </span>
                <div className="min-w-0">
                  <div className="text-gray-100 font-medium text-base tracking-wide truncate">{artifact.label}</div>
                  <div className="text-gray-500 font-mono text-[11px] truncate mt-0.5">
                    {artifact.type === 'testcases' ? artifact.csvPath : artifact.path}
                  </div>
                </div>
                {content && (
                  <span className="shrink-0 ml-2 text-[10px] font-mono text-gray-400 bg-white/5 border border-white/10 px-2.5 py-1 rounded-md">
                    {statsBadge()}
                  </span>
                )}
              </div>
              {artifact.type === 'testcases' && artifact.csvPath && (
                <button
                  onClick={async () => {
                    const res  = await fetch(`${API}/artifact?path=${encodeURIComponent(artifact.csvPath)}`)
                    const text = await res.text()
                    const url  = URL.createObjectURL(new Blob([text], { type: 'text/csv' }))
                    const a    = Object.assign(document.createElement('a'), {
                      href: url,
                      download: artifact.csvPath.split('/').pop(),
                    })
                    a.click()
                    URL.revokeObjectURL(url)
                  }}
                  className="shrink-0 flex items-center gap-1.5 text-gray-400 hover:text-cyan-400 hover:bg-cyan-900/20 border border-gray-700 hover:border-cyan-700/50 px-3 py-1.5 rounded-lg text-xs font-mono transition-all ml-2"
                >
                  <Download className="w-3.5 h-3.5" />
                  Export CSV
                </button>
              )}
              <button
                onClick={onClose}
                className="shrink-0 text-gray-500 hover:text-white hover:bg-white/10 p-2 rounded-lg transition-colors ml-2"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-hidden relative">
              {renderContent()}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
