import React from 'react';

export default function About({ darkMode }) {
    return (
        <div className="container" style={{ paddingTop: '4rem', paddingBottom: '4rem' }}>
            {/* Hero Section */}
            <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
                <h1 style={{
                    fontSize: '3rem',
                    fontWeight: 700,
                    background: 'linear-gradient(135deg, var(--teal-primary), var(--cyan-accent))',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    marginBottom: '1rem'
                }}>
                    About VeriSight
                </h1>
                <p style={{
                    fontSize: '1.25rem',
                    color: 'var(--text-muted)',
                    maxWidth: '800px',
                    margin: '0 auto',
                    lineHeight: 1.6
                }}>
                    We're building a production-ready, knowledge-enhanced misinformation detection system that combines cutting-edge AI with knowledge graphs to provide fast, accurate, and explainable English fact-checking.
                </p>
            </div>

            {/* Key Features Grid */}
            <div style={{ marginBottom: '4rem' }}>
                <h2 style={{
                    fontSize: '2rem',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    marginBottom: '2rem',
                    textAlign: 'center'
                }}>
                    Key Features
                </h2>
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                    gap: '1.5rem'
                }}>
                    {[
                        { icon: '🌍', title: 'English Focused', desc: 'English-only analysis pipeline for consistent verdict quality and explainability' },
                        { icon: '🤖', title: 'AI-Powered', desc: 'XLM-RoBERTa for text analysis, CLIP for images, with quantized models for fast inference' },
                        { icon: '🔗', title: 'Knowledge Verification', desc: 'Integration with Google Fact Check API and Wikidata for comprehensive fact-checking' },
                        { icon: '⚡', title: 'Fast & Efficient', desc: '~200ms average response time with early-exit optimization for obvious patterns' },
                        { icon: '💡', title: 'Explainable Results', desc: 'Clear evidence with keywords, confidence scores, and authoritative sources' },
                        { icon: '💰', title: '100% Free', desc: 'Deployed on free-tier services: Vercel, Railway, and MongoDB Atlas' }
                    ].map((feature, idx) => (
                        <div key={idx} className="glass-card" style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>{feature.icon}</div>
                            <h3 style={{
                                fontSize: '1.25rem',
                                fontWeight: 600,
                                color: 'var(--text-primary)',
                                marginBottom: '0.5rem'
                            }}>
                                {feature.title}
                            </h3>
                            <p style={{ color: 'var(--text-muted)', lineHeight: 1.6 }}>
                                {feature.desc}
                            </p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Technology Stack */}
            <div style={{ marginBottom: '4rem' }}>
                <h2 style={{
                    fontSize: '2rem',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    marginBottom: '2rem',
                    textAlign: 'center'
                }}>
                    Technology Stack
                </h2>
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                    gap: '1.5rem'
                }}>
                    {[
                        {
                            title: 'Frontend',
                            items: ['React 18 + Vite', 'Modern CSS', 'Axios for API calls', 'React Router']
                        },
                        {
                            title: 'Backend',
                            items: ['FastAPI (Python)', 'MongoDB Atlas', 'PyTorch + Transformers', 'spaCy NER']
                        },
                        {
                            title: 'ML Models',
                            items: ['XLM-RoBERTa (text)', 'CLIP (images)', 'FLAVA (multimodal)', 'All quantized (INT8)']
                        },
                        {
                            title: 'Knowledge APIs',
                            items: ['Google Fact Check', 'Wikidata SPARQL', 'Smart caching', 'Quota management']
                        }
                    ].map((stack, idx) => (
                        <div key={idx} className="glass-card">
                            <h3 style={{
                                fontSize: '1.25rem',
                                fontWeight: 600,
                                color: 'var(--teal-primary)',
                                marginBottom: '1rem'
                            }}>
                                {stack.title}
                            </h3>
                            <ul style={{
                                listStyle: 'none',
                                padding: 0,
                                margin: 0
                            }}>
                                {stack.items.map((item, i) => (
                                    <li key={i} style={{
                                        color: 'var(--text-secondary)',
                                        padding: '0.5rem 0',
                                        borderBottom: i < stack.items.length - 1 ? '1px solid var(--glass-border)' : 'none'
                                    }}>
                                        • {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
            </div>

            {/* Performance Metrics */}
            <div className="glass-card" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
                <h2 style={{
                    fontSize: '2rem',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    marginBottom: '3rem'
                }}>
                    Performance Metrics
                </h2>
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '2rem'
                }}>
                    {[
                        { value: '91.6%', label: 'Average F1 Score' },
                        { value: '200ms', label: 'Avg Response Time' },
                        { value: '15+', label: 'Languages Supported' },
                        { value: '$0', label: 'Monthly Cost' }
                    ].map((metric, idx) => (
                        <div key={idx}>
                            <div style={{
                                fontSize: '3rem',
                                fontWeight: 700,
                                background: 'linear-gradient(135deg, var(--teal-primary), var(--cyan-accent))',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                backgroundClip: 'text',
                                marginBottom: '0.5rem'
                            }}>
                                {metric.value}
                            </div>
                            <div style={{
                                color: 'var(--text-muted)',
                                fontSize: '0.9rem'
                            }}>
                                {metric.label}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
