import { useState, useEffect, useCallback, useRef } from 'react'
import { EXPECTED_ARTIFACTS, SELF_HEAL_ARTIFACTS } from '../constants/stages.js'

const WS_URL = 'ws://localhost:8765/ws'
const API_URL = 'http://localhost:8765'

export function useWorkflowSocket() {
  const [events, setEvents] = useState([])
  const [stageStatuses, setStageStatuses] = useState({})
  const [activeHitl, setActiveHitl] = useState(null)
  const [connected, setConnected] = useState(false)
  const [workflowActive, setWorkflowActive] = useState(false)
  const [workflowMode, setWorkflowMode] = useState('e2e') // 'e2e' | 'self_heal_webhook' | 'self_heal_skill'
  const [artifacts, setArtifacts] = useState([])
  const [runStatus, setRunStatus] = useState('idle') // 'idle' | 'launching' | 'running' | 'error'
  const [claudeActivities, setClaudeActivities] = useState([]) // ai_activity events
  const [pendingPr, setPendingPr] = useState(null) // {number, title, branch, url} from webhook
  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)

  const handleEvent = useCallback((event) => {
    if (event.type === 'reset') {
      setEvents([])
      setStageStatuses({})
      setActiveHitl(null)
      setWorkflowActive(false)
      setWorkflowMode('e2e')
      setArtifacts([])
      setRunStatus('idle')
      setClaudeActivities([])
      setPendingPr(null)
      return
    }

    // pr_detected is a meta-event — don't add to the log stream or it
    // would flip showLanding to false before the modal can render.
    if (event.type !== 'pr_detected') {
      setEvents(prev => [...prev, event])
    }

    if (event.type === 'workflow_start') {
      const mode = event.data?.mode || 'e2e'
      setWorkflowActive(true)
      setWorkflowMode(mode)
      setStageStatuses({})
      const isSelfHeal = mode === 'self_heal_webhook' || mode === 'self_heal_skill'
      setArtifacts((isSelfHeal ? SELF_HEAL_ARTIFACTS : EXPECTED_ARTIFACTS).map(a => ({ ...a, path: null })))
      setRunStatus('running')
      setClaudeActivities([])
    }

    if (event.type === 'workflow_complete') {
      setWorkflowActive(false)
      setRunStatus('idle')
    }

    if (event.type === 'stage_start' && event.stage) {
      setStageStatuses(prev => ({ ...prev, [event.stage]: 'active' }))
    }

    if (event.type === 'stage_complete' && event.stage) {
      setStageStatuses(prev => {
        const next = { ...prev, [event.stage]: 'complete' }
        // If regression passes cleanly, skip all heal stages — nothing to fix
        if (event.stage === 'run_regression') {
          const failed = parseInt(event.data?.failed ?? '1', 10)
          if (failed === 0) {
            next.inspect_dom   = 'skipped'
            next.apply_heal    = 'skipped'
            next.verify_heal   = 'skipped'
            next.raise_heal_pr = 'skipped'
          }
        }
        // If the test run passed cleanly, there's no bug to log — skip the defect stage
        if (event.stage === 'run_tests') {
          const failed = parseInt(event.data?.failed ?? '0', 10)
          if (failed === 0) {
            next.jira_defects = 'skipped'
          }
        }
        return next
      })
      if (event.data?.artifacts?.length) {
        const incoming = event.data.artifacts
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

    if (event.type === 'pr_detected' && event.data?.pr_number) {
      setPendingPr({
        number: event.data.pr_number,
        title:  event.data.pr_title  || 'Unknown PR',
        branch: event.data.pr_branch || 'unknown-branch',
        url:    event.data.pr_url    || '',
      })
    }

    // Claude activity stream — any workflow can emit these
    if (event.type === 'ai_activity' && event.data?.content) {
      setClaudeActivities(prev => [...prev, {
        phase:      event.data.phase || 'response',
        content:    event.data.content,
        model:      event.data.model || null,
        tokens:     event.data.tokens || null,
        elapsed_ms: event.data.elapsed_ms || null,
        ts:         event.timestamp,
      }])
    }
  }, [])

  const connect = useCallback(() => {
    const state = wsRef.current?.readyState
    if (state === WebSocket.OPEN || state === WebSocket.CONNECTING) return

    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      if (wsRef.current !== ws) return   // stale — a newer socket took over
      setConnected(true)
      clearTimeout(reconnectTimer.current)
    }

    ws.onmessage = (e) => {
      if (wsRef.current !== ws) return   // stale
      try { handleEvent(JSON.parse(e.data)) } catch {}
    }

    ws.onclose = () => {
      if (wsRef.current !== ws) return   // stale — don't schedule reconnect
      setConnected(false)
      reconnectTimer.current = setTimeout(connect, 2000)
    }

    ws.onerror = () => ws.close()
  }, [handleEvent])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimer.current)
      const ws = wsRef.current
      wsRef.current = null               // mark current socket as stale
      // Only close OPEN sockets — closing a CONNECTING socket produces
      // "closed before connection established" in React StrictMode dev mode.
      // Stale-ref checks in the handlers above prevent any action from it.
      if (ws?.readyState === WebSocket.OPEN) ws.close()
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

  /**
   * Trigger a mock workflow run from the landing page.
   * mode: 'e2e' | 'self_heal'  (resolved to self_heal_webhook/self_heal_skill internally)
   * prData: optional { number, title, branch, url } for webhook-sourced PR
   */
  const triggerWorkflow = useCallback(async (mode, prData = null) => {
    const endpoint = mode === 'self_heal' ? '/run/self-heal' : '/run/e2e'
    // Set mode + seed artifacts immediately so Pipeline renders before workflow_start WS arrives
    const resolvedMode = mode === 'self_heal'
      ? (prData ? 'self_heal_webhook' : 'self_heal_skill')
      : 'e2e'
    setWorkflowMode(resolvedMode)
    const isSelfHeal = resolvedMode === 'self_heal_webhook' || resolvedMode === 'self_heal_skill'
    setArtifacts((isSelfHeal ? SELF_HEAL_ARTIFACTS : EXPECTED_ARTIFACTS)
      .map(a => ({ ...a, path: null })))
    setRunStatus('launching')
    // Normalise pendingPr shape {number,title,branch,url} → server shape {pr_number,...}
    const body = prData ? {
      pr_number: prData.number || prData.pr_number || null,
      pr_title:  prData.title  || prData.pr_title  || null,
      pr_branch: prData.branch || prData.pr_branch || null,
      pr_url:    prData.url    || prData.pr_url    || null,
    } : null
    try {
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        ...(body && {
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `Failed to start ${mode} workflow`)
      }
      // runStatus flips to 'running' once workflow_start event arrives via WS
    } catch (err) {
      setRunStatus('error')
      setTimeout(() => setRunStatus('idle'), 3000)
      throw err
    }
  }, [])

  const dismissPr = useCallback(() => setPendingPr(null), [])

  // claudeIsActive = the last activity is a 'thinking' phase (still processing)
  const claudeIsActive = claudeActivities.length > 0 &&
    claudeActivities[claudeActivities.length - 1]?.phase === 'thinking'

  return {
    events, stageStatuses, activeHitl, connected,
    workflowActive, workflowMode, artifacts, runStatus,
    claudeActivities, claudeIsActive,
    pendingPr, dismissPr,
    respondToHitl, resetWorkflow, sendTeamsUpdate, triggerWorkflow,
  }
}
