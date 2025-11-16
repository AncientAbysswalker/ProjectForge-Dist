const inventoryWidth = 24;

class Engine {
    constructor(canvas, ctx, winX, winY, drawHitboxes) {
        // Context and Window
        this.ctx = ctx;
        this.canvas = canvas;
        this.winX = winX;
        this.winY = winY;

        // Game Object Information
        this.mapCollision;
        this.playerObject;
        this.renderList = [];
        this.clickableList = [];
        this.objectList = [];
        this.solidObjectList = [];

        // Drawing
        this.backgroundColor = "#FFFFFF";
        this.mapLayers = [];
        this.drawHitboxes = drawHitboxes;
        this.renderCache = {};

        this.timestamp;
        this.lastEngineFrame = -1;

        // Binding for this-related conflicts
        this.clickEvent = this.clickEvent.bind(this);
    }

    setPlayerObject(playerObject) {
        this.playerObject = playerObject;
    }

    getPlayerObject() {
        return this.playerObject;
    }

    
    setBackgroundColor(color) {
        this.backgroundColor = color;
    }

    addMapLayer(sprite, layer, offsetX, offsetY) {
        this.mapLayers.push({
            sprite: sprite,
            layer: layer,
            offsetX: offsetX,
            offsetY: offsetY
        });
    }

    setMapCollision(mapCollision) {
        this.mapCollision = mapCollision;
    }

    getMapCollision(row, col) {
        return this.mapCollision[row][col];
    }

    registerClickable(o) {
        this.clickableList.push(o);
    }

    deregisterClickable(o) {
        const index = this.clickableList.findIndex(i => i === o);

        if (index !== -1) {
            this.clickableList.splice(index, 1);
        }
    }

    addObject(o) {
        this.renderList.push(o);
        this.objectList.push(o);
    }

    addSolidObject(o) {
        this.renderList.push(o);
        this.solidObjectList.push(o);
    }

    removeObject(o) {
        const renderIndex = this.renderList.findIndex(i => i === o);
        const objectIndex = this.objectList.findIndex(i => i === o);

        if (renderIndex !== -1 && objectIndex !== -1) {
            this.renderList.splice(renderIndex, 1);
            this.objectList.splice(objectIndex, 1);
        }
    }

    removeSolidObject(o) {
        this.renderList.remove(o);
        this.solidObjectList.remove(o);
    }

    getRenderList() {
        return this.renderList;
    }

    getObjectList() {
        return this.objectList;
    }

    getSolidObjectList() {
        return this.solidObjectList;
    }

    setWindowPosition(winX, winY) {
        this.winX = winX;
        this.winY = winY;
    }

    startEngine() {
        this.tick(0);
    }

    tick = (timestamp) => {
        this.timestamp = timestamp;
        const currentEngineFrame = Math.floor(timestamp / 1000 * 30);

        // Only run update once per frame
        if (currentEngineFrame > this.lastEngineFrame) {
            this.lastEngineFrame = currentEngineFrame;

            // Reset Canvas
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            
            // Background color in case we go outside the maze
            this.ctx.fillStyle = this.backgroundColor;
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
            // Map layers
            for (const mapLayer of this.mapLayers) {
                this.submitImageForDraw(mapLayer.layer, mapLayer.sprite, mapLayer.offsetX - this.winX, mapLayer.offsetY - this.winY);
            }

            // Update all objects
            this.playerObject.update();
            for (const renderObject of this.getRenderList()) {
                renderObject.update();
            }
            
            // Submit all objects for draw
            this.playerObject.draw();
            for (const renderObject of this.getRenderList()) {
                renderObject.draw();
            }
        
            // Submit map hitboxes for draw
            if (this.drawHitboxes) {
                for (let row = 0; row < this.mapCollision.length; row++) {
                    for (let col = 0; col < this.mapCollision[row].length; col++) {
                        if (this.mapCollision[row][col]) {
                            this.submitBoundingBoxForDraw(99, "yellow",
                                col * 32 - this.winX, 
                                row * 32 - this.winY, 
                                32, 
                                32);
                        }
                    }
                }
            }

            // Draw everything
            this.drawCachedLayers();
        }

        requestAnimationFrame(this.tick);
    }

    submitImageForDraw(zIndex, ...args) {
        if (!(zIndex in this.renderCache)) {
            this.renderCache[zIndex] = [];
        }

        this.renderCache[zIndex].push(() => this.ctx.drawImage(...args));
    }

    submitBoundingBoxForDraw(zIndex, color, ...args) {
        if (!(zIndex in this.renderCache)) {
            this.renderCache[zIndex] = [];
        }

        this.renderCache[zIndex].push(() => {
            this.ctx.beginPath();
            this.ctx.strokeStyle = color;
            this.ctx.strokeRect(...args);
            this.ctx.closePath()
        });
    }

    drawCachedLayers() {
        for (const zIndex of Object.keys(this.renderCache).sort((a, b) => a - b)) {
            for (const cachedDraw of this.renderCache[zIndex]) {
                cachedDraw();
            }
        }

        // Clear Cache
        this.renderCache = {};
    }

    clickEvent(event) {
        const clientRect = this.canvas.getBoundingClientRect();
        const x = Math.round(event.clientX - clientRect.left + this.winX);
        const y = Math.round(event.clientY - clientRect.top + this.winY);

        for (const clickable of this.clickableList) {
            clickable.checkClick(x, y);
        }
    }
}

export { Engine, inventoryWidth };
