import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, Code2, FileJson, Table, Folder, BarChart2, LayoutList } from 'lucide-react'

const SERVER_URL = 'http://localhost:8765'

const TYPE_META = {
  csv:       { icon: Table,      color: 'text-cyan-400',   border: 'border-cyan-700/60',   bg: 'bg-cyan-900/20'   },
  python:    { icon: Code2,      color: 'text-green-400',  border: 'border-green-700/60',  bg: 'bg-green-900/20'  },
  markdown:  { icon: FileText,   color: 'text-purple-400', border: 'border-purple-700/60', bg: 'bg-purple-900/20' },
  json:      { icon: FileJson,   color: 'text-amber-400',  border: 'border-amber-700/60',  bg: 'bg-amber-900/20'  },
  report:    { icon: BarChart2,  color: 'text-rose-400',   border: 'border-rose-700/60',   bg: 'bg-rose-900/20'   },
  testcases: { icon: LayoutList, color: 'text-cyan-400',   border: 'border-cyan-700/60',   bg: 'bg-cyan-900/20'   },
  default:   { icon: Folder,     color: 'text-gray-400',   border: 'border-gray-700',      bg: 'bg-gray-900/20'   },
}

function handleOpen(artifact, onOpen) {
  if (artifact.type === 'report') {
    window.open(`${SERVER_URL}/${artifact.path}/`, '_blank')
  } else {
    onOpen(artifact)
  }
}

function ArtifactPill({ artifact, onOpen }) {
  const meta  = TYPE_META[artifact.type] || TYPE_META.default
  const ready = !!artifact.path
  const Icon  = meta.icon

  return (
    <motion.button
      title={ready ? (artifact.path || artifact.csvPath) : 'Pending...'}
      onClick={() => ready && handleOpen(artifact, onOpen)}
      animate={{ opacity: ready ? 1 : 0.35, scale: ready ? 1 : 0.97 }}
      transition={ready
        ? { type: 'spring', damping: 12, stiffness: 260 }
        : { duration: 0.15 }
      }
      className={[
        'shrink-0 flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-mono',
        'transition-colors duration-200',
        meta.color, meta.border, meta.bg,
        ready ? 'hover:brightness-125 cursor-pointer' : 'cursor-not-allowed pointer-events-none',
      ].join(' ')}
    >
      <Icon className="w-3.5 h-3.5" />
      <span>{artifact.label}</span>
      {!ready && (
        <motion.span
          className="text-[9px] text-gray-600 font-mono"
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 1.8, repeat: Infinity }}
        >
          ···
        </motion.span>
      )}
    </motion.button>
  )
}

export function ArtifactPanel({ artifacts, onOpen }) {
  if (!artifacts.length) return null

  // Consolidate the two test-case artifacts into one synthetic pill
  const csvArt = artifacts.find(a => a.label === 'Test Cases CSV')
  const mdArt  = artifacts.find(a => a.label === 'Test Cases MD')
  const others = artifacts.filter(
    a => a.label !== 'Test Cases CSV' && a.label !== 'Test Cases MD'
  )

  // Synthetic testcases artifact — ready as soon as CSV path exists (cards+table need it)
  const tcArtifact = (csvArt || mdArt) ? {
    label:   'Test Cases',
    type:    'testcases',
    path:    csvArt?.path || null,   // satisfies the ready check in ArtifactPill
    csvPath: csvArt?.path || null,
    mdPath:  mdArt?.path  || null,
  } : null

  const displayArtifacts = [
    ...(tcArtifact ? [tcArtifact] : []),
    ...others,
  ]

  return (
    <div className="border-t border-gray-800 bg-gray-950/60 px-6 py-2 shrink-0">
      <div className="flex items-center gap-3 overflow-x-auto pb-1">
        <span className="text-[10px] text-gray-600 font-mono uppercase tracking-wider shrink-0">
          Artifacts
        </span>
        {displayArtifacts.map((artifact) => (
          <ArtifactPill key={artifact.label} artifact={artifact} onOpen={onOpen} />
        ))}
      </div>
    </div>
  )
}
