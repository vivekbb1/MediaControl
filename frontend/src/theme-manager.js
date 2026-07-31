/**
 * Theme Manager
 * Handles day/night/system theme switching with localStorage persistence
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
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            // Modern browsers
            if (mediaQuery.addEventListener) {
                mediaQuery.addEventListener('change', (e) => {
                    this.systemTheme = e.matches ? 'dark' : 'light';
                    if (this.mode === 'system') {
                        this.applyTheme();
                    }
                });
            }
            // Legacy browsers
            else if (mediaQuery.addListener) {
                mediaQuery.addListener((e) => {
                    this.systemTheme = e.matches ? 'dark' : 'light';
                    if (this.mode === 'system') {
                        this.applyTheme();
                    }
                });
            }
        }
        
        // Listen for storage changes (multi-tab sync)
        window.addEventListener('storage', (e) => {
            if (e.key === 'theme_mode') {
                this.mode = e.newValue || 'system';
                this.applyTheme();
            }
        });
    }
    
    /**
     * Load theme mode from localStorage
     */
    loadMode() {
        try {
            const saved = localStorage.getItem('theme_mode');
            if (saved && ['light', 'dark', 'system'].includes(saved)) {
                return saved;
            }
        } catch (e) {
            console.warn('Failed to load theme from localStorage:', e);
        }
        return 'system';
    }
    
    /**
     * Save theme mode to localStorage
     */
    saveMode(mode) {
        try {
            localStorage.setItem('theme_mode', mode);
        } catch (e) {
            console.warn('Failed to save theme to localStorage:', e);
        }
        this.mode = mode;
    }
    
    /**
     * Detect system theme preference
     */
    detectSystemTheme() {
        if (window.matchMedia) {
            if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
                return 'dark';
            }
            if (window.matchMedia('(prefers-color-scheme: light)').matches) {
                return 'light';
            }
        }
        // Default to light if no preference
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
        
        const oldEffective = this.getEffectiveTheme();
        this.saveMode(mode);
        const newEffective = this.getEffectiveTheme();
        
        // Add transition class temporarily
        if (oldEffective !== newEffective) {
            document.documentElement.classList.add('theme-changing');
        }
        
        this.applyTheme();
        
        // Remove transition class after animation
        setTimeout(() => {
            document.documentElement.classList.remove('theme-changing');
        }, 50);
        
        // Dispatch event for other components
        const event = new CustomEvent('themechange', {
            detail: {
                mode: this.mode,
                effective: this.getEffectiveTheme(),
                previous: oldEffective
            }
        });
        window.dispatchEvent(event);
        
        console.log(`Theme changed: ${this.mode} (effective: ${this.getEffectiveTheme()})`);
    }
    
    /**
     * Apply theme to document
     */
    applyTheme() {
        const effectiveTheme = this.getEffectiveTheme();
        
        // Update data attribute
        document.documentElement.setAttribute('data-theme', effectiveTheme);
        
        // Update meta theme-color for mobile browsers
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        const bgColor = effectiveTheme === 'dark' ? '#000000' : '#ffffff';
        metaThemeColor.setAttribute('content', bgColor);
        
        // Update body class for legacy support
        document.body.classList.remove('theme-light', 'theme-dark');
        document.body.classList.add(`theme-${effectiveTheme}`);
    }
    
    /**
     * Toggle between light and dark (skips system)
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
    
    /**
     * Get current mode info
     */
    getInfo() {
        return {
            mode: this.mode,
            effective: this.getEffectiveTheme(),
            system: this.systemTheme,
            isDark: this.getEffectiveTheme() === 'dark',
            isLight: this.getEffectiveTheme() === 'light',
            isSystem: this.mode === 'system'
        };
    }
}

// Initialize theme manager on load
let themeManager;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        themeManager = new ThemeManager();
        window.themeManager = themeManager;
    });
} else {
    themeManager = new ThemeManager();
    window.themeManager = themeManager;
}

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}

// Export for ES6
if (typeof exports !== 'undefined') {
    exports.ThemeManager = ThemeManager;
}
