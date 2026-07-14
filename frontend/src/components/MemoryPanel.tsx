import { useState, useEffect, useCallback } from 'react'
import { Brain, Search, Clock, Trash2, BookOpen, Loader2 } from 'lucide-react'
import { memoryService, type MemoryItem } from '../services/memory'
import { formatDate } from '../utils/format'

export default function MemoryPanel() {
  const [memories, setMemories] = useState<MemoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<MemoryItem[] | null>(null)
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadRecent = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const items = await memoryService.getRecent(20)
      setMemories(items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load memories')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadRecent() }, [loadRecent])

  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    setSearching(true)
    setError(null)
    try {
      const results = await memoryService.search(searchQuery, 10)
      setSearchResults(results)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setSearching(false)
    }
  }

  const handleDelete = async (key: string) => {
    try {
      await memoryService.delete(key)
      setMemories(prev => prev.filter(m => m.key !== key))
      if (searchResults) {
        setSearchResults(prev => prev?.filter(m => m.key !== key) ?? null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  const handleClearSearch = () => {
    setSearchQuery('')
    setSearchResults(null)
  }

  const displayMemories = searchResults ?? memories

  return (
    <div className="memory-panel">
      <div className="memory-header">
        <div className="memory-title">
          <Brain size={18} />
          <span>Memory</span>
        </div>
        <button className="memory-refresh" onClick={loadRecent} title="Refresh">
          <Clock size={14} />
        </button>
      </div>

      <div className="memory-search">
        <div className="memory-search-input">
          <Search size={14} />
          <input
            type="text"
            placeholder="Search memories..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
          />
          {searchResults && (
            <button className="memory-clear-search" onClick={handleClearSearch} title="Clear search">
              &times;
            </button>
          )}
        </div>
        <button className="memory-search-btn" onClick={handleSearch} disabled={searching || !searchQuery.trim()}>
          {searching ? <Loader2 size={14} className="spin" /> : 'Go'}
        </button>
      </div>

      {error && <div className="memory-error">{error}</div>}

      <div className="memory-list">
        {loading ? (
          <div className="memory-loading">
            <Loader2 size={20} className="spin" />
            <span>Loading memories...</span>
          </div>
        ) : displayMemories.length === 0 ? (
          <div className="memory-empty">
            <BookOpen size={24} />
            <span>{searchResults ? 'No results found' : 'No memories yet'}</span>
          </div>
        ) : (
          displayMemories.map(mem => (
            <div key={mem.key} className="memory-item">
              <div className="memory-item-content">
                <div className="memory-item-text">
                  {mem.text || mem.value || mem.key}
                </div>
                {(mem.agent_name || mem.created_at) && (
                  <div className="memory-item-meta">
                    {mem.agent_name && <span className="memory-agent">{mem.agent_name}</span>}
                    {mem.score !== undefined && (
                      <span className="memory-score">{(mem.score * 100).toFixed(0)}%</span>
                    )}
                    {mem.created_at && <span>{formatDate(mem.created_at)}</span>}
                  </div>
                )}
              </div>
              <button
                className="memory-delete"
                onClick={() => handleDelete(mem.key)}
                title="Delete memory"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
