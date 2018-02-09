class Geometry {

    /*
    * Static class used for geometric manipulations, for convenience.
    */

    /**
    * @param {Agent} p1
    * @param {Agent} p2
    * @returns the Manhattan distance between p1 and p2
    */
    static distance1(p1, p2) {
        return Math.abs(p1.x - p2.x) + Math.abs(p1.y - p2.y);
    }

    /**
    * @param {Agent} p1
    * @param {Agent} p2
    * @returns the Euclidean distance between p1 and p2
    */
    static distance2(p1, p2) {
        return Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2);
    }
}

class Agent {
    /*
    An agent is simply one of the samples. It is characterized by two features,
    and a label.
    */

    /**
    * @param {float} x first feature value
    * @param {float} y second feature value
    * @param {integer} label initial class of the sample
    * @returns nothing
    */
    constructor(x, y, label) {

        // Features
        this.x = x;
        this.y = y;

        // Initial label, 0 if it is unknown
        this.label = label;

        // A variable pressure_old must be kept, because system is synchrone
        this.pressure_old = label;
        this.pressure = label;

        // Initial display color
        this.color = (label == 1) ? color(255, 100, 100) : (label == -1) ? color(100, 100, 255) : color(100, 100, 100);
    }

    /**
    * @param {float} p pressure to be applied
    * @returns nothing
    * This method allows an angent to be applied pressure. Truncates it if
    * it outreaches a give threshold.
    */
    addPressure(p) {
        this.pressure += p;
        if (Math.abs(this.pressure) > constants.MAXPRESSURE)
            this.pressure = sign(this.pressure) * constants.MAXPRESSURE;
    }

    /**
    * @param {Agent} other_agent
    * @returns the pressure applied by "this" on "other_agent"
    */
    getPressure(other_agent) {
        const d = Geometry.distance1(this, other_agent);

        // If the other agent is out of range from this, there is no pressure
        // If the other agent is at distance 0, no pressure too (duplicate)
        if (d > constants.MAXREACH | d == 0) return 0;

        // Otherwise, there is a pressure w.r.t. distance and "this" pressure
        // Note that we use 'pressure_old', to be able to simulate the process
        // to be synchronous.
        return get_pressure(d, this.pressure_old);
    }

    /**
    * @param {Agent list} agents
    * @returns nothing
    * Updates pressure applied on the agent by the agent list
    */
    sufferPressure(agents) {
        for (let agent of agents) {
            this.addPressure( agent.getPressure(this) );
        }
    }

    /**
    * @returns nothing
    * Called at the end of each round, updating labels.
    */
    updateLabel() {
        // We store pressure at the end of round n to be able to recall it
        // for round n+1
        this.pressure_old = this.pressure;
        
        this.color = generate_color(this.pressure);
    }

    // Draws stuff
    draw() {
        stroke(this.color);
        fill(this.color);
        ellipse( (this.x + 2) * 200, (this.y + 2) * 150, constants.AGENTRADIUS, constants.AGENTRADIUS);
        stroke(255);
        fill(255);
        //text( Math.round(this.pressure * 10) / 10, (this.x + 2) * 200, (this.y + 2) * 150 + 4 );
    }
}
