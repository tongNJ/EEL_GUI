// event listener
async function getDataFromPython(){
  document.getElementById("myeel").innerText = await eel.hello_eel()();
  document.querySelector("div").innerHTML = await eel.read_data()();
};

// async function getTableFromPython(){
//   document.querySelector("div").innerHTML = await eel.read_data()();
// };


document.getElementById("mybtn").addEventListener("click", () =>{
  getDataFromPython();
});

document.getElementById("mybtn").addEventListener("click", () =>{
  getTableFromPython();
});



// sedning data from Javascript to python
document.getElementById("toPy").addEventListener("click", async() =>{
  
  await eel.get_date_js(
    document.getElementById("navDate").value
  );
});

// //add event listener to receive input from HTML
// document.getElementById("navDate").addEventListener("change", async() =>{
//   var input = this.value;
//   var newDate = new Date(input);
//   await eel.get_date_js(newDate);
// });


// eel.expose(say_hello_js);
// function say_hello_js(x) {
//   console.log("Hello from " + x);
// };






// document.getElementById("data").addEventListener("click"),() =>{
//   importDF();
// };

// document.getElementById("mybtn").addEventListener("click", async function(){
//   document.getElementById("myeel").innerText = await eel.hello_eel()();
// });

