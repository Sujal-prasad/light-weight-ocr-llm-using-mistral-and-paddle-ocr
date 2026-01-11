const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

function createWindow() {
    const win = new BrowserWindow({
        width: 1200,
        height: 800,
        backgroundColor: '#0f0f10', // Set a dark background so it's not a white flash
        webPreferences: { nodeIntegration: true }
    });

    const startUrl = 'http://127.0.0.1:5000';

    // Function to try loading the page
    const loadPage = () => {
        win.loadURL(startUrl).catch(() => {
            console.log("Server not ready, retrying in 1s...");
            setTimeout(loadPage, 1000); // Try again in 1 second
        });
    };

    loadPage();
}

app.whenReady().then(createWindow);