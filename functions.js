/**
* @param {float} x
* @return 1 if x >= 0, -1 otherwise
*/
function sign(x) {
    return (x < 0) ? -1 : 1;
}

/**
* @param {float} distance
* @param {float} pressure
* @returns a pressure value depending on inputs
*/
function get_pressure(distance, pressure) {
    return constants.LAMBDA * pressure / distance;
}

/**
* Just for a fancy plot
*/
function generate_color(pressure) {
    if (pressure >= 0)
        return color(
            100 + Math.min(1, Math.max(0, 0.5 * (pressure + 1)))*155,
            100,
            100
        );
    return color(
        100,
        100,
        100 + Math.min(1, Math.max(0, 1 - 0.5 * (pressure + 1)))*155
    );
}
