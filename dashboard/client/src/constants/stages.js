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

// All artifacts that the workflow may produce, in the order they appear.
// path is null until the stage_complete event provides the real filename.
export const EXPECTED_ARTIFACTS = [
  { label: 'Test Cases CSV',     type: 'csv',      stage: 'test_cases',     path: null },
  { label: 'Test Cases MD',      type: 'markdown', stage: 'test_cases',     path: null },
  { label: 'UI Tests',           type: 'python',   stage: 'generate_tests', path: null },
  { label: 'API Tests',          type: 'python',   stage: 'generate_tests', path: null },
  { label: 'Allure Report',      type: 'report',   stage: 'run_tests',      path: null },
  { label: 'Postman Collection', type: 'json',     stage: 'postman_export', path: null },
  { label: 'Run Summary',        type: 'markdown', stage: 'pr_review',      path: null },
]
