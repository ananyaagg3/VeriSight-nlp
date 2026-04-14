import React from 'react';
import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from 'recharts';

const ConfidenceChart = ({ confidence, verdict, keywords = [] }) => {
    // Confidence gauge data
    const confidencePercent = Math.round(confidence * 100);
    const gaugeColor = verdict === 'AUTHENTIC'
        ? '#10b981'
        : verdict === 'NEEDS_VERIFICATION'
            ? '#fbbf24'
            : '#ef4444';
    const gaugeData = [
        {
            name: 'Confidence',
            value: confidencePercent,
            fill: gaugeColor
        }
    ];

    // Keywords bar chart data  
    const keywordData = keywords.slice(0, 5).map(kw => ({
        word: kw.word,
        score: Math.round((kw.score || 0) * 100),
        importance: kw.importance || 'medium'
    }));

    // Color based on importance
    const getColor = (importance) => {
        switch (importance) {
            case 'high': return '#ef4444';
            case 'medium': return '#14b8a6';
            default: return '#6b7280';
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Confidence Gauge */}
            <div className="glass-card">
                <h3 style={{
                    fontSize: '1.25rem',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    marginBottom: '1rem'
                }}>
                    Confidence Score
                </h3>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <ResponsiveContainer width="100%" height={200}>
                        <RadialBarChart
                            cx="50%"
                            cy="50%"
                            innerRadius="60%"
                            outerRadius="100%"
                            barSize={20}
                            data={gaugeData}
                            startAngle={180}
                            endAngle={0}
                        >
                            <PolarAngleAxis
                                type="number"
                                domain={[0, 100]}
                                angleAxisId={0}
                                tick={false}
                            />
                            <RadialBar
                                background={{ fill: 'var(--glass-border)' }}
                                dataKey="value"
                                cornerRadius={10}
                                fill={gaugeData[0].fill}
                            />
                        </RadialBarChart>
                    </ResponsiveContainer>
                </div>
                <div style={{ textAlign: 'center', marginTop: '0.5rem' }}>
                    <p style={{ fontSize: '3rem', fontWeight: 700, color: gaugeData[0].fill }}>
                        {confidencePercent}%
                    </p>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                        {verdict === 'MISINFORMATION'
                            ? 'Misinformation Likelihood'
                            : verdict === 'NEEDS_VERIFICATION'
                                ? 'Uncertain — Needs Verification'
                                : 'Authenticity Score'}
                    </p>
                </div>
            </div>

            {/* Keywords Importance Chart */}
            {keywordData.length > 0 && (
                <div className="glass-card">
                    <h3 style={{
                        fontSize: '1.25rem',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                        marginBottom: '1rem'
                    }}>
                        Key Terms Analysis
                    </h3>
                    <ResponsiveContainer width="100%" height={180}>
                        <BarChart data={keywordData} layout="horizontal">
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" opacity={0.3} />
                            <XAxis
                                type="number"
                                domain={[0, 100]}
                                tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                            />
                            <YAxis
                                dataKey="word"
                                type="category"
                                tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                                width={80}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'var(--bg-card)',
                                    border: '1px solid var(--glass-border)',
                                    borderRadius: '8px',
                                    color: 'var(--text-primary)'
                                }}
                                formatter={(value) => [`${value}%`, 'Attention Score']}
                            />
                            <Bar dataKey="score" radius={[0, 8, 8, 0]}>
                                {keywordData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={getColor(entry.importance)} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                    <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', justifyContent: 'center', fontSize: '0.875rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#ef4444' }}></div>
                            <span style={{ color: 'var(--text-muted)' }}>High Importance</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#14b8a6' }}></div>
                            <span style={{ color: 'var(--text-muted)' }}>Medium Importance</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Processing Info */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Analysis Method</p>
                    <p style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '0.25rem' }}>
                        Multimodal AI
                    </p>
                </div>
                <div className="glass-card" style={{ textAlign: 'center' }}>
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Verification</p>
                    <p style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '0.25rem' }}>
                        Knowledge Graph
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ConfidenceChart;
