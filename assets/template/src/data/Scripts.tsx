import React, { createContext, useContext, useEffect, useRef } from 'react';

// ScriptManager definition
class ScriptManager {
    constructor() {
        this.scripts = new Map();
        this.initializedScripts = new Set(); // Use a Set to track initialized script identifiers
    }

    addScript(object, script, identifier) {
        if (this.initializedScripts.has(identifier)) {
            return; // Prevent re-initialization
        }

        // Script initialization logic here
        script.NotifyOnInit();
        this.initializedScripts.add(identifier); // Mark as initialized

        // Add the script to the scripts map if not already present
        if (!this.scripts.has(object)) {
            this.scripts.set(object, []);
        }
        this.scripts.get(object).push(script);
    }

    updateScripts() {
        this.scripts.forEach((scripts, object) => {
            scripts.forEach(script => script.NotifyOnUpdate());
        });
    }

    // Implement removeScript if needed
}

// Context
export const ScriptManagerContext = createContext(null);

// Context Provider Component
export const ScriptManagerProvider = ({ children }) => {
    const scriptManager = useRef(new ScriptManager()).current;

    useEffect(() => {
        const interval = setInterval(() => {
            scriptManager.updateScripts();
        }, 1000 / 60); // update at roughly 60 fps

        return () => clearInterval(interval);
    }, [scriptManager]);

    return (
        <ScriptManagerContext.Provider value={scriptManager}>
            {children}
        </ScriptManagerContext.Provider>
    );
};

// Custom hook to use ScriptManager
export const useScriptManager = () => useContext(ScriptManagerContext);