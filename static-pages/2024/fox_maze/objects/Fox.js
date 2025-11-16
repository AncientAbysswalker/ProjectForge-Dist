import { 
    checkMovingBoundingBoxesCollision, 
    moveToBoundingBoxCollisionBottom,
    moveToBoundingBoxCollisionTop,
    moveToBoundingBoxCollisionRight,
    moveToBoundingBoxCollisionLeft
} from '../helpers/collision.js';

import { DreamBubble } from './DreamBubble.js';

const state = Object.freeze({
    INITIAL_SLEEPING: 'INITIAL_SLEEPING',
    SLEEPING: 'SLEEPING',
    WAKING_UP: 'WAKING_UP',
    FALLING_ASLEEP: 'FALLING_ASLEEP',
    WALKING: 'WALKING',
    STANDING: 'STANDING',
});

const millisecondsBeforeFallingAsleep = 180000; // 3 minutes to mimic Animal Well

// Bounding Box - Static Definitions
const centerX = 16;
const centerY = 28;
const bbWidth = 20;
const bbHeight = 8;

// Bounding Box - Calculated
const bbLeftX = centerX - bbWidth / 2;
const bbRightX = centerX + bbWidth / 2;
const bbTopY = centerY - bbHeight / 2;
const bbBottomY = centerY + bbHeight / 2;

class Fox {
    constructor(engine, startingX, startingY) {
        this.engine = engine;

        // Animation Constants
        this.sprL = new Image();
        this.sprR = new Image();
        this.sprOutlineL = new Image();
        this.sprOutlineR = new Image();
        this.sprL.src = './graphics/sprites/fox_l.png';
        this.sprR.src = './graphics/sprites/fox_r.png';
        this.sprOutlineL.src = './graphics/sprites/fox_l_outline.png';
        this.sprOutlineR.src = './graphics/sprites/fox_r_outline.png';
        this.frameWidth = 32;
        this.frameHeight = 32;

        // Animation and Movement
        this.specialAnimationChance = 0.1;
        this.currentAnimationReversed;
        this.currentAnimationFrame;
        this.currentAnimationWaitFrame;
        this.engineFramesPerAnimationFrame;
        this.currentAnimationMaxFrames;
        this.currentAnimationSpritesheetRow;
        this.maxSpeed = 4;

        // State
        this.lastInteractedTime = 0;
        this.state = state.INITIAL_SLEEPING;
        this.lastState;
        this.x = startingX;
        this.y = startingY;
        this.faceRight = true;

        // Dream Bubble
        this.dreamBubble = new DreamBubble(engine);
        this.engine.addObject(this.dreamBubble);
    }

    // Bounding Box
    getBoundingLeft() {
        return this.x + bbLeftX;
    }
    getBoundingRight() {
        return this.x + bbRightX;
    }
    getBoundingTop() {
        return this.y + bbTopY;
    }
    getBoundingBottom() {
        return this.y + bbBottomY;
    }

    checkForSolidMap(x, y) {
        const xx = Math.floor(x / 32);
        const yy = Math.floor(y / 32);
        // return (xx==10 && yy==10) || (xx==10 && yy==9)|| (xx==10 && yy==8); // Check array
        return this.engine.getMapCollision(yy, xx); // Check map data
    }

    // Check Movement
    checkMoveLeft() {
        const x = this.getBoundingLeft();
        const y1 = this.getBoundingTop();
        const y2 = this.getBoundingBottom();

        // Check for map collision, then object solids, then otherwise move unrestricted
        if (this.checkForSolidMap(x - this.maxSpeed, y1) || this.checkForSolidMap(x - this.maxSpeed, y2)) {
            this.x = Math.floor(x / 32) * 32 - bbLeftX + 1;
        } else {
            let isCollided = false;
            for (const objectSolid of this.engine.getSolidObjectList()) {
                if (checkMovingBoundingBoxesCollision(this, objectSolid, - this.maxSpeed, 0)) {
                    isCollided = true;
                    moveToBoundingBoxCollisionRight(this, objectSolid);
                }
            }

            if (!isCollided) {
                this.x -= this.maxSpeed;
            }
        }
    }
    checkMoveRight() {
        const x = this.getBoundingRight();
        const y1 = this.getBoundingTop();
        const y2 = this.getBoundingBottom();

        // Check for map collision, then object solids, then otherwise move unrestricted
        if (this.checkForSolidMap(x + this.maxSpeed, y1) || this.checkForSolidMap(x + this.maxSpeed, y2)) {
            this.x = Math.floor((x + this.maxSpeed) / 32) * 32 - bbRightX - 1;
        } else {
            let isCollided = false;
            for (const objectSolid of this.engine.getSolidObjectList()) {
                if (checkMovingBoundingBoxesCollision(this, objectSolid, this.maxSpeed, 0)) {
                    isCollided = true;
                    moveToBoundingBoxCollisionLeft(this, objectSolid);
                }
            }

            if (!isCollided) {
                this.x += this.maxSpeed;
            }
        }
    }
    checkMoveUp() {
        const y = this.getBoundingTop();
        const x1 = this.getBoundingLeft();
        const x2 = this.getBoundingRight();

        // Check for map collision, then object solids, then otherwise move unrestricted
        if (this.checkForSolidMap(x1, y - this.maxSpeed) || this.checkForSolidMap(x2, y - this.maxSpeed)) {
            this.y = Math.floor(y / 32) * 32 -bbTopY + 1;
        } else {
            let isCollided = false;
            for (const objectSolid of this.engine.getSolidObjectList()) {
                if (checkMovingBoundingBoxesCollision(this, objectSolid, 0, - this.maxSpeed)) {
                    isCollided = true;
                    moveToBoundingBoxCollisionBottom(this, objectSolid);
                }
            }

            if (!isCollided) {
                this.y -= this.maxSpeed;
            }
        }
    }
    checkMoveDown() {
        const y = this.getBoundingBottom();
        const x1 = this.getBoundingLeft();
        const x2 = this.getBoundingRight();

        // Check for map collision, then object solids, then otherwise move unrestricted
        if (this.checkForSolidMap(x1, y + this.maxSpeed) || this.checkForSolidMap(x2, y + this.maxSpeed)) {
            this.y = Math.floor((y + this.maxSpeed) / 32) * 32 - bbBottomY - 1;
        } else {
            let isCollided = false;
            for (const objectSolid of this.engine.getSolidObjectList()) {
                if (checkMovingBoundingBoxesCollision(this, objectSolid, 0, this.maxSpeed)) {
                    isCollided = true;
                    moveToBoundingBoxCollisionTop(this, objectSolid);
                }
            }

            if (!isCollided) {
                this.y += this.maxSpeed;
            }
        }
    }

    checkForSpriteStateUpdate() {
        // If state changed, cut to new animation
        if (this.lastState != this.state) {
            this.lastState = this.state;

            switch(this.state)
            {
                case state.STANDING:
                    this.currentAnimationReversed = false;
                    this.engineFramesPerAnimationFrame = 3;
                    this.currentAnimationMaxFrames = 5;
                    this.currentAnimationSpritesheetRow = 0;
                    break;
                case state.WALKING:
                    this.currentAnimationReversed = false;
                    this.engineFramesPerAnimationFrame = 3;
                    this.currentAnimationMaxFrames = 8;
                    this.currentAnimationSpritesheetRow = 2;
                    break;
                case state.INITIAL_SLEEPING:
                case state.SLEEPING:
                    this.currentAnimationReversed = false;
                    this.engineFramesPerAnimationFrame = 9;
                    this.currentAnimationMaxFrames = 6;
                    this.currentAnimationSpritesheetRow = 4;
                    break;
                case state.WAKING_UP:
                    this.currentAnimationReversed = true;
                    this.engineFramesPerAnimationFrame = 3;
                    this.currentAnimationMaxFrames = 6;
                    this.currentAnimationSpritesheetRow = 3;
                    break;
                case state.FALLING_ASLEEP:
                    this.currentAnimationReversed = false;
                    this.engineFramesPerAnimationFrame = 3;
                    this.currentAnimationMaxFrames = 6;
                    this.currentAnimationSpritesheetRow = 3;
                    break;
            }
            this.currentAnimationFrame = 0;
            this.currentAnimationWaitFrame = 0;
        }
    }

    setupNextAnimationFrame() {
        // Continue to wait is there remain wait frames
        if (this.currentAnimationWaitFrame != this.engineFramesPerAnimationFrame) {
            this.currentAnimationWaitFrame++;
            
        // Else move to setup next frame and reset current wait frame to 0
        } else {
            this.currentAnimationWaitFrame = 0;

            // Update chance for special animation
            if (this.specialAnimationChance < 0.1) {
                this.specialAnimationChance += 0.0001; // Appx 30sec to refill
            }

            // Special handling for end of animation
            if (this.currentAnimationFrame == this.currentAnimationMaxFrames - 1) {
                // Transition to standing at end of wake up
                if (this.state == state.WAKING_UP) {
                    this.updateState(state.STANDING);
                    return;
                }

                // Transition to sleeping at end of falling asleep
                if (this.state == state.FALLING_ASLEEP) {
                    this.updateState(state.SLEEPING);
                    this.dreamBubble.startDreaming(this.x, this.y);
                    return;
                }

                // Transition to falling asleep if too idle
                if ((this.state != state.INITIAL_SLEEPING && this.state != state.SLEEPING)
                    && (this.engine.timestamp - this.lastInteractedTime > millisecondsBeforeFallingAsleep)) {
                    this.updateState(state.FALLING_ASLEEP);
                    return;
                }

                // Special alternate resting animation
                if (this.state == state.STANDING) {
                    // Potentially start special animation, else end it
                    if (this.currentAnimationSpritesheetRow == 0 && Math.random() < this.specialAnimationChance) {
                        this.specialAnimationChance = 0;
                        this.currentAnimationMaxFrames = 14;
                        this.currentAnimationSpritesheetRow = 1;
                    } else {
                        this.currentAnimationMaxFrames = 5;
                        this.currentAnimationSpritesheetRow = 0;
                    }
                }

                // Reset animation at end of animation
                this.currentAnimationFrame = 0;
                return;
            }
            
            // Progress to next frame of current animation
            this.currentAnimationFrame++;
        }
    }

    draw() {
        // Check fox sprite for state update
        this.checkForSpriteStateUpdate();

        // Draw fox
        this.engine.submitImageForDraw(10,
            this.faceRight ? this.sprR : this.sprL, 
            this.frameWidth * (this.currentAnimationReversed 
                ? this. currentAnimationMaxFrames - this.currentAnimationFrame - 1
                : this.currentAnimationFrame),
            this.currentAnimationSpritesheetRow*this.frameHeight, 
            this.frameWidth, 
            this.frameHeight, 
            this.x - this.engine.winX, 
            this.y - this.engine.winY, 
            this.frameWidth, 
            this.frameHeight);

        // Draw fox outline
        this.engine.submitImageForDraw(60,
            this.faceRight ? this.sprOutlineR : this.sprOutlineL, 
            this.frameWidth * (this.currentAnimationReversed 
                ? this. currentAnimationMaxFrames - this.currentAnimationFrame - 1
                : this.currentAnimationFrame),
            this.currentAnimationSpritesheetRow*this.frameHeight, 
            this.frameWidth, 
            this.frameHeight, 
            this.x - this.engine.winX, 
            this.y - this.engine.winY, 
            this.frameWidth, 
            this.frameHeight);

            
        if (this.engine.drawHitboxes) {
            this.engine.submitBoundingBoxForDraw(99, "red",
                this.x + bbLeftX - this.engine.winX, 
                this.y + bbTopY - this.engine.winY, 
                bbWidth, 
                bbHeight);
        }
        
        // Setup properties for next rendered frame
        this.setupNextAnimationFrame();    
    }

    update() {
        if (this.state == state.STANDING || this.state == state.WALKING) {
            if (keyPressed["left"] || keyPressed["right"] || keyPressed["up"] || keyPressed["down"]) {
                this.lastInteractedTime = this.engine.timestamp;

                if (keyPressed["left"] != keyPressed["right"]) {
                    // Left
                    if (keyPressed["left"]) {
                        this.faceRight = false;
                        this.updateState(state.WALKING);
                        this.checkMoveLeft();
                    }
                    // Right
                    if (keyPressed["right"]) {
                        this.faceRight = true;
                        this.updateState(state.WALKING);
                        this.checkMoveRight();
                    }
                }
                if (keyPressed["up"] != keyPressed["down"]) {
                    // Up
                    if (keyPressed["up"]) {
                        this.updateState(state.WALKING);
                        this.checkMoveUp();
                    }
                    // Down
                    if (keyPressed["down"]) {
                        this.updateState(state.WALKING);
                        this.checkMoveDown();
                    }
                }
            } else {
                if (this.state === state.WALKING) {
                    this.updateState(state.STANDING);
                }
            }
        } else {
            if (keyPressed["left"] || keyPressed["right"] || keyPressed["up"] || keyPressed["down"]) {
                this.lastInteractedTime = this.engine.timestamp;
                
                // If the fox is visible in the original 160x160 pane (10px of give) then wake up
                if (this.state == state.SLEEPING || 
                    (this.state == state.INITIAL_SLEEPING // Only restrict for the initial
                    && (this.x + bbLeftX - this.engine.winX > -10
                        && this.x + bbRightX - this.engine.winX < 170 // CANVAS W
                        && this.y + bbTopY - this.engine.winY > -10
                        && this.y + bbBottomY - this.engine.winY < 170))) { // CANVAS H
                    this.updateState(state.WAKING_UP);
                    this.dreamBubble.wakeUp();
                }
            }
        }
    }

    updateState(newState) {
        if (newState !== this.state) {
            this.state = newState;
        }
    }
}

// Keyboard event handlers for movement
var keyPressed = {};
window.addEventListener("keydown", (e) => {
    console.log(e)
    // All the extra repeated-logic is to reduce input lag
    if (e.repeat) { return }

    if (!keyPressed["up"] && (e.key === "W" || e.key === "w")) {
        keyPressed["up"] = true;
    }
    if (!keyPressed["down"] && (e.key === "S" || e.key === "s")) {
        keyPressed["down"] = true;
    }
    if (!keyPressed["left"] && (e.key === "A" || e.key === "a")) {
        keyPressed["left"] = true;
    }
    if (!keyPressed["right"] && (e.key === "D" || e.key === "d")) {
        keyPressed["right"] = true;
    }
});

window.addEventListener("keyup", (e) => {
    if (e.key === "W" || e.key === "w") {
        keyPressed["up"] = false;
    }
    if (e.key === "S" || e.key === "s") {
        keyPressed["down"] = false;
    }
    if (e.key === "A" || e.key === "a") {
        keyPressed["left"] = false;
    }
    if (e.key === "D" || e.key === "d") {
        keyPressed["right"] = false;
    }
});

export { Fox };
