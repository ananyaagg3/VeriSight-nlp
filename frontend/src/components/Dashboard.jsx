import React, { useState } from 'react';
import FileUpload from './FileUpload';
import ImageUpload from './ImageUpload';
import AnalysisResult from './AnalysisResult';
import LoadingSpinner from './LoadingSpinner';
import { analyzeText } from '../services/analysisService';

export default function Dashboard({ darkMode }) {
    const [text, setText] = useState('');
    const [image, setImage] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleAnalyze = async () => {
        if (!text || text.length < 10) {
            setError('Please enter at least 10 characters');
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await analyzeText(text, image);
            setResult(response);
        } catch (err) {
            setError(err.message || 'Analysis failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleClear = () => {
        setText('');
        setImage(null);
        setResult(null);
        setError(null);
    };

    return (
        <div className="container">
            {/* Hero Section - Dark Premium Design */}
            <div className="hero">
                <h1 style={{
                    fontSize: '3rem',
                    fontWeight: 700,
                    marginBottom: '0.5rem'
                }}>
                    <span style={{ color: 'white' }}>Veri</span>
                    <span style={{
                        background: 'linear-gradient(135deg, var(--primary-accent), var(--cyan-accent))',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text'
                    }}>Sight</span>
                </h1>

                {/* Subtitle */}
                <p style={{ fontSize: '1.1rem', color: 'var(--text-muted)', marginBottom: '2rem' }}>
                    Knowledge-Enhanced Multimodal Misinformation Detection with Real-Time Fact-Checking Integration
                </p>

                {/* Feature Badges */}
                <div className="hero-badges">
                    <div className="badge">
                        <span className="badge-icon">⚡</span>
                        200ms Response
                    </div>
                    <div className="badge">
                        <span className="badge-icon">🌍</span>
                        English Only
                    </div>
                    <div className="badge">
                        <span className="badge-icon">🧠</span>
                        Explainable AI
                    </div>
                </div>
            </div>

            {/* Main Card */}
            <div className="glass-card">
                {/* Text Input */}
                <div className="form-group">
                    <label>Enter text to analyze:</label>
                    <textarea
                        placeholder="Enter the text you want to analyze for misinformation..."
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                    />
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                        <span>{text.length} characters (minimum 10 required)</span>
                        {text.length > 0 && (
                            <button
                                onClick={handleClear}
                                style={{ background: 'none', border: 'none', color: 'var(--cyan-accent)', cursor: 'pointer' }}
                            >
                                Clear
                            </button>
                        )}
                    </div>
                </div>

                {/* File Upload */}
                <FileUpload darkMode={darkMode} onTextExtracted={setText} />

                {/* Image Upload */}
                <ImageUpload darkMode={darkMode} onImageSelected={setImage} currentImage={image} />

                {/* Analyze Button */}
                <button
                    onClick={handleAnalyze}
                    disabled={loading || text.length < 10}
                    className={`btn btn-primary btn-large ${loading || text.length < 10 ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                    {loading ? (
                        <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                            </svg>
                            Analyzing...
                        </span>
                    ) : (
                        <>
                            <span style={{ fontSize: '1.25rem' }}>🔍</span>
                            Analyze for Misinformation
                        </>
                    )}
                </button>

                {/* Error Message */}
                {error && (
                    <div style={{
                        marginTop: '1.5rem',
                        padding: '1rem',
                        borderRadius: '12px',
                        borderLeft: '4px solid #ef4444',
                        background: 'rgba(239, 68, 68, 0.1)',
                        color: '#fca5a5'
                    }}>
                        <p style={{ fontWeight: 600 }}>Error:</p>
                        <p>{error}</p>
                    </div>
                )}
            </div>

            {/* Loading Spinner */}
            {loading && <LoadingSpinner darkMode={darkMode} />}

            {/* Results */}
            {result && !loading && (
                <AnalysisResult result={result} darkMode={darkMode} />
            )}
        </div>
    );
}
