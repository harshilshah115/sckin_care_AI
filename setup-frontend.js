const fs = require('fs');
const path = require('path');
const basePath = 'd:\\Harshil Projects\\Sckin Care\\frontend';

// Create all directories
const dirs = [
  basePath,
  path.join(basePath, 'src'),
  path.join(basePath, 'src', 'components'),
  path.join(basePath, 'src', 'pages'),
  path.join(basePath, 'src', 'styles'),
  path.join(basePath, 'src', 'context'),
  path.join(basePath, 'src', 'hooks'),
  path.join(basePath, 'src', 'services'),
  path.join(basePath, 'src', 'assets'),
  path.join(basePath, 'public'),
];

dirs.forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// File contents
const packageJson = {
  name: "skincare-frontend",
  private: true,
  version: "0.0.1",
  type: "module",
  scripts: {
    dev: "vite",
    build: "vite build",
    lint: "eslint .",
    preview: "vite preview"
  },
  dependencies: {
    react: "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.28.0"
  },
  devDependencies: {
    "@vitejs/plugin-react": "^4.3.3",
    vite: "^5.4.10"
  }
};

const files = {
  'package.json': JSON.stringify(packageJson, null, 2),
  'vite.config.js': `import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  }
})`,
  'index.html': `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@200;300;400;500;600;700;800&display=swap" rel="stylesheet" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
    <title>Lumière Clinical | AI Skincare Assistant</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"><\/script>
  </body>
</html>`,
  'src/main.jsx': `import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import App from './App'
import './index.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <App />
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
)`,
  'src/App.jsx': `import { Routes, Route } from 'react-router-dom'
import './App.css'

function App() {
  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<div>Landing Page</div>} />
      </Routes>
    </div>
  )
}

export default App`,
  'src/App.css': `/* App specific styles */
.app {
  min-height: 100vh;
}`,
  'src/index.css': `/* Root Variables for Dark Theme (Nocturne) */
:root {
  --surface: #0b1326;
  --surface-container-highest: #2d3449;
  --surface-bright: #31394d;
  --surface-container-high: #222a3d;
  --surface-container-low: #131b2e;
  --surface-container-lowest: #060e20;
  --surface-container: #171f33;
  --surface-variant: #2d3449;
  
  --primary: #4edea3;
  --primary-container: #10b981;
  --primary-fixed: #6ffbbe;
  --primary-fixed-dim: #4edea3;
  
  --secondary: #b0ceb4;
  --secondary-container: #334d38;
  
  --tertiary: #ffb3af;
  --tertiary-container: #fc7c78;
  
  --on-surface: #dae2fd;
  --on-surface-variant: #bbcabf;
  --on-primary: #003824;
  --on-primary-container: #00422b;
  --on-secondary-container: #9fbca3;
  
  --outline: #86948a;
  --outline-variant: #3c4a42;
  
  --error: #ffb4ab;
  --error-container: #93000a;
  
  --background: #0b1326;
  --on-background: #dae2fd;
  
  --font-headline: 'Manrope', sans-serif;
  --font-body: 'Manrope', sans-serif;
  --font-label: 'Manrope', sans-serif;
  
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-2xl: 1.5rem;
  --radius-full: 9999px;
}

.light {
  --surface: #fefee5;
  --surface-container-highest: #e8ebc0;
  --surface-bright: #fefee5;
  --surface-container-high: #eef1cb;
  --surface-container-low: #fbfcdc;
  --surface-container-lowest: #ffffff;
  --surface-container: #f4f6d2;
  --surface-variant: #e8ebc0;
  
  --primary: #4a6c4f;
  --primary-container: #c6ecc8;
  --primary-fixed: #c6ecc8;
  --primary-fixed-dim: #b8debb;
  
  --secondary: #6d6350;
  --secondary-container: #efe1c9;
  
  --tertiary: #5b675e;
  --tertiary-container: #e7f4e8;
  
  --on-surface: #373a1c;
  --on-surface-variant: #636745;
  --on-primary: #ffffff;
  --on-primary-container: #38593e;
  --on-secondary-container: #5a513f;
  
  --outline: #80835f;
  --outline-variant: #b9bc94;
  
  --error: #af3d3b;
  --error-container: #fa746f;
  
  --background: #fefee5;
  --on-background: #373a1c;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-body);
  background-color: var(--background);
  color: var(--on-surface);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-headline);
}

a {
  text-decoration: none;
  color: inherit;
}

button {
  cursor: pointer;
  border: none;
  font-family: inherit;
}

img {
  max-width: 100%;
  display: block;
}

::selection {
  background-color: rgba(78, 222, 163, 0.3);
  color: var(--primary);
}

.glass-card {
  background: rgba(45, 52, 73, 0.4);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.light .glass-card {
  background: rgba(255, 255, 255, 0.6);
}

.text-glow {
  text-shadow: 0 0 20px rgba(78, 222, 163, 0.3);
}

.light .text-glow {
  text-shadow: 0 0 20px rgba(74, 108, 79, 0.2);
}

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}`,
  'src/context/ThemeContext.jsx': `import { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext()

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('theme')
    return saved || 'dark'
  })

  useEffect(() => {
    localStorage.setItem('theme', theme)
    document.documentElement.classList.remove('light', 'dark')
    document.documentElement.classList.add(theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark')
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)`,
  'src/styles/variables.css': `/* Global CSS variables for consistent theming */`,
  'public/vite.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#4edea3"/>
  <text x="50" y="60" text-anchor="middle" fill="#003824" font-size="30" font-family="sans-serif">L</text>
</svg>`,
  'src/components/.gitkeep': '',
  'src/pages/.gitkeep': '',
  'src/hooks/.gitkeep': '',
  'src/services/.gitkeep': '',
  'src/assets/.gitkeep': '',
};

Object.entries(files).forEach(([filePath, content]) => {
  const fullPath = path.join(basePath, filePath);
  fs.writeFileSync(fullPath, content, 'utf-8');
});

console.log('✓ Frontend structure created successfully!');
