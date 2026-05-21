import { useState, useEffect, useCallback, useRef } from 'react'
import { EXPECTED_ARTIFACTS } from '../constants/stages.js'

const WS_URL = 'ws://localhost:8765/ws'
const API_URL = 'http://localhost:8765'

export function useWorkflowSocket() {
  const [events, setEvents] = useState([])
  const [stageStatuses, setStageStatuses] = useState({})
  const [activeHitl, setActiveHitl] = useState(null)
  const [connected, setConnected] = useState(false)
  const [workflowActive, setWorkflowActive] = useState(false)
  const [artifacts, setArtifacts] = useState([])
  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)

  const handleEvent = useCallback((event) => {
    if (event.type === 'reset') {
      setEvents([])
      setStageStatuses({})
      setActiveHitl(null)
      setWorkflowActive(false)
      setArtifacts([])
      return
    }

    setEvents(prev => [...prev, event])

    if (event.type === 'workflow_start') {
      setWorkflowActive(true)
      setStageStatuses({})
      // Seed all expected artifacts as pending (path: null)
      setArtifacts(EXPECTED_ARTIFACTS.map(a => ({ ...a, path: null })))
    }

    if (event.type === 'workflow_complete') {
      setWorkflowActive(false)
    }

    if (event.type === 'stage_start' && event.stage) {
      setStageStatuses(prev => ({ ...prev, [event.stage]: 'active' }))
    }

    if (event.type === 'stage_complete' && event.stage) {
      setStageStatuses(prev => ({ ...prev, [event.stage]: 'complete' }))
      // Unlock artifacts emitted with this stage (fill in their real path)
      if (event.data?.artifacts?.length) {
        const incoming = event.data.artifacts  // [{label, path, type}, ...]
        setArtifacts(prev => prev.map(a => {
          const match = incoming.find(r => r.label === a.label)
          return match ? { ...a, path: match.path } : a
        }))
      }
    }

    if (event.type === 'stage_error' && event.stage) {
      setStageStatuses(prev => ({ ...prev, [event.stage]: 'error' }))
    }

    if (event.type === 'hitl_checkpoint') {
      setActiveHitl(event)
    }

    if (event.type === 'hitl_response') {
      setActiveHitl(null)
    }
  }, [])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      clearTimeout(reconnectTimer.current)
    }

    ws.onmessage = (e) => {
      try {
        handleEvent(JSON.parse(e.data))
      } catch {}
    }

    ws.onclose = () => {
      setConnected(false)
      reconnectTimer.current = setTimeout(connect, 2000)
    }

    ws.onerror = () => ws.close()
  }, [handleEvent])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [connect])

  const respondToHitl = useCallback(async (checkpointId, choice, feedback = null) => {
    await fetch(`${API_URL}/hitl/${checkpointId}/respond`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ choice, feedback }),
    })
  }, [])

  const resetWorkflow = useCallback(async () => {
    await fetch(`${API_URL}/reset`, { method: 'DELETE' })
  }, [])

  const sendTeamsUpdate = useCallback(async () => {
    const res = await fetch(`${API_URL}/teams/notify`, { method: 'POST' })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Teams notify failed')
    }
    return res.json()
  }, [])

  return { events, stageStatuses, activeHitl, connected, workflowActive, artifacts, respondToHitl, resetWorkflow, sendTeamsUpdate }
}
