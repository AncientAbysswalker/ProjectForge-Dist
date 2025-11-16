import { checkPointToBoundingBoxCollision } from '../helpers/collision.js';

const state = Object.freeze({
    OFFSCREEN: 'OFFSCREEN',
    DREAMING: 'DREAMING',
    FROZEN: 'FROZEN'
});

// Bounding Box - Player - Static Definitions
let boundingData = {
    centerX: 21,
    centerY: 11,
    bbWidth: 12,
    bbHeight: 12
}
boundingData = {
    ...boundingData,
    bbLeftX: boundingData.centerX - boundingData.bbWidth / 2,
    bbRightX: boundingData.centerX + boundingData.bbWidth / 2,
    bbTopY: boundingData.centerY - boundingData.bbHeight / 2,
    bbBottomY: boundingData.centerY + boundingData.bbHeight / 2
};

class DreamBubble {
    constructor(engine) {
        this.engine = engine;
        this.engine.registerClickable(this);
        
        // Animation Constants
        this.spr = new Image();
        this.spr.src = 'graphics/sprites/dream_bubble.png';
        this.sprWidth = 32;
        this.sprHeight = 32;

        // Animation and Movement
        this.currentAnimationFrame = 0;
        this.currentAnimationLockFrame;
        this.currentAnimationWaitFrame = 0;
        this.engineFramesPerAnimationFrame = 6;
        this.currentAnimationMaxFrames = 6;

        // State
        this.state = state.OFFSCREEN;
        this.lastState;
        this.x = -2500;
        this.y = -2500;
    }

    // Bounding Box
    getBoundingLeft() {
        return this.x + boundingData.bbLeftX;
    }
    getBoundingRight() {
        return this.x + boundingData.bbRightX;
    }
    getBoundingTop() {
        return this.y + boundingData.bbTopY;
    }
    getBoundingBottom() {
        return this.y + boundingData.bbBottomY;
    }

    update() {}

    draw() {
        // Check sprite for state update
        this.checkForSpriteStateUpdate();

        // Draw Sprite
        this.engine.submitImageForDraw(60,
            this.spr, 
            this.currentAnimationFrame * this.sprWidth, 
            0, 
            this.sprWidth,
            this.sprHeight,
            this.x - this.engine.winX,
            this.y - this.engine.winY,
            this.sprWidth, 
            this.sprHeight);

        // Draw Hitboxes
        if (this.engine.drawHitboxes) {
            // Draw collision hitbox
            this.engine.submitBoundingBoxForDraw(99, "red",
                this.x + boundingData.bbLeftX - this.engine.winX, 
                this.y + boundingData.bbTopY - this.engine.winY, 
                boundingData.bbWidth, 
                boundingData.bbHeight);
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
                case state.OFFSCREEN:
                    this.currentAnimationLockFrame = true;
                    this.currentAnimationFrame = 0;
                    this.x = -2500;
                    this.y = -2500;
                    break;
                case state.DREAMING:
                    this.currentAnimationLockFrame = false;
                    this.currentAnimationFrame = 0;
                    break;
                case state.FROZEN:
                    this.currentAnimationLockFrame = true;
                    this.currentAnimationFrame = this.currentAnimationMaxFrames - 1;
                    break;
            } 
        }
    }

    startDreaming(playerX, playerY) {
        this.x = playerX + 26;
        this.y = playerY - 10;
        this.updateState(state.DREAMING);
    }

    wakeUp() {
        this.x = -2500;
        this.y = -2500;
        this.updateState(state.OFFSCREEN);
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
                if (this.state == state.DREAMING) {
                    this.updateState(state.FROZEN);
                    return;
                }

                // Reset animation at end of animation
                this.currentAnimationFrame = 0;
                return;
            }

            // Progress to next frame of current animation
            this.currentAnimationFrame++;
        }
    }

    checkClick(x, y) {
        if (checkPointToBoundingBoxCollision(x, y, this)) {
            emitPuzzleSolvedEvent();
        }
    }

    updateState(newState) {
        if (newState !== this.state) {
            this.state = newState;
        }
    }
}

export { DreamBubble };
