var data, agents = [];

function preload() {
    // Loading dataset
    data = loadTable('double_moons.csv', 'csv', 'header');
}

function setup() {
    // Initializations
    createCanvas(1000, 600);

    for (let row of data.rows) {
        agents.push( new Agent(parseFloat(row.arr[0]), parseFloat(row.arr[1]), (row.arr[2] == "N/A") ? 0 : parseInt(row.arr[2])) );
    }

    textAlign(CENTER);
    textSize(8);
}

function draw() {
    // Function called once per frame to update the drawing
    stroke(0);
    fill(10, 30, 40);
    rect(0, 0, 999, 599);

    for (let agent of agents) {
        agent.draw();
    }
}

function play_round() {
    // A distributed round
    for (let agent of agents) {
        agent.sufferPressure(agents);
    }
    for (let agent of agents) {
        agent.updateLabel();
    }

    // We call the next round 150ms after
    setTimeout( play_round, 150 );
}

function keyPressed() {
    // Enter to trigger the process
    if (keyCode == ENTER)
        play_round();
}
