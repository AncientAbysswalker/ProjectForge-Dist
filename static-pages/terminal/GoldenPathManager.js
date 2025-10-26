const path = require('path');

const { BrowserWindow } = require('electron');

const { GlobalKeyboardListener } = require('node-global-key-listener');
const gkl = new GlobalKeyboardListener();
var hash = require('object-hash');

const goldenPaths = require('./validGoldenPaths');
const { arrowKeys, shiftKeys, LSHIFT, RSHIFT, UP, DOWN, LEFT, RIGHT, UP_LEFT, UP_RIGHT, DOWN_LEFT, DOWN_RIGHT, INVALID } = require('./arrowKeys');

const logHashes = false;

module.exports = class GoldenPathManager {
    static pathTimeout = 5 * 1000;

    constructor(witnessManager, simplePuzzleManager) {
        // Debug Window
        this.debugWindow;

        // Valid Path Management
        this.currentTime = 0;
        this.currentIndex = 0;
        this.remainingPaths = [];

        // Other Puzzle Managers
        this.witnessManager = witnessManager;
        this.simplePuzzleManager = simplePuzzleManager;

        // Buffering Variables
        let buf0;
        let buf1;

        if (logHashes) {
            for (const goldenPath of goldenPaths) {
                const pathhash = hash(goldenPath['path']);
                console.log(pathhash);
            }
        }

        const gpm = this;
        gkl.addListener(function (e, down) {
            if (e.state == 'DOWN') {
                if (Object.values(arrowKeys).includes(e.name)) {
                    // If shift is held down we should buffer
                    if (down[LSHIFT] || down[RSHIFT]) {
                        gpm.debugSendBufferArrow(e.name);
                        gpm.addToBuffer(e.name);
                    } else {
                        gpm.pressedArrowKey(e.name);
                    }
                } else if (Object.values(shiftKeys).includes(e.name)) {
                    gpm.debugSendBufferOn();
                }
            } else if (
                e.state == 'UP' &&
                Object.values(shiftKeys).includes(e.name)
            ) {
                gpm.debugSendBufferOff();
                gpm.flushBufferToKey();
            }
        });
    }

    addToBuffer(arrowKey) {
        this.buf0 = this.buf1;
        this.buf1 = arrowKey;
    }

    flushBufferToKey() {
        let flush;
        if (this.buf0 === undefined && this.buf1 === undefined) {
            return;
        } else if (this.buf0 === undefined || this.buf1 === undefined) {
            flush = this.buf0 || this.buf1;
        } else if (this.buf0 === UP && this.buf1 === LEFT || this.buf1 === UP && this.buf0 === LEFT) {
            flush = UP_LEFT;
        } else if (this.buf0 === UP && this.buf1 === RIGHT || this.buf1 === UP && this.buf0 === RIGHT) {
            flush = UP_RIGHT;
        } else if (this.buf0 === DOWN && this.buf1 === RIGHT || this.buf1 === DOWN && this.buf0 === RIGHT) {
            flush = DOWN_RIGHT;
        } else if (this.buf0 === DOWN && this.buf1 === LEFT || this.buf1 === DOWN && this.buf0 === LEFT) {
            flush = DOWN_LEFT;
        } else {
            flush = INVALID;
        }

        this.buf0 = undefined;
        this.buf1 = undefined;
        this.pressedArrowKey(flush); 
    }

    pressedArrowKey(arrowKey) {
        // Check if we've waited too long for the next input. If so, set our pointer to the start and re-initiate the available list of valid golden paths
        const now = Date.now();
        if (now - this.currentTime > GoldenPathManager.pathTimeout) {
            this.currentIndex = 0;
            this.remainingPaths = goldenPaths.slice(0);
        }

        // Send our key to the debug if it's open
        this.debugSendArrow(arrowKey);

        // Regardless, set time to now
        this.currentTime = now;

        // Check available list of valid golden paths from end to start
        for (let i = this.remainingPaths.length - 1; i >= 0; i--) {
            let possiblePath = this.remainingPaths[i];

            // If the pressed arrow key does not match, then remove the possibility from the list
            if (possiblePath['path'][this.currentIndex] != arrowKey) {
                this.remainingPaths.splice(i, 1);

                // If the pressed arrow key does match and it is the final entry in the possibility, run the associated action
            } else if (possiblePath['path'].length == this.currentIndex + 1) {
                possiblePath['action'](this);
            }
        }

        this.currentIndex += 1;
    }
    
    debugSendArrow(arrowKey) {
        if (this.debugWindow) {
            this.debugWindow.webContents.send('arrow-pressed', arrowKey);
        }
    }
    
    debugSendBufferArrow(arrowKey) {
        if (this.debugWindow) {
            this.debugWindow.webContents.send('buffer-arrow-pressed', arrowKey);
        }
    }
    
    debugSendBufferOn() {
        if (this.debugWindow) {
            this.debugWindow.webContents.send('buffer-on');
        }
    }
    
    debugSendBufferOff() {
        if (this.debugWindow) {
            this.debugWindow.webContents.send('buffer-off');
        }
    }

    createDebugWindow() {
        if (this.debugWindow) {
            return;
        }

        // Create the debug window
        const iconPath = path.join(__dirname, 'debug_window/icon.png');
        const win = new BrowserWindow({
            useContentSize: true,
            width: 800,
            height: 500,
            resizable: false,
            minimizable: false,
            maximizable: false,
            icon: iconPath,
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false,
            },
        });
        win.removeMenu();
        win.setAlwaysOnTop(true);

        // Load debug window
        win.loadFile('golden_path/debug_window/index.html');
        this.debugWindow = win;

        win.on('close', () => {
            this.debugWindow = undefined; 
        });
    }
};
