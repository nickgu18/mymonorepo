import re

# ConfigurationInterface.tsx
with open('projects/bench-hub/web-ui/src/components/ConfigurationInterface.tsx', 'r') as f:
    data = f.read()
data = data.replace('value={config.dataset || \'\'}', 'value={String(config.dataset || \'\')}')
data = data.replace('value={config.model || \'\'}', 'value={String(config.model || \'\')}')
data = data.replace('<li>User: {config.hub_user}</li>', '<li>User: {String(config.hub_user || \'\')}</li>')
with open('projects/bench-hub/web-ui/src/components/ConfigurationInterface.tsx', 'w') as f:
    f.write(data)

# RunBrowser.tsx
with open('projects/bench-hub/web-ui/src/components/RunBrowser.tsx', 'r') as f:
    data = f.read()
data = data.replace('if (aValue < bValue)', 'if ((aValue as number) < (bValue as number))')
data = data.replace('if (aValue > bValue)', 'if ((aValue as number) > (bValue as number))')
with open('projects/bench-hub/web-ui/src/components/RunBrowser.tsx', 'w') as f:
    f.write(data)

# RunSummary.test.tsx
with open('projects/bench-hub/web-ui/src/components/RunSummary.test.tsx', 'r') as f:
    data = f.read()
data = data.replace('import { vi } from \'vitest\';', 'import { vi, describe, it, expect, beforeEach, afterEach } from \'vitest\';')
data = data.replace('async (status) =>', 'async (status: string) =>')
with open('projects/bench-hub/web-ui/src/components/RunSummary.test.tsx', 'w') as f:
    f.write(data)

