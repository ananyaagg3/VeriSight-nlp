import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import History from './components/History';
import About from './components/About';
import Navbar from './components/Navbar';
import './styles/global.css';

function App() {
    const [darkMode, setDarkMode] = useState(true); // Default to dark mode

    useEffect(() => {
        // Check for saved theme preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'light') {
            setDarkMode(false);
            document.documentElement.classList.remove('dark');
        } else {
            setDarkMode(true);
            document.documentElement.classList.add('dark');
        }
    }, []);

    const toggleDarkMode = () => {
        setDarkMode(!darkMode);
        if (!darkMode) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    };

    return (
        <Router>
            <div className="min-h-screen">
                <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode} />

                <Routes>
                    <Route path="/" element={<Dashboard darkMode={darkMode} />} />
                    <Route path="/history" element={<History darkMode={darkMode} />} />
                    <Route path="/about" element={<About darkMode={darkMode} />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
