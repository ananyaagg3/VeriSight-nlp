import React, { useState, useEffect } from 'react';
import { getHistory, clearHistory } from '../services/analysisService';

export default function History({ darkMode }) {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [databaseAvailable, setDatabaseAvailable] = useState(true);

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await getHistory(20);
            setHistory(data.history || []);
            setDatabaseAvailable(data.database_available !== false);
        } catch (err) {
            setError(err.message || 'Failed to load history');
        } finally {
            setLoading(false);
        }
    };

    const handleClearHistory = async () => {
        if (!window.confirm('⚠️ Are you sure you want to clear ALL history? This cannot be undone!')) {
            return;
        }

        try {
            setLoading(true);
            const result = await clearHistory();
            setHistory([]);
            alert(`✅ Successfully cleared ${result.deleted_count} analysis records!`);
        } catch (err) {
            setError('Failed to clear history');
            alert('❌ Failed to clear history. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="container" style={{ paddingTop: '4rem' }}>
                <h1 style={{
                    fontSize: '2.5rem',
                    fontWeight: 700,
                    color: 'var(--text-primary)',
                    marginBottom: '2rem',
                    textAlign: 'center'
                }}>
                    📊 Analysis History
                </h1>
                <div style={{ textAlign: 'center', padding: '3rem 0' }}>
                    <div style={{
                        width: '48px',
                        height: '48px',
                        border: '4px solid var(--glass-border)',
                        borderTopColor: 'var(--teal-primary)',
                        borderRadius: '50%',
                        margin: '0 auto',
                        animation: 'spin 1s linear infinite'
                    }}></div>
                </div>
            </div>
        );
    }

    return (
        <div className="container" style={{ paddingTop: '4rem', paddingBottom: '4rem' }}>
            {/* Header with Clear Button */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '2rem',
                flexWrap: 'wrap',
                gap: '1rem'
            }}>
                <h1 style={{
                    fontSize: '2.5rem',
                    fontWeight: 700,
                    background: 'linear-gradient(135deg, var(--teal-primary), var(--cyan-accent))',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    margin: 0
                }}>
                    📊 Analysis History
                </h1>

                {history.length > 0 && (
                    <button
                        onClick={handleClearHistory}
                        disabled={loading}
                        style={{
                            padding: '0.75rem 1.5rem',
                            borderRadius: '12px',
                            border: '2px solid #ef4444',
                            background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.1))',
                            color: '#fca5a5',
                            fontWeight: 700,
                            fontSize: '1rem',
                            cursor: loading ? 'not-allowed' : 'pointer',
                            transition: 'all 0.3s ease',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            opacity: loading ? 0.5 : 1,
                            boxShadow: '0 4px 12px rgba(239, 68, 68, 0.3)'
                        }}
                        onMouseOver={(e) => {
                            if (!loading) {
                                e.currentTarget.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
                                e.currentTarget.style.color = 'white';
                                e.currentTarget.style.transform = 'scale(1.05)';
                            }
                        }}
                        onMouseOut={(e) => {
                            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.1))';
                            e.currentTarget.style.color = '#fca5a5';
                            e.currentTarget.style.transform = 'scale(1)';
                        }}
                    >
                        <span style={{ fontSize: '1.25rem' }}>🗑️</span>
                        Clear All History
                    </button>
                )}
            </div>

            {error && (
                <div style={{
                    padding: '1rem',
                    borderRadius: '12px',
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid #ef4444',
                    color: '#fca5a5',
                    marginBottom: '2rem'
                }}>
                    {error}
                </div>
            )}

            {history.length === 0 ? (
                <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
                    <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📭</div>
                    <h3 style={{ fontSize: '1.5rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                        No History Yet
                    </h3>
                    <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
                        {databaseAvailable
                            ? 'Your analysis history will appear here after you run analyses.'
                            : 'History is not saved because the backend is not connected to MongoDB. Set MONGODB_URI in your backend .env (e.g. mongodb://localhost:27017) and restart the server to save and view history.'}
                    </p>
                    {!databaseAvailable && (
                        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                            Analyses still work; they just won’t be stored or shown here until the database is connected.
                        </p>
                    )}
                </div>
            ) : (
                <div style={{ display: 'grid', gap: '1.5rem' }}>
                    {history.map((item, index) => (
                        <div
                            key={index}
                            className="glass-card"
                            style={{
                                borderLeft: `4px solid ${item.verdict === 'AUTHENTIC' ? '#10b981' : item.verdict === 'NEEDS_VERIFICATION' ? '#fbbf24' : '#ef4444'}`,
                                transition: 'all 0.3s ease'
                            }}
                            onMouseOver={(e) => {
                                e.currentTarget.style.transform = 'translateX(8px)';
                                e.currentTarget.style.borderLeftWidth = '6px';
                            }}
                            onMouseOut={(e) => {
                                e.currentTarget.style.transform = 'translateX(0)';
                                e.currentTarget.style.borderLeftWidth = '4px';
                            }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', marginBottom: '1rem' }}>
                                <div style={{ flex: 1 }}>
                                    <div style={{
                                        display: 'inline-block',
                                        padding: '0.4rem 1rem',
                                        borderRadius: '50px',
                                        background: item.verdict === 'AUTHENTIC'
                                            ? 'linear-gradient(135deg, #10b981, #059669)'
                                            : item.verdict === 'NEEDS_VERIFICATION'
                                                ? 'linear-gradient(135deg, #fbbf24, #f59e0b)'
                                                : 'linear-gradient(135deg, #ef4444, #dc2626)',
                                        color: 'white',
                                        fontWeight: 600,
                                        fontSize: '0.85rem',
                                        marginBottom: '0.75rem'
                                    }}>
                                        {item.verdict === 'AUTHENTIC'
                                            ? '✓ AUTHENTIC'
                                            : item.verdict === 'NEEDS_VERIFICATION'
                                                ? '? NEEDS VERIFICATION'
                                                : '✗ MISINFORMATION'}
                                    </div>
                                    <p style={{
                                        color: 'var(--text-primary)',
                                        fontSize: '1rem',
                                        lineHeight: 1.6,
                                        marginBottom: '0.5rem'
                                    }}>
                                        {item.text}
                                    </p>
                                    <p style={{
                                        color: 'var(--text-muted)',
                                        fontSize: '0.85rem'
                                    }}>
                                        {new Date(item.timestamp).toLocaleString()}
                                    </p>
                                </div>
                                <div style={{
                                    fontSize: '2rem',
                                    fontWeight: 700,
                                    color: item.verdict === 'AUTHENTIC' ? '#10b981' : item.verdict === 'NEEDS_VERIFICATION' ? '#fbbf24' : '#f87171'
                                }}>
                                    {(item.confidence * 100).toFixed(0)}%
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
