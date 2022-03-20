eel.expose(js_random);
function js_random() {
    return Math.random();
}

async function run() {
    // Synchronous call must be inside function marked 'async'
    
    // Get result returned synchronously by 
    //  using 'await' and passing nothing in second brackets
    //        v                   v
    let n = await eel.py_random()();
    document.getElementById('demo2').innerHTML = await n;
    console.log('Got this from Python: ' + n);
}

run();