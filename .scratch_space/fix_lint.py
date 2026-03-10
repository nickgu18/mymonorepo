import re

# App.test.tsx
with open('projects/bench-hub/web-ui/src/App.test.tsx', 'r') as f:
    data = f.read()
data = data.replace('} as any);', '} as unknown as Response);')
with open('projects/bench-hub/web-ui/src/App.test.tsx', 'w') as f:
    f.write(data)

# App.tsx
with open('projects/bench-hub/web-ui/src/App.tsx', 'r') as f:
    data = f.read()
data = data.replace('return tab as any;', "return tab as 'new' | 'browse' | 'summary' | 'trajectory';")
data = data.replace('useState<any>({', 'useState<Record<string, unknown>>({')
data = data.replace('const handleSelectInstance = (instanceId: string) => {\n    setSelectedInstanceId(instanceId);\n    setActiveTab(\'trajectory\');\n  };\n\n  ', '')
data = data.replace('const handleLaunchSuccess = (jobId: string) => {', 'const handleLaunchSuccess = (_jobId: string) => {')
with open('projects/bench-hub/web-ui/src/App.tsx', 'w') as f:
    f.write(data)

# ConfigurationInterface.tsx
with open('projects/bench-hub/web-ui/src/components/ConfigurationInterface.tsx', 'r') as f:
    data = f.read()
data = data.replace('(config: any)', '(config: Record<string, unknown>)')
data = data.replace('config: any;', 'config: Record<string, unknown>;')
data = data.replace('a: any, b: any', 'a: Dataset, b: Dataset')
data = data.replace('}, []);', '  // eslint-disable-next-line react-hooks/exhaustive-deps\n  }, []);')
with open('projects/bench-hub/web-ui/src/components/ConfigurationInterface.tsx', 'w') as f:
    f.write(data)

# RunBrowser.tsx
with open('projects/bench-hub/web-ui/src/components/RunBrowser.tsx', 'r') as f:
    data = f.read()
data = data.replace('(run: any)', '(run: Record<string, unknown>)')
data = data.replace('let aValue: any;', 'let aValue: unknown;')
data = data.replace('let bValue: any;', 'let bValue: unknown;')
data = data.replace('catch (e) {', 'catch (_e) {')
with open('projects/bench-hub/web-ui/src/components/RunBrowser.tsx', 'w') as f:
    f.write(data)

# RunLauncher.tsx
with open('projects/bench-hub/web-ui/src/components/RunLauncher.tsx', 'r') as f:
    data = f.read()
data = data.replace('config: any;', 'config: Record<string, unknown>;')
with open('projects/bench-hub/web-ui/src/components/RunLauncher.tsx', 'w') as f:
    f.write(data)

# RunSummary.test.tsx
with open('projects/bench-hub/web-ui/src/components/RunSummary.test.tsx', 'r') as f:
    data = f.read()
data = data.replace('vi.fn() as any', 'vi.fn() as unknown as typeof fetch')
data = data.replace('(global.fetch as any)', '(global.fetch as unknown as ReturnType<typeof vi.fn>)')
with open('projects/bench-hub/web-ui/src/components/RunSummary.test.tsx', 'w') as f:
    f.write(data)

# RunSummary.tsx
with open('projects/bench-hub/web-ui/src/components/RunSummary.tsx', 'r') as f:
    data = f.read()
data = data.replace('}, [jobId]);', '  // eslint-disable-next-line react-hooks/exhaustive-deps\n  }, [jobId]);')
with open('projects/bench-hub/web-ui/src/components/RunSummary.tsx', 'w') as f:
    f.write(data)

