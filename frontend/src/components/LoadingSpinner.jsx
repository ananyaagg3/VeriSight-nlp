import React from 'react';

export default function LoadingSpinner({ darkMode }) {
    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '4rem 2rem',
            gap: '1.5rem'
        }}>
            {/* Animated Spinner */}
            <div style={{
                width: '80px',
                height: '80px',
                border: '6px solid var(--glass-border)',
                borderTop: '6px solid var(--teal-primary)',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                boxShadow: '0 0 30px rgba(20, 184, 166, 0.3)'
            }}></div>

            {/* Loading Text */}
            <div style={{ textAlign: 'center' }}>
                <h3 style={{
                    fontSize: '1.5rem',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    marginBottom: '0.5rem'
                }}>
                    Analyzing Content...
                </h3>
                <p style={{
                    color: 'var(--text-muted)',
                    fontSize: '0.95rem'
                }}>
                    🔍 Running ML models • 🌐 Checking knowledge graphs • 📊 Generating evidence
                </p>
            </div>

            {/* Progress Dots */}
            <div style={{
                display: 'flex',
                gap: '0.5rem'
            }}>
                {[0, 1, 2].map((i) => (
                    <div
                        key={i}
                        style={{
                            width: '12px',
                            height: '12px',
                            borderRadius: '50%',
                            background: 'var(--teal-primary)',
                            animation: `pulse 1.5s ease-in-out ${i * 0.2}s infinite`
                        }}
                    ></div>
                ))}
            </div>
        </div>
    );
}

/* Add animations */
if (typeof document !== 'undefined') {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        @keyframes pulse {
            0%, 100% { opacity: 0.3; transform: scale(0.8); }
            50% { opacity: 1; transform: scale(1.2); }
        }
    `;
    if (!document.querySelector('style[data-loading-animations]')) {
        style.setAttribute('data-loading-animations', 'true');
        document.head.appendChild(style);
    }
}
