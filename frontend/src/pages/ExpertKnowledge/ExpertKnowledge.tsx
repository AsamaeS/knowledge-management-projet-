import { expertVoices, insights, sourceStats, themes } from './data'

export function ExpertKnowledge() {
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Expert Knowledge</p>
          <h1>Auto Experts Knowledge Profile</h1>
          <p className="hero-text">
            A curated, resume-style knowledge display built from the fixed PDF
            <strong> Knowledge Auo Experts.pdf</strong>. This section is separate
            from the RAG assistant and presents the document as a structured profile.
          </p>
        </div>
        <div className="source-card">
          <span>Source Document</span>
          <strong>Knowledge Auo Experts.pdf</strong>
          <p>Automotive, EV, battery, and semiconductor strategy dossier.</p>
        </div>
      </section>

      <section className="stats-grid" aria-label="Knowledge base summary">
        {sourceStats.map((stat) => (
          <article className="stat-card" key={stat.label}>
            <span>{stat.value}</span>
            <p>{stat.label}</p>
          </article>
        ))}
      </section>

      <section className="section">
        <div className="section-heading">
          <p className="eyebrow">Knowledge Map</p>
          <h2>Strategic Themes</h2>
        </div>
        <div className="theme-grid">
          {themes.map((theme) => (
            <article className="theme-card" key={theme.title}>
              <span className="tag">{theme.tag}</span>
              <h3>{theme.title}</h3>
              <p>{theme.summary}</p>
              <ul>
                {theme.points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>

      <section className="split-section">
        <div className="panel">
          <div className="section-heading">
            <p className="eyebrow">Resume View</p>
            <h2>Expert Voices Captured</h2>
          </div>
          <div className="voice-list">
            {expertVoices.map((voice) => (
              <article className="voice-card" key={voice.name}>
                <h3>{voice.name}</h3>
                <span>{voice.role}</span>
                <p>{voice.focus}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="panel dark-panel">
          <div className="section-heading">
            <p className="eyebrow">Executive Readout</p>
            <h2>What The PDF Is Really About</h2>
          </div>
          <ol className="insight-list">
            {insights.map((insight) => (
              <li key={insight}>{insight}</li>
            ))}
          </ol>
        </div>
      </section>
    </>
  )
}
