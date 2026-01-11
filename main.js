const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let flaskProcess = null;

// --- 1. FUNCTION TO START PYTHON BACKEND ---
function startFlask() {
    console.log("Starting Flask Backend...");
    
    // Adjust 'python' to 'python3' if you are on Mac/Linux
    // If using a venv, ensure you run 'npm start' from the activated terminal
    const scriptPath = path.join(__dirname, 'app.py');
    flaskProcess = spawn('python', [scriptPath]);

    // Pipe Python output to the Electron console for debugging
    flaskProcess.stdout.on('data', (data) => {
        console.log(`Flask: ${data}`);
    });

    flaskProcess.stderr.on('data', (data) => {
        console.error(`Flask Error: ${data}`);
    });

    flaskProcess.on('close', (code) => {
        console.log(`Flask process exited with code ${code}`);
    });
}

function createWindow() {
    const win = new BrowserWindow({
        width: 1200,
        height: 800,
        backgroundColor: '#0f0f10', // Set a dark background so it's not a white flash
        webPreferences: { nodeIntegration: true }
    });

    const startUrl = 'http://127.0.0.1:5000';

    // --- 2. RETRY LOGIC (Waits for Flask to boot) ---
    const loadPage = () => {
        win.loadURL(startUrl).catch(() => {
            console.log("Server not ready, retrying in 1s...");
            setTimeout(loadPage, 1000); // Try again in 1 second
        });
    };

    loadPage();
}

// --- 3. APP LIFECYCLE ---

app.whenReady().then(() => {
    startFlask();    // Start Python first
    createWindow();  // Then open the UI
});

// Quit when all windows are closed (Windows/Linux standard)
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// --- 4. CLEANUP: KILL PYTHON ON EXIT ---
app.on('will-quit', () => {
    if (flaskProcess) {
        console.log("Killing Flask Process...");
        flaskProcess.kill();
        flaskProcess = null;
    }
});