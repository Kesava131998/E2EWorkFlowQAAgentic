import { useState } from 'react'
import { useWorkflowSocket } from './hooks/useWebSocket.js'
import { Header } from './components/Header.jsx'
import { Pipeline } from './components/Pipeline.jsx'
import { LogStream } from './components/LogStream.jsx'
import { HitlGate } from './components/HitlGate.jsx'
import { StageDetail } from './components/StageDetail.jsx'
import { ArtifactPanel } from './components/ArtifactPanel.jsx'
import { ArtifactViewer } from './components/ArtifactViewer.jsx'

export default function App() {
  const {
    events,
    stageStatuses,
    activeHitl,
    connected,
    workflowActive,
    workflowMode,
    artifacts,
    respondToHitl,
    resetWorkflow,
    sendTeamsUpdate,
  } = useWorkflowSocket()

  const [openArtifact, setOpenArtifact] = useState(null)

  return (
    <div className="h-screen flex bg-gray-950 font-mono overflow-hidden">
        {/* Left Sidebar: Pipeline & Properties Merged */}
        <Pipeline
          stageStatuses={stageStatuses}
          events={events}
          workflowActive={workflowActive}
          workflowMode={workflowMode}
          onReset={resetWorkflow}
          onTeamsNotify={sendTeamsUpdate}
          connected={connected}
        />

      <div className="flex flex-col flex-1 overflow-hidden relative">
        {/* Artifact strip */}
        <ArtifactPanel artifacts={artifacts} onOpen={setOpenArtifact} />

        {/* Main Canvas: Log Stream */}
        <div className="flex-1 overflow-hidden">
          <LogStream events={events} />
        </div>
      </div>

      {/* HITL overlay */}
      <HitlGate checkpoint={activeHitl} onRespond={respondToHitl} onOpenArtifact={setOpenArtifact} />

      {/* Artifact drawer */}
      <ArtifactViewer artifact={openArtifact} onClose={() => setOpenArtifact(null)} />
    </div>
  )
}
