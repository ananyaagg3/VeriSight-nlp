import React from 'react';
import ConfidenceChart from './ConfidenceChart';
import { motion } from 'framer-motion';

export default function AnalysisResult({ result, darkMode }) {
    // Safety check
    if (!result) {
        return null;
    }

    const detailedClaims = result.detailed_claims || [];
    const hasMisinfoClaim = detailedClaims.some(c => c.verdict === 'MISINFORMATION');
    const verdict = hasMisinfoClaim ? 'MISINFORMATION' : (result.verdict || 'NEEDS_VERIFICATION');
    // When showing MISINFORMATION from claims, use max claim confidence so the % matches the detail
    const displayConfidence = hasMisinfoClaim && detailedClaims.length
        ? Math.max(result.confidence || 0, ...detailedClaims.filter(c => c.verdict === 'MISINFORMATION').map(c => c.confidence || 0))
        : (result.confidence || 0);
    const confidencePercent = (displayConfidence * 100).toFixed(1);
    const isAuthentic = verdict === 'AUTHENTIC';
    const needsVerification = verdict === 'NEEDS_VERIFICATION';
    const isMisinformation = verdict === 'MISINFORMATION';

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            style={{ marginTop: '3rem' }}
        >
            {/* Verdict Banner - BRIGHTER COLORS */}
            <div className="glass-card" style={{
                borderLeft: `6px solid ${isAuthentic ? '#10b981' : needsVerification ? '#fbbf24' : '#ef4444'}`,
                background: isAuthentic
                    ? 'linear-gradient(90deg, rgba(16, 185, 129, 0.2), rgba(20, 184, 166, 0.1))'
                    : needsVerification
                        ? 'linear-gradient(90deg, rgba(251, 191, 36, 0.2), rgba(245, 158, 11, 0.12))'
                        : 'linear-gradient(90deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.1))',
                marginBottom: '2rem',
                boxShadow: isAuthentic
                    ? '0 8px 32px rgba(16, 185, 129, 0.2)'
                    : needsVerification
                        ? '0 8px 32px rgba(251, 191, 36, 0.18)'
                        : '0 8px 32px rgba(239, 68, 68, 0.2)'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                    <div>
                        <h2 style={{
                            fontSize: '2.25rem',
                            fontWeight: 700,
                            color: isAuthentic ? '#10b981' : needsVerification ? '#fbbf24' : '#f87171',
                            marginBottom: '0.5rem',
                            textShadow: isAuthentic
                                ? '0 0 20px rgba(16, 185, 129, 0.3)'
                                : needsVerification
                                    ? '0 0 20px rgba(251, 191, 36, 0.25)'
                                    : '0 0 20px rgba(239, 68, 68, 0.3)'
                        }}>
                            {isAuthentic
                                ? '✅ AUTHENTIC CONTENT'
                                : needsVerification
                                    ? 'ℹ️ NEEDS VERIFICATION'
                                    : '⚠️ MISINFORMATION DETECTED'}
                        </h2>
                        <p style={{ fontSize: '1.2rem', color: 'var(--text-primary)', fontWeight: 600 }}>
                            Confidence: <span style={{
                                color: isAuthentic ? '#10b981' : needsVerification ? '#fbbf24' : '#f87171',
                                fontWeight: 700,
                                fontSize: '1.3rem'
                            }}>{confidencePercent}%</span>
                        </p>
                        {result.processing_time_ms && (
                            <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                                ⚡ Analyzed in {result.processing_time_ms.toFixed(0)}ms
                            </p>
                        )}
                    </div>
                    <div style={{
                        fontSize: '5rem',
                        opacity: 0.4,
                        filter: isAuthentic
                            ? 'drop-shadow(0 0 10px rgba(16, 185, 129, 0.5))'
                            : needsVerification
                                ? 'drop-shadow(0 0 10px rgba(251, 191, 36, 0.45))'
                                : 'drop-shadow(0 0 10px rgba(239, 68, 68, 0.5))'
                    }}>
                        {isAuthentic ? '✓' : needsVerification ? '?' : '✗'}
                    </div>
                </div>
            </div>

            {/* SCORE BREAKDOWN PANEL - 4 Component Scores */}
            {result.score_breakdown && (
                <div className="glass-card" style={{
                    marginBottom: '2rem',
                    background: 'linear-gradient(135deg, hsla(220, 15%, 10%, 0.9), hsla(220, 15%, 8%, 0.9))'
                }}>
                    <h3 style={{
                        fontSize: '1.25rem',
                        fontWeight: 600,
                        color: 'var(--primary-accent)',
                        marginBottom: '1.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}>
                        <span>📊</span> Analysis Score Breakdown
                    </h3>
                    <div className="score-breakdown">
                        {/* Image Authenticity */}
                        <div className="score-item">
                            <span className="score-label">🖼️ Image Authenticity</span>
                            <span className="score-value" style={{
                                color: result.score_breakdown.image_authenticity != null
                                    ? (result.score_breakdown.image_authenticity > 50 ? '#10b981' : '#f87171')
                                    : 'var(--text-muted)'
                            }}>
                                {result.score_breakdown.image_authenticity != null
                                    ? `${result.score_breakdown.image_authenticity}%`
                                    : 'N/A'}
                            </span>
                            {result.score_breakdown.image_authenticity != null && (
                                <div className="score-bar">
                                    <div className="score-fill" style={{
                                        width: `${result.score_breakdown.image_authenticity}%`,
                                        background: result.score_breakdown.image_authenticity > 50
                                            ? 'linear-gradient(90deg, #10b981, #059669)'
                                            : 'linear-gradient(90deg, #f87171, #ef4444)'
                                    }} />
                                </div>
                            )}
                        </div>

                        {/* Text Authenticity */}
                        <div className="score-item">
                            <span className="score-label">📝 Text Authenticity</span>
                            <span className="score-value" style={{
                                color: result.score_breakdown.text_authenticity > 50 ? '#10b981' : '#f87171'
                            }}>
                                {result.score_breakdown.text_authenticity}%
                            </span>
                            <div className="score-bar">
                                <div className="score-fill" style={{
                                    width: `${result.score_breakdown.text_authenticity}%`,
                                    background: result.score_breakdown.text_authenticity > 50
                                        ? 'linear-gradient(90deg, #10b981, #059669)'
                                        : 'linear-gradient(90deg, #f87171, #ef4444)'
                                }} />
                            </div>
                        </div>

                        {/* Cross-Modal Consistency */}
                        <div className="score-item">
                            <span className="score-label">🔗 Cross-Modal Consistency</span>
                            <span className="score-value" style={{
                                color: result.score_breakdown.cross_modal_consistency != null
                                    ? (result.score_breakdown.cross_modal_consistency > 40 ? '#10b981' : '#fbbf24')
                                    : 'var(--text-muted)'
                            }}>
                                {result.score_breakdown.cross_modal_consistency != null
                                    ? `${result.score_breakdown.cross_modal_consistency}%`
                                    : 'N/A'}
                            </span>
                            {result.score_breakdown.cross_modal_consistency != null && (
                                <div className="score-bar">
                                    <div className="score-fill" style={{
                                        width: `${result.score_breakdown.cross_modal_consistency}%`,
                                        background: 'linear-gradient(90deg, var(--primary-accent), var(--cyan-accent))'
                                    }} />
                                </div>
                            )}
                        </div>

                        {/* Knowledge Verification */}
                        <div className="score-item">
                            <span className="score-label">🔍 Knowledge Verification</span>
                            <span className="score-value" style={{
                                color: result.score_breakdown.knowledge_verification > 50 ? '#10b981' : '#fbbf24'
                            }}>
                                {result.score_breakdown.knowledge_verification}%
                            </span>
                            <div className="score-bar">
                                <div className="score-fill" style={{
                                    width: `${result.score_breakdown.knowledge_verification}%`,
                                    background: 'linear-gradient(90deg, #3b82f6, #2563eb)'
                                }} />
                            </div>
                        </div>
                    </div>

                    {/* Fusion Method Badge */}
                    {result.fusion_method && (
                        <div style={{ marginTop: '1rem', textAlign: 'center' }}>
                            <span style={{
                                padding: '0.5rem 1rem',
                                background: 'var(--glass-bg)',
                                border: '1px solid var(--glass-border)',
                                borderRadius: '50px',
                                fontSize: '0.85rem',
                                color: 'var(--text-muted)'
                            }}>
                                Fusion: <strong style={{ color: 'var(--primary-accent)' }}>{result.fusion_method}</strong>
                            </span>
                        </div>
                    )}
                </div>
            )}

            {/* DETAILED CLAIMS - SEPARATE BOXES */}
            {result.detailed_claims && result.detailed_claims.length > 0 && (
                <div style={{ marginBottom: '2rem' }}>
                    <h3 style={{
                        fontSize: '1.5rem',
                        fontWeight: 600,
                        color: 'var(--teal-primary)',
                        marginBottom: '1.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.75rem'
                    }}>
                        <span>📋</span> Detailed Claim-by-Claim Analysis
                    </h3>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        {result.detailed_claims.map((claim, index) => {
                            const claimIsAuthentic = claim.verdict === 'AUTHENTIC';
                            return (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    className="glass-card"
                                    style={{
                                        borderLeft: `4px solid ${claimIsAuthentic ? '#10b981' : claim.verdict === 'NEEDS_VERIFICATION' ? '#fbbf24' : '#ef4444'}`,
                                        background: claimIsAuthentic
                                            ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(20, 184, 166, 0.05))'
                                            : claim.verdict === 'NEEDS_VERIFICATION'
                                                ? 'linear-gradient(135deg, rgba(251, 191, 36, 0.08), rgba(245, 158, 11, 0.05))'
                                                : 'linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(220, 38, 38, 0.05))'
                                    }}
                                >
                                    {/* Claim Header */}
                                    <div style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'flex-start',
                                        marginBottom: '1rem',
                                        gap: '1rem'
                                    }}>
                                        <div style={{ flex: 1 }}>
                                            <div style={{
                                                display: 'inline-block',
                                                padding: '0.4rem 1rem',
                                                borderRadius: '50px',
                                                background: claimIsAuthentic
                                                    ? 'linear-gradient(135deg, #10b981, #059669)'
                                                    : claim.verdict === 'NEEDS_VERIFICATION'
                                                        ? 'linear-gradient(135deg, #fbbf24, #f59e0b)'
                                                        : 'linear-gradient(135deg, #ef4444, #dc2626)',
                                                color: 'white',
                                                fontWeight: 600,
                                                fontSize: '0.85rem',
                                                marginBottom: '0.75rem',
                                                boxShadow: claimIsAuthentic
                                                    ? '0 4px 12px rgba(16, 185, 129, 0.4)'
                                                    : claim.verdict === 'NEEDS_VERIFICATION'
                                                        ? '0 4px 12px rgba(251, 191, 36, 0.3)'
                                                        : '0 4px 12px rgba(239, 68, 68, 0.4)'
                                            }}>
                                                {claimIsAuthentic
                                                    ? '✓ AUTHENTIC'
                                                    : claim.verdict === 'NEEDS_VERIFICATION'
                                                        ? '? NEEDS VERIFICATION'
                                                        : '✗ MISINFORMATION'}
                                            </div>
                                            <p style={{
                                                fontSize: '1.05rem',
                                                color: 'var(--text-primary)',
                                                lineHeight: 1.6,
                                                fontWeight: 500
                                            }}>
                                                "{claim.claim}"
                                            </p>
                                        </div>
                                        <div style={{
                                            fontSize: '2rem',
                                            fontWeight: 700,
                                            color: claimIsAuthentic ? '#10b981' : claim.verdict === 'NEEDS_VERIFICATION' ? '#fbbf24' : '#f87171'
                                        }}>
                                            {((claim.confidence || 0) * 100).toFixed(0)}%
                                        </div>
                                    </div>

                                    {/* Evidence */}
                                    <div style={{
                                        padding: '1rem',
                                        background: 'rgba(20, 184, 166, 0.05)',
                                        borderRadius: '8px',
                                        borderLeft: '3px solid var(--teal-primary)'
                                    }}>
                                        <p style={{
                                            fontSize: '0.9rem',
                                            color: 'var(--text-secondary)',
                                            lineHeight: 1.6,
                                            margin: 0
                                        }}>
                                            <strong style={{ color: 'var(--teal-primary)' }}>Evidence:</strong> {claim.evidence}
                                        </p>
                                    </div>

                                    {/* Sources */}
                                    {claim.sources && claim.sources.length > 0 && (
                                        <div style={{ marginTop: '0.75rem' }}>
                                            <p style={{
                                                fontSize: '0.85rem',
                                                color: 'var(--text-muted)',
                                                marginBottom: '0.5rem'
                                            }}>
                                                <strong>Sources:</strong>
                                            </p>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                                {claim.sources.map((source, idx) => (
                                                    <span
                                                        key={idx}
                                                        style={{
                                                            padding: '0.25rem 0.75rem',
                                                            background: 'var(--glass-bg)',
                                                            border: '1px solid var(--glass-border)',
                                                            borderRadius: '50px',
                                                            fontSize: '0.8rem',
                                                            color: 'var(--text-muted)'
                                                        }}
                                                    >
                                                        {typeof source === 'string' ? source : source.name || 'Source'}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </motion.div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Two Column Layout */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '2rem',
                marginBottom: '2rem'
            }}>
                {/* Left Column: Charts */}
                <div>
                    <ConfidenceChart
                        confidence={result.confidence || 0}
                        verdict={verdict}
                        keywords={result.keywords || []}
                    />
                </div>

                {/* Right Column: Information */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    {/* Explanation */}
                    {result.explanation && (
                        <div className="glass-card" style={{
                            background: 'linear-gradient(135deg, rgba(20, 184, 166, 0.08), rgba(6, 182, 212, 0.05))'
                        }}>
                            <h3 style={{
                                fontSize: '1.25rem',
                                fontWeight: 600,
                                color: 'var(--teal-primary)',
                                marginBottom: '1rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }}>
                                <span>📝</span> Analysis Explanation
                            </h3>
                            <p style={{ color: 'var(--text-primary)', lineHeight: 1.7, fontSize: '1rem' }}>
                                {result.explanation}
                            </p>
                        </div>
                    )}

                    {/* Keywords */}
                    {result.keywords && result.keywords.length > 0 && (
                        <div className="glass-card">
                            <h3 style={{
                                fontSize: '1.25rem',
                                fontWeight: 600,
                                color: 'var(--teal-primary)',
                                marginBottom: '1rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }}>
                                <span>🔑</span> Key Terms Detected
                            </h3>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                                {result.keywords.slice(0, 10).map((keyword, index) => (
                                    <motion.div
                                        key={index}
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        transition={{ delay: index * 0.1 }}
                                        style={{
                                            padding: '0.6rem 1.2rem',
                                            borderRadius: '50px',
                                            background: keyword.importance === 'high'
                                                ? 'linear-gradient(135deg, #f87171, #ef4444)'
                                                : 'linear-gradient(135deg, var(--teal-primary), var(--cyan-accent))',
                                            border: 'none',
                                            color: 'white',
                                            fontWeight: 600,
                                            cursor: 'default',
                                            transition: 'transform 0.2s ease',
                                            boxShadow: keyword.importance === 'high'
                                                ? '0 4px 12px rgba(239, 68, 68, 0.4)'
                                                : '0 4px 12px rgba(20, 184, 166, 0.4)'
                                        }}
                                        onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
                                        onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                    >
                                        {keyword.word} 📌 {((keyword.score || 0) * 100).toFixed(0)}%
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Sources */}
                    {result.sources && result.sources.length > 0 && (
                        <div className="glass-card">
                            <h3 style={{
                                fontSize: '1.25rem',
                                fontWeight: 600,
                                color: 'var(--teal-primary)',
                                marginBottom: '1rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }}>
                                <span>🔗</span> Verification Sources
                            </h3>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                {result.sources.slice(0, 5).map((source, index) => (
                                    <div
                                        key={index}
                                        style={{
                                            padding: '0.9rem',
                                            background: 'linear-gradient(135deg, rgba(20, 184, 166, 0.1), rgba(6, 182, 212, 0.05))',
                                            border: '1px solid var(--teal-primary)',
                                            borderRadius: '10px',
                                            color: 'var(--text-primary)',
                                            fontSize: '0.95rem',
                                            fontWeight: 500
                                        }}
                                    >
                                        {typeof source === 'string' ? source : (source.name || source.url || 'Unknown source')}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Related articles (News API) */}
            {result.related_articles && result.related_articles.length > 0 && (
                <div className="glass-card" style={{ marginBottom: '2rem' }}>
                    <h3 style={{
                        fontSize: '1.25rem',
                        fontWeight: 600,
                        color: 'var(--teal-primary)',
                        marginBottom: '1rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}>
                        <span>📰</span> Related articles
                    </h3>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1rem' }}>
                        News coverage related to your claim — use these to cross-check.
                    </p>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        {result.related_articles.map((article, index) => (
                            <a
                                key={index}
                                href={article.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                    display: 'block',
                                    padding: '1rem',
                                    background: 'linear-gradient(135deg, rgba(20, 184, 166, 0.08), rgba(6, 182, 212, 0.05))',
                                    border: '1px solid var(--glass-border)',
                                    borderRadius: '12px',
                                    color: 'var(--text-primary)',
                                    textDecoration: 'none',
                                    transition: 'border-color 0.2s, box-shadow 0.2s'
                                }}
                                onMouseOver={(e) => {
                                    e.currentTarget.style.borderColor = 'var(--teal-primary)';
                                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(20, 184, 166, 0.2)';
                                }}
                                onMouseOut={(e) => {
                                    e.currentTarget.style.borderColor = 'var(--glass-border)';
                                    e.currentTarget.style.boxShadow = 'none';
                                }}
                            >
                                <div style={{ fontWeight: 600, fontSize: '1rem', marginBottom: '0.35rem' }}>
                                    {article.title}
                                </div>
                                {(article.source || article.publishedAt) && (
                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                                        {article.source}
                                        {article.publishedAt && (
                                            <span style={{ marginLeft: '0.5rem' }}>
                                                • {new Date(article.publishedAt).toLocaleDateString()}
                                            </span>
                                        )}
                                    </div>
                                )}
                                {article.description && (
                                    <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem', lineHeight: 1.4 }}>
                                        {article.description}
                                    </div>
                                )}
                            </a>
                        ))}
                    </div>
                </div>
            )}

            {/* Bottom Row: Additional Info - BRIGHTER */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '1rem'
            }}>
                {/* Sentiment */}
                {result.sentiment && (
                    <div className="glass-card" style={{
                        textAlign: 'center',
                        background: 'linear-gradient(135deg, rgba(20, 184, 166, 0.08), rgba(6, 182, 212, 0.05))'
                    }}>
                        <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>
                            {result.sentiment === 'POSITIVE' ? '😊' : result.sentiment === 'NEGATIVE' ? '😞' : '😐'}
                        </div>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                            Sentiment: <span style={{ fontWeight: 700, color: 'var(--teal-primary)' }}>
                                {typeof result.sentiment === 'string' ? result.sentiment : result.sentiment.sentiment || 'N/A'}
                            </span>
                        </p>
                    </div>
                )}

                {/* Language */}
                {result.language && (
                    <div className="glass-card" style={{
                        textAlign: 'center',
                        background: 'linear-gradient(135deg, rgba(20, 184, 166, 0.08), rgba(6, 182, 212, 0.05))'
                    }}>
                        <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🌍</div>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                            Language: <span style={{ fontWeight: 700, color: 'var(--teal-primary)' }}>{result.language.toUpperCase()}</span>
                        </p>
                    </div>
                )}

                {/* Analysis ID */}
                {result.analysis_id && (
                    <div className="glass-card" style={{
                        textAlign: 'center',
                        background: 'linear-gradient(135deg, rgba(20, 184, 166, 0.08), rgba(6, 182, 212, 0.05))'
                    }}>
                        <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🆔</div>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                            Analysis ID: <span style={{ fontWeight: 700, color: 'var(--teal-primary)', fontSize: '0.75rem' }}>
                                {result.analysis_id.substring(0, 8)}...
                            </span>
                        </p>
                    </div>
                )}
            </div>
        </motion.div>
    );
}
