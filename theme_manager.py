"""
Theme Manager
Handles day/night/system theme modes with localStorage persistence
"""

from enum import Enum
from typing import Dict, Optional
import json


class ThemeMode(Enum):
    """Theme modes"""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class ThemePreset:
    """Theme color presets"""
    
    LIGHT_THEME = {
        "background": "#ffffff",
        "background_secondary": "#f5f5f5",
        "surface": "#ffffff",
        "surface_elevated": "#fafafa",
        "border": "#e0e0e0",
        "text_primary": "#1a1a1a",
        "text_secondary": "#666666",
        "text_tertiary": "#999999",
        "primary": "#0066cc",
        "primary_hover": "#0052a3",
        "primary_light": "#e6f2ff",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#3b82f6",
        "shadow": "rgba(0, 0, 0, 0.1)",
        "overlay": "rgba(0, 0, 0, 0.5)",
    }
    
    DARK_THEME = {
        "background": "#000000",
        "background_secondary": "#0a0a0a",
        "surface": "#1a1a1a",
        "surface_elevated": "#2a2a2a",
        "border": "#333333",
        "text_primary": "#ffffff",
        "text_secondary": "#cccccc",
        "text_tertiary": "#888888",
        "primary": "#0066cc",
        "primary_hover": "#0080ff",
        "primary_light": "#001a33",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#3b82f6",
        "shadow": "rgba(0, 0, 0, 0.3)",
        "overlay": "rgba(0, 0, 0, 0.75)",
    }
    
    # Day mode (optimized for bright environments)
    DAY_THEME = {
        **LIGHT_THEME,
        "background": "#fafafa",
        "background_secondary": "#f0f0f0",
        "surface": "#ffffff",
    }
    
    # Night mode (optimized for dark environments, OLED-friendly)
    NIGHT_THEME = {
        **DARK_THEME,
        "background": "#000000",
        "surface": "#0d0d0d",
        "surface_elevated": "#1a1a1a",
    }


class ThemeManager:
    """
    Manages theme preferences and provides theme data
    """
    
    def __init__(self):
        self.user_preferences: Dict[str, ThemeMode] = {}  # user_id → mode
    
    def set_user_theme(self, user_id: str, mode: ThemeMode):
        """Set theme mode for a user"""
        self.user_preferences[user_id] = mode
    
    def get_user_theme(self, user_id: str) -> ThemeMode:
        """Get theme mode for a user"""
        return self.user_preferences.get(user_id, ThemeMode.SYSTEM)
    
    def get_theme_colors(self, mode: ThemeMode) -> Dict[str, str]:
        """Get color palette for a theme mode"""
        if mode == ThemeMode.LIGHT:
            return ThemePreset.DAY_THEME
        elif mode == ThemeMode.DARK:
            return ThemePreset.NIGHT_THEME
        else:  # SYSTEM
            # Return both, client will choose based on OS preference
            return {
                "light": ThemePreset.DAY_THEME,
                "dark": ThemePreset.NIGHT_THEME,
            }
    
    def to_css_variables(self, colors: Dict[str, str]) -> str:
        """Convert theme colors to CSS variables"""
        css = ":root {\n"
        for key, value in colors.items():
            css += f"  --{key.replace('_', '-')}: {value};\n"
        css += "}\n"
        return css


# Frontend JavaScript code
THEME_MANAGER_JS = """
// theme-manager.js
/**
 * Theme Manager - Handles day/night/system theme switching
 */

class ThemeManager {
    constructor() {
        this.mode = this.loadMode();
        this.systemTheme = this.detectSystemTheme();
        this.init();
    }
    
    /**
     * Initialize theme manager
     */
    init() {
        // Apply initial theme
        this.applyTheme();
        
        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                this.systemTheme = e.matches ? 'dark' : 'light';
                if (this.mode === 'system') {
                    this.applyTheme();
                }
            });
        }
    }
    
    /**
     * Load theme mode from localStorage
     */
    loadMode() {
        const saved = localStorage.getItem('theme_mode');
        return saved || 'system';
    }
    
    /**
     * Save theme mode to localStorage
     */
    saveMode(mode) {
        localStorage.setItem('theme_mode', mode);
        this.mode = mode;
    }
    
    /**
     * Detect system theme preference
     */
    detectSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }
    
    /**
     * Get effective theme (resolves 'system' to 'light' or 'dark')
     */
    getEffectiveTheme() {
        if (this.mode === 'system') {
            return this.systemTheme;
        }
        return this.mode;
    }
    
    /**
     * Set theme mode
     * @param {string} mode - 'light', 'dark', or 'system'
     */
    setMode(mode) {
        if (!['light', 'dark', 'system'].includes(mode)) {
            console.error('Invalid theme mode:', mode);
            return;
        }
        
        this.saveMode(mode);
        this.applyTheme();
        
        // Dispatch event for other components
        window.dispatchEvent(new CustomEvent('themechange', {
            detail: {
                mode: this.mode,
                effective: this.getEffectiveTheme()
            }
        }));
    }
    
    /**
     * Apply theme to document
     */
    applyTheme() {
        const effectiveTheme = this.getEffectiveTheme();
        
        // Update data attribute
        document.documentElement.setAttribute('data-theme', effectiveTheme);
        
        // Update meta theme-color for mobile browsers
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            const bgColor = effectiveTheme === 'dark' ? '#000000' : '#ffffff';
            metaThemeColor.setAttribute('content', bgColor);
        }
        
        console.log(`Theme applied: ${this.mode} (effective: ${effectiveTheme})`);
    }
    
    /**
     * Toggle between light and dark
     */
    toggle() {
        const effectiveTheme = this.getEffectiveTheme();
        const newMode = effectiveTheme === 'dark' ? 'light' : 'dark';
        this.setMode(newMode);
    }
    
    /**
     * Cycle through all modes (light → dark → system)
     */
    cycle() {
        const modes = ['light', 'dark', 'system'];
        const currentIndex = modes.indexOf(this.mode);
        const nextIndex = (currentIndex + 1) % modes.length;
        this.setMode(modes[nextIndex]);
    }
}

// Create global instance
window.themeManager = new ThemeManager();

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}
"""


# React component
THEME_TOGGLE_REACT = """
// ThemeToggle.tsx
import React, { useState, useEffect } from 'react';

type ThemeMode = 'light' | 'dark' | 'system';

interface ThemeToggleProps {
    className?: string;
    showLabel?: boolean;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ 
    className = '', 
    showLabel = true 
}) => {
    const [mode, setMode] = useState<ThemeMode>('system');
    const [effectiveTheme, setEffectiveTheme] = useState<'light' | 'dark'>('light');
    
    useEffect(() => {
        // Initialize from themeManager
        if (window.themeManager) {
            setMode(window.themeManager.mode);
            setEffectiveTheme(window.themeManager.getEffectiveTheme());
        }
        
        // Listen for theme changes
        const handleThemeChange = (e: CustomEvent) => {
            setMode(e.detail.mode);
            setEffectiveTheme(e.detail.effective);
        };
        
        window.addEventListener('themechange', handleThemeChange as EventListener);
        return () => {
            window.removeEventListener('themechange', handleThemeChange as EventListener);
        };
    }, []);
    
    const handleCycle = () => {
        if (window.themeManager) {
            window.themeManager.cycle();
        }
    };
    
    const getIcon = () => {
        if (mode === 'system') {
            return '🖥️'; // Computer icon
        }
        return effectiveTheme === 'dark' ? '🌙' : '☀️';
    };
    
    const getLabel = () => {
        if (mode === 'system') {
            return `System (${effectiveTheme === 'dark' ? 'Dark' : 'Light'})`;
        }
        return mode === 'dark' ? 'Dark' : 'Light';
    };
    
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

// Styles
const styles = `
.theme-toggle {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
}

.theme-toggle:hover {
    background: var(--surface-elevated);
    transform: translateY(-1px);
}

.theme-toggle:active {
    transform: translateY(0);
}

.theme-icon {
    font-size: 1.25rem;
    line-height: 1;
}

.theme-label {
    font-weight: 500;
}
`;
"""


# CSS for themes
THEME_CSS = """
/* theme.css */

/* Light Theme (Day) */
[data-theme="light"] {
    --background: #fafafa;
    --background-secondary: #f0f0f0;
    --surface: #ffffff;
    --surface-elevated: #fafafa;
    --border: #e0e0e0;
    
    --text-primary: #1a1a1a;
    --text-secondary: #666666;
    --text-tertiary: #999999;
    
    --primary: #0066cc;
    --primary-hover: #0052a3;
    --primary-light: #e6f2ff;
    
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
    --info: #3b82f6;
    
    --shadow: rgba(0, 0, 0, 0.1);
    --overlay: rgba(0, 0, 0, 0.5);
    
    /* Component-specific */
    --button-bg: #ffffff;
    --button-hover: #f5f5f5;
    --button-active: #e0e0e0;
    
    --input-bg: #ffffff;
    --input-border: #d0d0d0;
    --input-focus: #0066cc;
    
    --card-bg: #ffffff;
    --card-shadow: 0 2px 8px var(--shadow);
}

/* Dark Theme (Night) */
[data-theme="dark"] {
    --background: #000000;
    --background-secondary: #0a0a0a;
    --surface: #0d0d0d;
    --surface-elevated: #1a1a1a;
    --border: #333333;
    
    --text-primary: #ffffff;
    --text-secondary: #cccccc;
    --text-tertiary: #888888;
    
    --primary: #0066cc;
    --primary-hover: #0080ff;
    --primary-light: #001a33;
    
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
    --info: #3b82f6;
    
    --shadow: rgba(0, 0, 0, 0.3);
    --overlay: rgba(0, 0, 0, 0.75);
    
    /* Component-specific */
    --button-bg: #1a1a1a;
    --button-hover: #2a2a2a;
    --button-active: #333333;
    
    --input-bg: #0d0d0d;
    --input-border: #333333;
    --input-focus: #0080ff;
    
    --card-bg: #0d0d0d;
    --card-shadow: 0 2px 8px var(--shadow);
}

/* Base styles */
body {
    background: var(--background);
    color: var(--text-primary);
    transition: background-color 0.3s ease, color 0.3s ease;
}

/* Smooth transitions for theme changes */
* {
    transition-property: background-color, border-color, color;
    transition-duration: 0.3s;
    transition-timing-function: ease;
}

/* Disable transitions on theme change to avoid flash */
.theme-changing * {
    transition: none !important;
}
"""
