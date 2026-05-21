import { motion } from 'framer-motion'

export const InnocitoLogo = () => (
  <div className="flex items-center gap-3 shrink-0">
    <svg viewBox="0 0 60 60" className="w-10 h-10 drop-shadow-md" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Outer Hexagon */}
      <path d="M 14 20 L 30 10.5 L 46 20" stroke="#FCC837" strokeWidth="5.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M 10.5 24 L 10.5 41 L 26.5 50.5" stroke="#F63B5D" strokeWidth="5.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M 49.5 24 L 49.5 41 L 33.5 50.5" stroke="#3BB273" strokeWidth="5.5" strokeLinecap="round" strokeLinejoin="round" />
      
      {/* Inner Cube */}
      <path d="M 30 31 L 36 27.5 L 30 24 L 24 27.5 Z" fill="#FCC837" />
      <path d="M 30 31 L 36 27.5 L 36 34.5 L 30 38 Z" fill="#3BB273" />
      <path d="M 30 31 L 24 27.5 L 24 34.5 L 30 38 Z" fill="#F63B5D" />
    </svg>
    <div className="flex flex-col justify-center">
      <div className="text-gray-100 text-lg font-bold tracking-tight leading-none mb-0.5">
        Innocito
      </div>
      <div className="text-gray-500 text-[8px] font-semibold tracking-[0.15em] uppercase">
        Ideate. Incubate. Scale.
      </div>
    </div>
  </div>
)

export const StatusControls = ({ workflowActive }) => {
  if (!workflowActive) return null
  
  return (
    <div className="flex items-center gap-4 shrink-0">
      <div className="flex items-center gap-2 text-brand-primary text-xs font-medium px-2 py-1 rounded-full bg-brand-primary/10 border border-brand-primary/20">
        <span className="w-1.5 h-1.5 rounded-full bg-brand-primary animate-pulse" />
        LIVE
      </div>
    </div>
  )
}

// Keeping a dummy Header export so imports in App.jsx don't immediately break before we update App.jsx
export function Header() {
  return null
}
