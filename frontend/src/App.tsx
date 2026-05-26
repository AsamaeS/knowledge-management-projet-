import { useEffect, useState } from 'react'
import './App.css'

const API_URL = (import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000').replace(/\/$/, '')

type ChatResponse = {
  answer: string
  sources: string[]
}

function App() {
  const [apiStatus, setApiStatus] = useState('checking')
  const [file, setFile] = useState<File | null>(null)
  const [uploadMessage, setUploadMessage] = useState('')
  const [question, setQuestion] = useState('What is this system?')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState<string[]>([])
  const [graphCount, setGraphCount] = useState(0)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    refreshStatus()
    refreshGraph()
  }, [])

  async function refreshStatus() {
    try {
      const res = await fetch(`${API_URL}/api/health`)
      const data = await res.json()
      setApiStatus(data.status === 'ok' ? 'online' : 'error')
    } catch {
      setApiStatus('offline')
    }
  }

  async function refreshGraph() {
    try {
      const res = await fetch(`${API_URL}/graph/chunks`)
      const data = await res.json()
      setGraphCount(Object.keys(data).length)
    } catch {
      setGraphCount(0)
    }
  }

  async function uploadFile() {
    if (!file) return

    setLoading(true)
    setUploadMessage('')
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_URL}/ingest`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Ingestion failed')
      setUploadMessage(`Indexed ${data.filename}: ${data.chunk_count} chunks`)
      setFile(null)
      await refreshGraph()
    } catch (err) {
      setUploadMessage(err instanceof Error ? err.message : 'Ingestion failed')
    } finally {
      setLoading(false)
    }
  }

  async function askQuestion() {
    if (!question.trim()) return

    setLoading(true)
    setAnswer('')
    setSources([])

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })
      const data = (await res.json()) as ChatResponse
      if (!res.ok) throw new Error('Chat request failed')
      setAnswer(data.answer)
      setSources(data.sources)
    } catch (err) {
      setAnswer(err instanceof Error ? err.message : 'Chat request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">NEXUS</p>
          <h1>AI Knowledge Chatbot</h1>
        </div>
        <div className="status-card">
          <span className={`status-dot ${apiStatus}`}></span>
          <div>
            <strong>Backend {apiStatus}</strong>
            <p>{API_URL}</p>
          </div>
        </div>
        <div className="metric">
          <span>{graphCount}</span>
          <p>chunk nodes in graph</p>
        </div>
      </aside>

      <section className="workspace">
        <section className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Ingestion</p>
              <h2>Upload knowledge</h2>
            </div>
            <span>.txt .pdf .json</span>
          </div>
          <div className="upload-row">
            <input
              type="file"
              accept=".txt,.pdf,.json"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
            <button onClick={uploadFile} disabled={!file || loading}>
              Ingest
            </button>
          </div>
          {uploadMessage && <p className="note">{uploadMessage}</p>}
        </section>

        <section className="panel chat-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">RAG Chat</p>
              <h2>Ask the knowledge base</h2>
            </div>
          </div>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            rows={3}
          />
          <button className="primary" onClick={askQuestion} disabled={loading}>
            {loading ? 'Working...' : 'Ask'}
          </button>
          {answer && (
            <div className="answer">
              <h3>Answer</h3>
              <p>{answer}</p>
              <h3>Sources</h3>
              {sources.length > 0 ? (
                <ul>
                  {sources.map((source) => (
                    <li key={source}>{source}</li>
                  ))}
                </ul>
              ) : (
                <p>No sources returned yet.</p>
              )}
            </div>
          )}
        </section>

        <section className="panel graph-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Graph</p>
              <h2>Chunk similarity graph</h2>
            </div>
            <button onClick={refreshGraph}>Refresh</button>
          </div>
          <div className="graph-placeholder">
            <span>{graphCount}</span>
            <p>nodes loaded from /graph/chunks</p>
          </div>
        </section>
      </section>
    </main>
  )
}

export default App
