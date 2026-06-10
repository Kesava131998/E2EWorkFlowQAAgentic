import { useState } from 'react'
import { useWorkflowSocket } from './hooks/useWebSocket.js'
import { Landing } from './components/Landing.jsx'
import { Pipeline } from './components/Pipeline.jsx'
import { LogStream } from './components/LogStream.jsx'
import { HitlGate } from './components/HitlGate.jsx'
import { ArtifactPanel } from './components/ArtifactPanel.jsx'
import { ArtifactViewer } from './components/ArtifactViewer.jsx'
import { ClaudePane } from './components/ClaudePane.jsx'

export default function App() {
  const {
    events,
    stageStatuses,
    activeHitl,
    connected,
    workflowActive,
    workflowMode,
    artifacts,
    runStatus,
    claudeActivities,
    claudeIsActive,
    pendingPr,
    dismissPr,
    respondToHitl,
    resetWorkflow,
    sendTeamsUpdate,
    triggerWorkflow,
  } = useWorkflowSocket()

  const [openArtifact, setOpenArtifact] = useState(null)

  // Show landing when idle with no events and no active workflow
  const showLanding = runStatus === 'idle' && events.length === 0 && !workflowActive

  return (
    <>
      {showLanding ? (
        <Landing
          connected={connected}
          onMockRun={triggerWorkflow}
          runStatus={runStatus}
          pendingPr={pendingPr}
          onDismissPr={dismissPr}
        />
      ) : (
        <div className="h-screen flex bg-gray-950 font-mono overflow-hidden">
          {/* Left Sidebar: Pipeline */}
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
      )}

      {/* Claude Activity Pane — floats globally over all views */}
      <ClaudePane
        activities={claudeActivities}
        isActive={claudeIsActive}
      />
    </>
  )
}
