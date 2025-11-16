function checkPointToBoundingBoxCollision(x, y, o) {
    return !(
        (y > (o.getBoundingBottom())) || // Collide at bottom
        (y < (o.getBoundingTop())) || // Collide at top
        (x < o.getBoundingLeft()) || // Collide at left
        (x > (o.getBoundingRight())) // Collide at right
    );
}

function checkBoundingBoxesCollision(o1, o2) {
    return checkMovingBoundingBoxesCollision(o1, o2, 0, 0);
}

function checkMovingBoundingBoxesCollision(o1, o2, xMov, yMov) {
    return !(
        ((o1.getBoundingTop() + yMov) > (o2.getBoundingBottom())) || // Collide at bottom
        ((o1.getBoundingBottom() + yMov) < (o2.getBoundingTop())) || // Collide at top
        ((o1.getBoundingRight() + xMov) < o2.getBoundingLeft()) || // Collide at left
        ((o1.getBoundingLeft() + xMov) > (o2.getBoundingRight())) // Collide at right
    );
}

function moveToBoundingBoxCollisionBottom(o1, o2) {
    o1.y -= o1.getBoundingTop() - o2.getBoundingBottom() - 1;
}
function moveToBoundingBoxCollisionTop(o1, o2) {
    o1.y += o2.getBoundingTop() - o1.getBoundingBottom() - 1;
}
function moveToBoundingBoxCollisionRight(o1, o2) {
    o1.x -= o1.getBoundingLeft() - o2.getBoundingRight() - 1;
}
function moveToBoundingBoxCollisionLeft(o1, o2) {
    o1.x += o2.getBoundingLeft() - o1.getBoundingRight() - 1;
}

export {
    checkPointToBoundingBoxCollision,
    checkBoundingBoxesCollision,
    checkMovingBoundingBoxesCollision, 
    moveToBoundingBoxCollisionBottom,
    moveToBoundingBoxCollisionTop,
    moveToBoundingBoxCollisionRight,
    moveToBoundingBoxCollisionLeft
};
