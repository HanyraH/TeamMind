const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: 'TeamMind — Интеллектуальный помощник формирования команд',
    backgroundColor: '#0f172a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  // In development, connect to Vite dev server or load production build
  const devUrl = 'http://localhost:5173';
  const prodPath = path.join(__dirname, '../frontend/dist/index.html');

  let hasLoaded = false;
  if (process.env.NODE_ENV === 'development' || !app.isPackaged) {
    mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
      if (!hasLoaded && validatedURL.includes('localhost:5173')) {
        console.warn('Dev server not reachable at localhost:5173, falling back to dist/index.html');
        hasLoaded = true;
        mainWindow.loadFile(prodPath).catch((err) => {
          console.error('Failed to load application from dist/index.html:', err);
        });
      }
    });

    mainWindow.loadURL(devUrl).then(() => {
      hasLoaded = true;
    }).catch(() => {
      if (!hasLoaded) {
        hasLoaded = true;
        mainWindow.loadFile(prodPath).catch((err) => {
          console.error('Failed to load application from dist/index.html:', err);
        });
      }
    });
  } else {
    mainWindow.loadFile(prodPath);
  }

  // Window control IPC handlers
  ipcMain.on('window-minimize', () => mainWindow?.minimize());
  ipcMain.on('window-maximize', () => {
    if (mainWindow?.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow?.maximize();
    }
  });
  ipcMain.on('window-close', () => mainWindow?.close());

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
