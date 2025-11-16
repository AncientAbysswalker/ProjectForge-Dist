import { checkBoundingBoxesCollision } from '../helpers/collision.js';
import { COLOR } from '../helpers/color.js';

const state = Object.freeze({
    CLOSED: 'CLOSED',
    OPENING: 'OPENING',
    OPEN: 'OPEN',
});

// Audio
const audio = new Audio('sounds/chest.mp3');

// Bounding Box - Static Definitions
const centerX = 16;
const centerY = 20;
const bbWidth = 18;
const bbHeight = 16;
const activationDistance = 2;

// Bounding Box - Calculated
const bbLeftX = centerX - bbWidth / 2;
const bbRightX = centerX + bbWidth / 2;
const bbTopY = centerY - bbHeight / 2;
const bbBottomY = centerY + bbHeight / 2;
class Chest {
    constructor(engine, startingX, startingY, color, key) {
        this.engine = engine;
        this.key = key;
        
        // Animation Constants
        this.spr = new Image();
        this.spr = new Image();
        switch(color) {
            case COLOR.RED:
                this.spr.src = 'graphics/sprites/chest_red.png';
                break;
            case COLOR.BLUE:
                this.spr.src = 'graphics/sprites/chest_blue.png';
                break;
            case COLOR.GREEN:
                this.spr.src = 'graphics/sprites/chest_green.png';
                break;
            default:
                throw new Error(`Invalid color provided: ${color}`);
        }
        this.sprWidth = 32;
        this.sprHeight = 32;
        this.sprHeightCutline = 16;

        // Animation and Movement
        this.currentAnimationFrame = 0;
        this.currentAnimationLockFrame;
        this.currentAnimationWaitFrame = 0;
        this.engineFramesPerAnimationFrame = 3;
        this.currentAnimationMaxFrames = 6;

        // State
        this.state = state.CLOSED;
        this.lastState;
        this.x = startingX;
        this.y = startingY;
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

    update() {
        if (!this.isOpened() && checkBoundingBoxesCollision(this, this.key)) {
            // Expand the canvas viewport
            const canvas = document.getElementById('canvas');
            const newSize = Math.min(canvas.width + 112, 384); // Grow by 112px, max 384px
            canvas.width = newSize;
            canvas.height = newSize;
            
            audio.currentTime = 0;
            audio.play();
            this.updateState(state.OPENING);
            this.key.consume();
        }
    }

    draw() {
        // Check sprite for state update
        this.checkForSpriteStateUpdate();

        // Top half of sprite
        this.engine.submitImageForDraw(20,
            this.spr, 
            this.currentAnimationFrame * this.sprWidth, 
            0, 
            this.sprWidth, 
            this.sprHeightCutline, 
            this.x - this.engine.winX, 
            this.y - this.engine.winY, 
            this.sprWidth, 
            this.sprHeightCutline);

        // Top half of sprite
        this.engine.submitImageForDraw(5,
            this.spr, 
            this.currentAnimationFrame * this.sprWidth, 
            this.sprHeightCutline, 
            this.sprWidth, 
            this.sprHeight - this.sprHeightCutline, 
            this.x - this.engine.winX, 
            this.y + this.sprHeightCutline - this.engine.winY, 
            this.sprWidth, 
            this.sprHeight - this.sprHeightCutline);

        // Draw Hitboxes
        if (this.engine.drawHitboxes) {
            // Draw collision hitbox
            this.engine.submitBoundingBoxForDraw(99, "red",
                this.x + bbLeftX - this.engine.winX, 
                this.y + bbTopY - this.engine.winY, 
                bbWidth, 
                bbHeight);

            // Draw activation hitbox
            this.engine.submitBoundingBoxForDraw(99, "blue",
                this.x + bbLeftX - activationDistance - this.engine.winX, 
                this.y + bbTopY - activationDistance - this.engine.winY, 
                bbWidth + 2* activationDistance, 
                bbHeight + 2* activationDistance);
        }
        
        // Setup properties for next rendered frame
        this.setupNextAnimationFrame();    
    }

    checkForSpriteStateUpdate() {
        // If state changed, cut to new animation
        if (this.lastState != this.state) {
            this.lastState = this.state;

            switch(this.state)
            {
                case state.CLOSED:
                    this.currentAnimationLockFrame = true;
                    this.currentAnimationFrame = 0;
                    break;
                case state.OPENING:
                    this.currentAnimationLockFrame = false;
                    this.currentAnimationFrame = 0;
                    break;
                case state.OPEN:
                    this.currentAnimationLockFrame = true;
                    this.currentAnimationFrame = this.currentAnimationMaxFrames - 1;
                    break;
            } 
            this.currentAnimationWaitFrame = 0;
        }
    }

    setupNextAnimationFrame() {
        // Skip frame checks if we have locked animation to a frame
        if (this.currentAnimationLockFrame) {
            return;
        }

        // Continue to wait is there remain wait frames
        if (this.currentAnimationWaitFrame != this.engineFramesPerAnimationFrame) {
            this.currentAnimationWaitFrame++;
            
        // Else move to setup next frame and reset current wait frame to 0
        } else {
            this.currentAnimationWaitFrame = 0;
            
            // Special handling for end of animation
            if (this.currentAnimationFrame == this.currentAnimationMaxFrames - 1) {
                // Transition to open at end of opening
                if (this.state == state.OPENING) {
                    this.updateState(state.OPEN);
                    return;
                }

                // Reset animation at end of animation
                this.currentAnimationFrame = 0;
                return;
            }

            this.currentAnimationFrame++;
        }
    }

    isOpened() {
        return this.state === state.OPEN || this.state === state.OPENING;
    }

    updateState(newState) {
        if (newState !== this.state) {
            this.state = newState;
        }
    }
}

export { Chest };
