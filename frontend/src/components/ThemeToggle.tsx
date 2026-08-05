// ThemeToggle.tsx
import React, { useState, useEffect } from 'react';
import './ThemeToggle.css';

type ThemeMode = 'light' | 'dark' | 'system';

interface ThemeInfo {
    mode: ThemeMode;
    effective: 'light' | 'dark';
    system: 'light' | 'dark';
    isDark: boolean;
    isLight: boolean;
    isSystem: boolean;
}

interface ThemeToggleProps {
    className?: string;
    showLabel?: boolean;
    variant?: 'button' | 'dropdown' | 'compact';
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ 
    className = '', 
    showLabel = true,
    variant = 'button'
}) => {
    const [themeInfo, setThemeInfo] = useState<ThemeInfo>({
        mode: 'system',
        effective: 'light',
        system: 'light',
        isDark: false,
        isLight: true,
        isSystem: true
    });
    
    useEffect(() => {
        // Initialize from themeManager
        updateThemeInfo();
        
        // Listen for theme changes
        const handleThemeChange = () => {
            updateThemeInfo();
        };
        
        window.addEventListener('themechange', handleThemeChange as EventListener);
        return () => {
            window.removeEventListener('themechange', handleThemeChange as EventListener);
        };
    }, []);
    
    const updateThemeInfo = () => {
        if (window.themeManager) {
            setThemeInfo(window.themeManager.getInfo());
        }
    };
    
    const handleCycle = () => {
        if (window.themeManager) {
            window.themeManager.cycle();
        }
    };
    
    const handleSetMode = (mode: ThemeMode) => {
        if (window.themeManager) {
            window.themeManager.setMode(mode);
        }
    };
    
    const getIcon = (mode: ThemeMode = themeInfo.mode) => {
        if (mode === 'system') {
            return '🖥️';
        }
        return mode === 'dark' ? '🌙' : '☀️';
    };
    
    const getLabel = () => {
        if (themeInfo.isSystem) {
            return `System (${themeInfo.effective === 'dark' ? 'Dark' : 'Light'})`;
        }
        return themeInfo.mode === 'dark' ? 'Dark Mode' : 'Light Mode';
    };
    
    // Compact variant (icon only with tooltip)
    if (variant === 'compact') {
        return (
            <button
                onClick={handleCycle}
                className={`theme-toggle compact ${className}`}
                title={`Theme: ${getLabel()}. Click to cycle.`}
                aria-label={`Current theme: ${getLabel()}`}
            >
                <span className="theme-icon" role="img" aria-hidden="true">
                    {getIcon()}
                </span>
            </button>
        );
    }
    
    // Dropdown variant (all 3 options)
    if (variant === 'dropdown') {
        return (
            <div className={`theme-toggle dropdown ${className}`}>
                <button 
                    className={themeInfo.mode === 'light' ? 'active' : ''}
                    onClick={() => handleSetMode('light')}
                    title="Light Mode"
                >
                    <span className="theme-icon">{getIcon('light')}</span>
                    {showLabel && <span>Light</span>}
                </button>
                <button 
                    className={themeInfo.mode === 'dark' ? 'active' : ''}
                    onClick={() => handleSetMode('dark')}
                    title="Dark Mode"
                >
                    <span className="theme-icon">{getIcon('dark')}</span>
                    {showLabel && <span>Dark</span>}
                </button>
                <button 
                    className={themeInfo.mode === 'system' ? 'active' : ''}
                    onClick={() => handleSetMode('system')}
                    title="System Theme"
                >
                    <span className="theme-icon">{getIcon('system')}</span>
                    {showLabel && <span>Auto</span>}
                </button>
            </div>
        );
    }
    
    // Button variant (default - cycles through options)
    return (
        <button
            onClick={handleCycle}
            className={`theme-toggle ${className}`}
            title="Cycle theme: Light → Dark → System"
            aria-label={`Current theme: ${getLabel()}`}
        >
            <span className="theme-icon" role="img" aria-hidden="true">
                {getIcon()}
            </span>
            {showLabel && (
                <span className="theme-label">{getLabel()}</span>
            )}
        </button>
    );
};

// Extend Window interface for TypeScript
declare global {
    interface Window {
        themeManager?: {
            mode: ThemeMode;
            cycle: () => void;
            setMode: (mode: ThemeMode) => void;
            getInfo: () => ThemeInfo;
            getEffectiveTheme: () => 'light' | 'dark';
        };
    }
}
