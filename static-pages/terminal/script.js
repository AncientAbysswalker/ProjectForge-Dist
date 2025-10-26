import { validGoldenPaths } from './validGoldenPaths.js';

// Golden Path validation state
const GOLDEN_PATH_TIMEOUT = 5 * 1000; // 5 seconds
let currentTime = 0;
let currentIndex = 0;
let remainingPaths = [];

// Golden Path validation function (moved from GoldenPathManager.js)
function validateGoldenPath(arrowKey) {
    // Check if we've waited too long for the next input. If so, set our pointer to the start and re-initiate the available list of valid golden paths
    const now = Date.now();
    if (now - currentTime > GOLDEN_PATH_TIMEOUT) {
        currentIndex = 0;
        remainingPaths = validGoldenPaths.slice(0);
        console.log("Resetting golden path validation due to timeout.");
    }

    // Regardless, set time to now
    currentTime = now;

    // Check available list of valid golden paths from end to start
    for (let i = remainingPaths.length - 1; i >= 0; i--) {
        let possiblePath = remainingPaths[i];

        // If the pressed arrow key does not match, then remove the possibility from the list
        console.log(possiblePath['path'][currentIndex]);
        console.log(arrowKey);
        console.log("------");
        if (possiblePath['path'][currentIndex] != arrowKey) {
            remainingPaths.splice(i, 1);

            // If the pressed arrow key does match and it is the final entry in the possibility, run the associated action
        } else if (possiblePath['path'].length == currentIndex + 1) {
            possiblePath['action'](null); // Pass null since we don't have gpm reference in debug window
        }
    }

    console.log("Remaining paths after validation:", remainingPaths);

    currentIndex += 1;
}

function arrowTextToArrow(arrowText) {
    switch (arrowText) {
        case 'UP ARROW':
            return '🡱';
        case 'DOWN ARROW':
            return '🡳';
        case 'LEFT ARROW':
            return '🡰';
        case 'RIGHT ARROW':
            return '🡲';
        case 'UP AND RIGHT':
            return '🡵';
        case 'UP AND LEFT':
            return '🡴';
        case 'DOWN AND RIGHT':
            return '🡶';
        case 'DOWN AND LEFT':
            return '🡷';
        case 'INVALID':
            return '?';
      default:
        return arrowText;
    }
}

const textColor = '#b1fd00';
const textShadowColor = '#e2ffb7';
const textShadowStyle = (color) => `1px 1px 2px ${color}, 0 0 1em ${color}, 0 0 0.2em ${color}`;
const screenColor = '#008000';

const inputText = document.getElementById("input");
const cursorText = document.getElementById("cursor");

// --- Standalone key event handling ---
let bufferActive = false;
let buf0, buf1;
let bufferChars = ['', '']; // Always two slots for buffer display

function handleArrowKey(arrowText) {
    console.log("Handling arrow key:", arrowText);
    const arrow = arrowTextToArrow(arrowText);
    inputText.innerText = inputText.innerText + arrow;
    
    // Call golden path validation with the arrow key
    validateGoldenPath(arrowText);
    
    startCountdown();
}

function handleBufferArrowKey(arrowText) {
    const arrow = arrowTextToArrow(arrowText);
    bufferChars[0] = bufferChars[1];
    bufferChars[1] = arrow;
    renderBufferCursor();
}

function bufferOn() {
    bufferChars = ['', ''];
    renderBufferCursor();
    cursorText.classList.add("buffer-cursor");
    cursorText.classList.remove("blinking-cursor");
    bufferActive = true;
    buf0 = undefined;
    buf1 = undefined;
}

function renderBufferCursor() {
    // Show two slots, empty slots as &nbsp; for a solid underline
    cursorText.innerHTML = (bufferChars[0] || '&nbsp;') + (bufferChars[1] || '&nbsp;');
}

function bufferOff() {
    cursorText.innerHTML = '&nbsp;';
    cursorText.classList.add("blinking-cursor");
    cursorText.classList.remove("buffer-cursor");
    bufferActive = false;
    flushBufferToKey();
}

function addToBuffer(arrowKey) {
    buf0 = buf1;
    buf1 = arrowKey;
}

function flushBufferToKey() {
    let flush;
    if (buf0 === undefined && buf1 === undefined) {
        return;
    } else if (buf0 === undefined || buf1 === undefined) {
        flush = buf0 || buf1;
    } else if ((buf0 === 'UP ARROW' && buf1 === 'LEFT ARROW') || (buf1 === 'UP ARROW' && buf0 === 'LEFT ARROW')) {
        flush = 'UP AND LEFT';
    } else if ((buf0 === 'UP ARROW' && buf1 === 'RIGHT ARROW') || (buf1 === 'UP ARROW' && buf0 === 'RIGHT ARROW')) {
        flush = 'UP AND RIGHT';
    } else if ((buf0 === 'DOWN ARROW' && buf1 === 'RIGHT ARROW') || (buf1 === 'DOWN ARROW' && buf0 === 'RIGHT ARROW')) {
        flush = 'DOWN AND RIGHT';
    } else if ((buf0 === 'DOWN ARROW' && buf1 === 'LEFT ARROW') || (buf1 === 'DOWN ARROW' && buf0 === 'LEFT ARROW')) {
        flush = 'DOWN AND LEFT';
    } else {
        flush = 'INVALID';
    }
    buf0 = undefined;
    buf1 = undefined;
    handleArrowKey(flush);
}

// Listen for key events
document.addEventListener('keydown', (e) => {
    if (e.key === 'Shift') {
        console.log("Shift key pressed, enabling buffer mode.");
        bufferOn();
    }
    if (bufferActive && (e.key === 'ArrowUp' || e.key === 'ArrowDown' || e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
        let arrowText = '';
        switch (e.key) {
            case 'ArrowUp': arrowText = 'UP ARROW'; break;
            case 'ArrowDown': arrowText = 'DOWN ARROW'; break;
            case 'ArrowLeft': arrowText = 'LEFT ARROW'; break;
            case 'ArrowRight': arrowText = 'RIGHT ARROW'; break;
        }
        handleBufferArrowKey(arrowText);
        addToBuffer(arrowText);
        e.preventDefault();
    } else if (!bufferActive && (e.key === 'ArrowUp' || e.key === 'ArrowDown' || e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
        let arrowText = '';
        switch (e.key) {
            case 'ArrowUp': arrowText = 'UP ARROW'; break;
            case 'ArrowDown': arrowText = 'DOWN ARROW'; break;
            case 'ArrowLeft': arrowText = 'LEFT ARROW'; break;
            case 'ArrowRight': arrowText = 'RIGHT ARROW'; break;
        }
        handleArrowKey(arrowText);
        e.preventDefault();
    }
});

document.addEventListener('keyup', (e) => {
    if (e.key === 'Shift') {
        bufferOff();
    }
});

const div = document.querySelector('div');
console.log("Div element found:", div);
const style = window.getComputedStyle(div);
console.log({
    fontFamily: style.fontFamily,
    fontSize: style.fontSize,
    fontWeight: style.fontWeight,
    fontStyle: style.fontStyle
  });

// Fade out timer
let countdownTimer;

function startCountdown() {
  // Reset previous transition
  inputText.style.transition = "none";
  inputText.style.color = textColor;
  inputText.style.textShadow = textShadowStyle(textShadowColor);

  // Start transition and countdown
  setTimeout(() => {
    inputText.style.transition = "color 5s ease-in, text-shadow 5s ease-in";
    inputText.style.color = screenColor;
    inputText.style.textShadow = textShadowStyle(screenColor);
  }, 10); // Slight delay to allow transition to reset

  // Clear previous countdown if it's running
  if (countdownTimer) {
    clearTimeout(countdownTimer);
  }

  countdownTimer = setTimeout(() => {
    inputText.textContent = "";
  }, 5100); // 5 seconds fade out
}
