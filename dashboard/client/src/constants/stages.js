export const STAGES = [
  { id: 'jira_fetch',         label: 'Fetch Ticket',   icon: '🎫', color: '#a855f7' },
  { id: 'branch_create',      label: 'Create Branch',  icon: '🌿', color: '#22c55e' },
  { id: 'swagger_discovery',  label: 'API Discovery',  icon: '🔍', color: '#3b82f6' },
  { id: 'test_cases',         label: 'Test Cases',     icon: '📋', color: '#06b6d4' },
  { id: 'generate_tests',     label: 'Generate Tests', icon: '⚙️',  color: '#f59e0b' },
  { id: 'run_tests',          label: 'Run Tests',      icon: '🧪', color: '#ef4444' },
  { id: 'postman_export',     label: 'Postman Export', icon: '📮', color: '#f97316' },
  { id: 'commit_push',        label: 'Commit & Push',  icon: '📦', color: '#8b5cf6' },
  { id: 'raise_pr',           label: 'Raise PR',       icon: '🔀', color: '#ec4899' },
  { id: 'update_jira',        label: 'Update Jira',    icon: '✅', color: '#10b981' },
  { id: 'pr_review',          label: 'PR Review',      icon: '🔎', color: '#6366f1' },
]

export const SELF_HEAL_STAGES = [
  { id: 'baseline_run',   label: 'Baseline Run',   icon: '🟢', color: '#22c55e' },
  { id: 'inject_decay',   label: 'Inject Decay',   icon: '💉', color: '#ef4444' },
  { id: 'detect_failure', label: 'Detect Failure', icon: '🔥', color: '#f97316' },
  { id: 'inspect_dom',    label: 'Inspect DOM',    icon: '🔬', color: '#3b82f6' },
  { id: 'apply_heal',     label: 'Apply Fix',      icon: '🩹', color: '#a855f7' },
  { id: 'verify_heal',    label: 'Verify Heal',    icon: '✅', color: '#10b981' },
]

export const STAGE_STATUS = {
  IDLE: 'idle',
  ACTIVE: 'active',
  COMPLETE: 'complete',
  ERROR: 'error',
  SKIPPED: 'skipped',
}

export const LEVEL_COLORS = {
  info:    'text-gray-300',
  success: 'text-emerald-400',
  warning: 'text-amber-400',
  error:   'text-red-400',
}

export const LEVEL_PREFIXES = {
  info:    '  ',
  success: '✓ ',
  warning: '⚠ ',
  error:   '✗ ',
}

// Artifacts for the standard e2e workflow
export const EXPECTED_ARTIFACTS = [
  { label: 'Test Cases CSV',     type: 'csv',      stage: 'test_cases',     path: null },
  { label: 'Test Cases MD',      type: 'markdown', stage: 'test_cases',     path: null },
  { label: 'UI Tests',           type: 'python',   stage: 'generate_tests', path: null },
  { label: 'API Tests',          type: 'python',   stage: 'generate_tests', path: null },
  { label: 'Allure Report',      type: 'report',   stage: 'run_tests',      path: null },
  { label: 'Postman Collection', type: 'json',     stage: 'postman_export', path: null },
  { label: 'Run Summary',        type: 'markdown', stage: 'pr_review',      path: null },
]

// Artifacts for the self-heal demo workflow
export const SELF_HEAL_ARTIFACTS = [
  { label: 'Regression Report', type: 'report',   stage: 'verify_heal', path: null },
  { label: 'Heal Summary',      type: 'markdown', stage: 'verify_heal', path: null },
]
