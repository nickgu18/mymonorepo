import re

with open("projects/bench-hub/.factory/bug-490147352/web-ui/src/components/RunBrowser.tsx", "r") as f:
    content = f.read()

# 1. Add hideHeals to filters state
content = content.replace("hideBroken: true // Enabled by default", "hideBroken: true, hideHeals: true")

# 2. Update fetch URL
content = content.replace("const response = await fetch('/api/jobs?limit=100');", "const response = await fetch(`/api/jobs?limit=100&exclude_heals=${filters.hideHeals}`);")

# 3. Update activeFilterCount
content = content.replace("key !== 'hideBroken' && v !== ''", "key !== 'hideBroken' && key !== 'hideHeals' && v !== ''")

# 4. Update clearFilters
content = content.replace("""hideBroken: true
    });""", """hideBroken: true,
      hideHeals: true
    });""")

# 5. Update useEffect dependency
content = content.replace("""  useEffect(() => {
    fetchRuns();
    const interval = setInterval(fetchRuns, 15000);
    return () => clearInterval(interval);
  }, []);""", """  useEffect(() => {
    fetchRuns();
    const interval = setInterval(fetchRuns, 15000);
    return () => clearInterval(interval);
  }, [filters.hideHeals]);""")

# 6. Add checkbox for hideHeals
checkbox_html = """                <label style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '0.5rem', 
                  fontSize: '0.875rem', 
                  cursor: 'pointer',
                  fontWeight: 600,
                  color: '#4a5568'
                }}>
                  <input 
                    type="checkbox" 
                    checked={filters.hideHeals}
                    onChange={e => setFilters(prev => ({ ...prev, hideHeals: e.target.checked }))}
                    style={{ width: '1.1rem', height: '1.1rem', cursor: 'pointer' }}
                  />
                  Hide heal jobs
                </label>
              </div>"""
              
content = content.replace("""              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>""", checkbox_html + "\n            </div>\n            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>")

with open("projects/bench-hub/.factory/bug-490147352/web-ui/src/components/RunBrowser.tsx", "w") as f:
    f.write(content)
