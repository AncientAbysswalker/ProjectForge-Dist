import { UP, DOWN, LEFT, RIGHT, DOWN_LEFT, DOWN_RIGHT, UP_RIGHT } from "./arrowKeys.js";

export const validGoldenPaths = [
    {
        // Starts: Loading Bar and then The Witness
        // From: Page of Cat Sleeping at Computer
        id: '096f2da0ac6ecb18e501656de9e9a7cfa816b192',
        path: [DOWN, UP_RIGHT],
        action: (gpm) => {
            console.log(`Golden path triggered: ${JSON.stringify({ id: '096f2da0ac6ecb18e501656de9e9a7cfa816b192', path: [DOWN, RIGHT, UP, LEFT, UP, RIGHT] })}`);
        },
    },
    // {
    //     // Starts: Loading Bar and then The Witness
    //     // From: Page of Cat Sleeping at Computer
    //     id: '096f2da0ac6ecb18e501656de9e9a7cfa816b192',
    //     path: [DOWN, LEFT, UP, RIGHT, UP, LEFT],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '096f2da0ac6ecb18e501656de9e9a7cfa816b192', path: [DOWN, LEFT, UP, RIGHT, UP, LEFT] })}`);
    //     },
    // },
    // {
    //     // Starts: Combo Lock
    //     // From: Rear of Scrabble
    //     id: '7614c031869f0a3cf314b896c0040f16646d6a04',
    //     path: [LEFT, UP, LEFT, DOWN, LEFT, UP, UP, RIGHT, RIGHT, UP, LEFT, DOWN, LEFT, UP, RIGHT, DOWN, DOWN, RIGHT, DOWN, LEFT],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '7614c031869f0a3cf314b896c0040f16646d6a04', path: [LEFT, UP, LEFT, DOWN, LEFT, UP, UP, RIGHT, RIGHT, UP, LEFT, DOWN, LEFT, UP, RIGHT, DOWN, DOWN, RIGHT, DOWN, LEFT] })}`);
    //     },
    // },
    // {
    //     // Starts: Catstermind
    //     // From: Base64 Encoded Image
    //     id: '11a26b4a6eb0509b3434d9836ac7438213c5e676',
    //     path: [UP, RIGHT, DOWN, DOWN, DOWN],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '11a26b4a6eb0509b3434d9836ac7438213c5e676', path: [UP, RIGHT, DOWN, DOWN, DOWN] })}`);
    //     },
    // },
    // {
    //     // Starts: Photo of Location - Safe (Monitor Box)
    //     // From: CD Gif (End of Catstermind) [Out of Frame]
    //     id: '6dc2855179dab9ee03dd2ba2cc5fcea7c571cde1',
    //     path: [LEFT, LEFT, DOWN, RIGHT, RIGHT, DOWN, UP, DOWN, UP, DOWN, RIGHT],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '6dc2855179dab9ee03dd2ba2cc5fcea7c571cde1', path: [LEFT, LEFT, DOWN, RIGHT, RIGHT, DOWN, UP, DOWN, UP, DOWN, RIGHT] })}`);
    //     },
    // },    
    // {
    //     // Starts: Hanoi
    //     // From: Simple Face Mural
    //     id: '9591d82313628ebff55cfabfe2175a15a781495c',
    //     path: [
    //         UP, UP, DOWN, LEFT, DOWN, 
    //         RIGHT, LEFT, RIGHT, RIGHT, UP,
    //         DOWN, UP, DOWN, UP, DOWN, 
    //         RIGHT, LEFT, RIGHT, RIGHT, LEFT,
    //         UP, LEFT, DOWN, LEFT, RIGHT
    //     ],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '9591d82313628ebff55cfabfe2175a15a781495c', path: [UP, UP, DOWN, LEFT, DOWN, RIGHT, LEFT, RIGHT, RIGHT, UP, DOWN, UP, DOWN, UP, DOWN, RIGHT, LEFT, RIGHT, RIGHT, LEFT, UP, LEFT, DOWN, LEFT, RIGHT] })}`);
    //     },
    // },
    // {
    //     // Starts: Start Fox Maze
    //     // From: Tomato Can [Out of Frame]
    //     id: '40140f0d4116e9ad6a82236cd6f3821dbef20620',
    //     path: [LEFT, UP, RIGHT, RIGHT, DOWN, LEFT, DOWN, UP, LEFT, DOWN, UP, LEFT, RIGHT],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '40140f0d4116e9ad6a82236cd6f3821dbef20620', path: [LEFT, UP, RIGHT, RIGHT, DOWN, LEFT, DOWN, UP, LEFT, DOWN, UP, LEFT, RIGHT] })}`);
    //     },
    // },
    // {
    //     // Starts: Photo of Location - Mimic Chest (Cat Tower Remnant)
    //     // From: Fox Maze Chest Arrows Puzzle
    //     id: '2e20ae5717f54a223ea610725acdaa8b7302cab7',
    //     path: [DOWN, RIGHT, DOWN, RIGHT, RIGHT, LEFT, LEFT, RIGHT, LEFT, UP, RIGHT, DOWN],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '2e20ae5717f54a223ea610725acdaa8b7302cab7', path: [DOWN, RIGHT, DOWN, RIGHT, RIGHT, LEFT, LEFT, RIGHT, LEFT, UP, RIGHT, DOWN] })}`);
    //     },
    // },
    // {
    //     // Starts: Simple Face Mural
    //     // From: Memo Pages (Input Pads)
    //     id: '92817efeb8d3549100db0433b0bb5443d4f1347d',
    //     path: [LEFT, UP, RIGHT, LEFT, DOWN, RIGHT, UP, DOWN],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '92817efeb8d3549100db0433b0bb5443d4f1347d', path: [LEFT, UP, RIGHT, LEFT, DOWN, RIGHT, UP, DOWN] })}`);
    //     },
    // },
    // {
    //     // Starts: Printing Left Map
    //     // From: Assembling all cipher flash card borders
    //     id: 'fc5752ac9c3dffcf647a90a04482c02106544d37',
    //     path: [
    //         RIGHT, RIGHT, RIGHT,
    //         UP, UP, RIGHT,
    //         DOWN, LEFT, LEFT,
    //         DOWN, LEFT, RIGHT,
    //         DOWN, DOWN, DOWN
    //     ],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: 'fc5752ac9c3dffcf647a90a04482c02106544d37', path: [RIGHT, RIGHT, RIGHT, UP, UP, RIGHT, DOWN, LEFT, LEFT, DOWN, LEFT, RIGHT, DOWN, DOWN, DOWN] })}`);
    //     },
    // },
    // {
    //     // Starts: Coconut Mall
    //     // From: Candy Wrappers
    //     id: '15d38ec860945d1ffb6a88b84d89a15ff0966b11',
    //     path: [UP, RIGHT, LEFT, UP, DOWN, RIGHT, RIGHT, LEFT, RIGHT, DOWN],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '15d38ec860945d1ffb6a88b84d89a15ff0966b11', path: [UP, RIGHT, LEFT, UP, DOWN, RIGHT, RIGHT, LEFT, RIGHT, DOWN] })}`);
    //     },
    // },
    // {
    //     // Starts: Debug Terminal
    //     // From: Ciphers Page
    //     id: '94aab5e6bc26eaa121be90afcd776a11f91033e6',
    //     path: [
    //         UP, UP,
    //         DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN
    //     ],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '94aab5e6bc26eaa121be90afcd776a11f91033e6', path: [UP, UP, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN, DOWN] })}`);
    //     },
    // },
    // {
    //     // Starts: Photo of Location - Glasses Chest (Clock Shelf)
    //     // From: Back of Puzzle
    //     id: '0c8222a91f50d02dea2790af502b3dc0e92263ec',
    //     path: [
    //         RIGHT, UP, LEFT, UP, RIGHT, RIGHT, DOWN, LEFT, UP, LEFT, DOWN, LEFT, UP, LEFT, DOWN, LEFT, UP, UP, RIGHT, DOWN, RIGHT, DOWN, LEFT, DOWN
    //     ],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '0c8222a91f50d02dea2790af502b3dc0e92263ec', path: [RIGHT, UP, LEFT, UP, RIGHT, RIGHT, DOWN, LEFT, UP, LEFT, DOWN, LEFT, UP, LEFT, DOWN, LEFT, UP, UP, RIGHT, DOWN, RIGHT, DOWN, LEFT, DOWN] })}`);
    //     },
    // },

    // /** 
    //  * All valid Bunny Paths
    //  * 
    //  * Note that Bunny #0 (Glitch Bun) is created from the loading bar of WitnessManager, not GPM
    //  * Note that Bunny #1 (Sleep Bun) is created from the SPM by clicking on the bunny in the fox maze
    //  */
    // {
    //     // Starts: Bunny #2 - Flower Buns
    //     // From: Fox Maze Flower Puzzle
    //     id: '2b295f31aeb328793cf997640abf3a05757491f8',
    //     path: [UP, RIGHT, DOWN, LEFT, DOWN, LEFT, DOWN, RIGHT, DOWN, RIGHT, UP, RIGHT, DOWN, LEFT, DOWN, LEFT, DOWN, RIGHT],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '2b295f31aeb328793cf997640abf3a05757491f8', path: [UP, RIGHT, DOWN, LEFT, DOWN, LEFT, DOWN, RIGHT, DOWN, RIGHT, UP, RIGHT, DOWN, LEFT, DOWN, LEFT, DOWN, RIGHT] })}`);
    //     },
    // },
    // {
    //     // Starts: Bunny #3 - Stripey Heart Bun
    //     // From: Color Page Removal Message
    //     id: 'caa32dcbe25ffb52db82d3fb4cd09adc2a8fbe53',
    //     path: [
    //         UP, LEFT, DOWN, RIGHT,
    //         UP, LEFT, DOWN, RIGHT,
    //         UP, LEFT, DOWN, RIGHT
    //     ],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: 'caa32dcbe25ffb52db82d3fb4cd09adc2a8fbe53', path: [UP, LEFT, DOWN, RIGHT, UP, LEFT, DOWN, RIGHT, UP, LEFT, DOWN, RIGHT] })}`);
    //     },
    // },
    // {
    //     // Starts: Bunny #4 - Standing Kawaii Bun
    //     // From: Hanoi Title Path
    //     id: '15d23ce64f94fee1b90c20b4ba6ec3dc2f1976de',
    //     path: [RIGHT, RIGHT, RIGHT, LEFT, UP, RIGHT, DOWN, RIGHT, LEFT, UP, LEFT, UP],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '15d23ce64f94fee1b90c20b4ba6ec3dc2f1976de', path: [RIGHT, RIGHT, RIGHT, LEFT, UP, RIGHT, DOWN, RIGHT, LEFT, UP, LEFT, UP] })}`);
    //     },
    // },
    // {
    //     // Starts: Bunny #5 - Kawaii Carrot Bun
    //     // From: Original Golden Path
    //     id: 'ef361c8dc6409be689ea3bd26d6943152f615823',
    //     path: [
    //         UP,
    //         LEFT,
    //         DOWN,
    //         LEFT,
    //         UP,
    //         LEFT,
    //         DOWN,
    //         LEFT,
    //         UP,
    //         RIGHT,
    //         UP,
    //         RIGHT,
    //         UP,
    //         LEFT,
    //         UP,
    //         RIGHT,
    //         DOWN,
    //         RIGHT,
    //         UP,
    //         LEFT,
    //         UP,
    //         LEFT,
    //         UP,
    //         RIGHT,
    //         UP,
    //         LEFT,
    //         DOWN,
    //         LEFT,
    //         UP,
    //         RIGHT,
    //         UP,
    //         UP,
    //         LEFT,
    //         UP,
    //         RIGHT,
    //         DOWN,
    //         RIGHT,
    //         DOWN,
    //         RIGHT,
    //         UP,
    //         RIGHT,
    //         DOWN,
    //         LEFT,
    //         DOWN,
    //         RIGHT,
    //         UP,
    //         RIGHT,
    //         RIGHT,
    //         DOWN,
    //         RIGHT,
    //         UP,
    //         RIGHT,
    //         DOWN,
    //         RIGHT,
    //         UP,
    //         RIGHT,
    //         RIGHT,
    //         DOWN,
    //         LEFT,
    //         DOWN,
    //         LEFT,
    //         DOWN,
    //         RIGHT,
    //         DOWN,
    //         RIGHT,
    //         DOWN,
    //         LEFT,
    //         LEFT,
    //         DOWN,
    //         RIGHT,
    //         DOWN,
    //         LEFT,
    //         DOWN,
    //         RIGHT,
    //         UP,
    //         RIGHT,
    //         DOWN,
    //         RIGHT,
    //         UP,
    //         RIGHT,
    //         RIGHT,
    //         DOWN,
    //         DOWN,
    //         LEFT,
    //         UP,
    //         RIGHT,
    //         UP,
    //         LEFT,
    //         DOWN,
    //         LEFT,
    //         UP,
    //         LEFT,
    //         UP,
    //         LEFT,
    //         UP,
    //         RIGHT,
    //         RIGHT,
    //         UP,
    //         LEFT,
    //         UP,
    //     ],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: 'ef361c8dc6409be689ea3bd26d6943152f615823', path: [UP, LEFT, DOWN, LEFT, UP, LEFT, DOWN, LEFT, UP, RIGHT, UP, RIGHT, UP, LEFT, UP, RIGHT, DOWN, RIGHT, UP, LEFT, UP, LEFT, UP, RIGHT, UP, LEFT, DOWN, LEFT, UP, RIGHT, UP, UP, LEFT, UP, RIGHT, DOWN, RIGHT, DOWN, RIGHT, UP, RIGHT, DOWN, LEFT, DOWN, RIGHT, UP, RIGHT, RIGHT, DOWN, RIGHT, UP, RIGHT, DOWN, RIGHT, UP, RIGHT, RIGHT, DOWN, LEFT, DOWN, LEFT, DOWN, RIGHT, DOWN, RIGHT, DOWN, LEFT, LEFT, DOWN, RIGHT, DOWN, LEFT, DOWN, RIGHT, UP, RIGHT, DOWN, RIGHT, UP, RIGHT, RIGHT, DOWN, DOWN, LEFT, UP, RIGHT, UP, LEFT, DOWN, LEFT, UP, LEFT, UP, LEFT, UP, RIGHT, RIGHT, UP, LEFT, UP] })}`);
    //     },
    // },
    // {
    //     // Starts: Bunny #6 - Mandarin Bun
    //     // From: Color Page Border Dots
    //     id: 'fe4a8f6eb5e8386f4bae63ad64a3d42058d14972',
    //     path: [DOWN, LEFT, DOWN, DOWN, DOWN, LEFT, LEFT, UP, DOWN, LEFT, RIGHT, UP, UP, DOWN, UP, RIGHT, LEFT, DOWN, RIGHT, RIGHT, LEFT, DOWN, UP, DOWN, DOWN, DOWN, UP, LEFT, LEFT, RIGHT, UP, LEFT, LEFT, LEFT, LEFT, LEFT, LEFT, DOWN, DOWN, DOWN, RIGHT, LEFT, LEFT, DOWN, DOWN, RIGHT, UP],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: 'fe4a8f6eb5e8386f4bae63ad64a3d42058d14972', path: [DOWN, LEFT, DOWN, DOWN, DOWN, LEFT, LEFT, UP, DOWN, LEFT, RIGHT, UP, UP, DOWN, UP, RIGHT, LEFT, DOWN, RIGHT, RIGHT, LEFT, DOWN, UP, DOWN, DOWN, DOWN, UP, LEFT, LEFT, RIGHT, UP, LEFT, LEFT, LEFT, LEFT, LEFT, LEFT, DOWN, DOWN, DOWN, RIGHT, LEFT, LEFT, DOWN, DOWN, RIGHT, UP] })}`);
    //     },
    // },
    // {
    //     // Starts: Bunny #7 - Standing Simple Bun
    //     // From: Steganography
    //     id: '4eae93cd60707e9f9a0139f84f93cf8417f1f36e',
    //     path: [
    //         RIGHT, UP, RIGHT, DOWN, RIGHT, RIGHT, UP, RIGHT, UP, RIGHT, DOWN, DOWN, RIGHT, RIGHT, RIGHT, UP, RIGHT, DOWN, RIGHT, UP, RIGHT, DOWN, RIGHT, DOWN, RIGHT
    //     ],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '4eae93cd60707e9f9a0139f84f93cf8417f1f36e', path: [RIGHT, UP, RIGHT, DOWN, RIGHT, RIGHT, UP, RIGHT, UP, RIGHT, DOWN, DOWN, RIGHT, RIGHT, RIGHT, UP, RIGHT, DOWN, RIGHT, UP, RIGHT, DOWN, RIGHT, DOWN, RIGHT] })}`);
    //     },
    // },
    // {
    //     // Starts: Bunny #8 - Headphones Bun
    //     // From: Collecting Music Note Twice
    //     id: '0f663ad0b0b08a5992b854a5a6af01c3eafc5b74',
    //     path: [
    //         UP, UP, DOWN, DOWN, LEFT, RIGHT, LEFT, RIGHT,
    //         UP, UP, UP, DOWN, DOWN, DOWN, 
    //         LEFT, LEFT, RIGHT, LEFT, LEFT, RIGHT, RIGHT
    //     ],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '0f663ad0b0b08a5992b854a5a6af01c3eafc5b74', path: [UP, UP, DOWN, DOWN, LEFT, RIGHT, LEFT, RIGHT, UP, UP, UP, DOWN, DOWN, DOWN, LEFT, LEFT, RIGHT, LEFT, LEFT, RIGHT, RIGHT] })}`);
    //     },
    // },
    // {
    //     // Starts: Bonus Note
    //     // From: Post-Bunny Path
    //     id: '199f018bca122b7136bab3b2de06882ca01dab3d',
    //     path: [
    //         UP,
    //         RIGHT, UP, LEFT,
    //         DOWN_RIGHT, DOWN,
    //         DOWN,
    //         DOWN_LEFT, DOWN_RIGHT, UP_RIGHT,
    //         DOWN, DOWN, RIGHT,
    //         UP_RIGHT, UP_RIGHT, UP,
    //         LEFT, UP,
    //         UP_RIGHT, DOWN_RIGHT
    //     ],
    //     action: (gpm) => {
    //         console.log(`Golden path triggered: ${JSON.stringify({ id: '199f018bca122b7136bab3b2de06882ca01dab3d', path: [UP, RIGHT, UP, LEFT, DOWN_RIGHT, DOWN, DOWN, DOWN_LEFT, DOWN_RIGHT, UP_RIGHT, DOWN, DOWN, RIGHT, UP_RIGHT, UP_RIGHT, UP, LEFT, UP, UP_RIGHT, DOWN_RIGHT] })}`);
    //     },
    // },
];
