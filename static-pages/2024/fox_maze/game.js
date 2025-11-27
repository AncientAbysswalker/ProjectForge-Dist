import { COLOR } from './helpers/color.js';
import { Chest } from './objects/Chest.js';
import { Key } from './objects/Key.js';
import { Fox } from './objects/Fox.js';
import { MusicNote } from './objects/MusicNote.js';
import { Engine } from './Engine.js';

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

const debug = false;

// Map data is stored with indices of row then col
const mapCollisionResponse = await fetch('./map.json');
const mapCollision = await mapCollisionResponse.json();

// Map
let map_lower = new Image();
let map_upper = new Image();
map_lower.src = 'graphics/map/layer_lower.png';
map_upper.src = 'graphics/map/layer_upper.png';

const engine = new Engine(canvas, ctx, 50, 50, debug);
engine.setBackgroundColor("#00E098");
engine.setMapCollision(mapCollision);
engine.addMapLayer(map_lower, 0, 0, -32);
engine.addMapLayer(map_upper, 50, 0, -32);

// Define Keys and Chests
let keyLocations = {};
let chestLocations = {};
keyLocations[COLOR.RED] = debug ? { x: 32, y: 27 } : { x: 3, y: 29 };
chestLocations[COLOR.RED] = { x: 32, y: 28 };
keyLocations[COLOR.BLUE] = debug ? { x: 30, y: 27 } : { x: 33, y: 5 };
chestLocations[COLOR.BLUE] = { x: 30, y: 28 };
keyLocations[COLOR.GREEN] = debug ? { x: 34, y: 27 } : { x: 57, y: 14 };
chestLocations[COLOR.GREEN] = { x: 34, y: 28 };

// Register Keys and Chests - Colors must match
Object.keys(keyLocations).forEach((color, index) => {
    const key = new Key(engine, keyLocations[color].x * 32, keyLocations[color].y * 32 - 12, color, index);
    const chest = new Chest(engine, chestLocations[color].x * 32, chestLocations[color].y * 32, color, key);

    engine.addObject(key);
    engine.addSolidObject(chest);
});

// Fun music note
const musicLocation = debug ? { x: 31, y: 26 } : { x: 43, y: 29 };
const musicNote = new MusicNote(engine, musicLocation.x * 32, musicLocation.y * 32 - 12);
engine.addObject(musicNote);

const foxLocation = debug ? { x: 27, y: 29 } : { x: 2, y: 14 };
let fox = new Fox(engine, foxLocation.x * 32, foxLocation.y * 32 - 2); // -2 to prevent collision at initial spawn location
engine.setPlayerObject(fox);

engine.startEngine();

canvas.addEventListener('click', engine.clickEvent, false);

// Canvas dragging to move viewport
let isDragging = false;
let dragStartX = 0;
let dragStartY = 0;
let viewportStartX = 0;
let viewportStartY = 0;

canvas.addEventListener('mousedown', (e) => {
    isDragging = true;
    dragStartX = e.clientX;
    dragStartY = e.clientY;
    viewportStartX = engine.winX;
    viewportStartY = engine.winY;
    canvas.style.cursor = 'grabbing';
});

window.addEventListener('mousemove', (e) => {
    if (isDragging) {
        const deltaX = dragStartX - e.clientX;
        const deltaY = dragStartY - e.clientY;
        engine.setWindowPosition(viewportStartX + deltaX, viewportStartY + deltaY);
    }
});

window.addEventListener('mouseup', () => {
    isDragging = false;
    canvas.style.cursor = 'grab';
});

canvas.style.cursor = 'grab';
canvas.focus();

// Allows for touch handling for panning
window.getEngine = () => engine;