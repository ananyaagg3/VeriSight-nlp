import React from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function Navbar({ darkMode, toggleDarkMode }) {
    const location = useLocation();

    const isActive = (path) => location.pathname === path;

    return (
        <header>
            <div className="header-content">
                <Link to="/" className="logo-container">
                    <span style={{ fontSize: '1.75rem', fontWeight: 700, letterSpacing: '-0.5px' }}>
                        <span style={{ color: 'white' }}>Veri</span>
                        <span style={{
                            background: 'linear-gradient(135deg, var(--teal-primary), var(--cyan-accent))',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            backgroundClip: 'text'
                        }}>Sight</span>
                    </span>
                </Link>

                {/* Navigation Links */}
                <nav>
                    <Link
                        to="/"
                        className={isActive('/') ? 'active' : ''}
                    >
                        Dashboard
                    </Link>
                    <Link
                        to="/history"
                        className={isActive('/history') ? 'active' : ''}
                    >
                        History
                    </Link>
                    <Link
                        to="/about"
                        className={isActive('/about') ? 'active' : ''}
                    >
                        About
                    </Link>
                </nav>
            </div>
        </header>
    );
}
