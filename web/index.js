// event listener
async function getTableFromPython(){
  document.getElementById("myeel").innerText = await eel.hello_eel()();
  document.querySelector("#data").innerHTML = await eel.read_data()();
};

document.getElementById("mybtn").addEventListener("click", () =>{
  getTableFromPython(); 
});

document.getElementById("mybtn").addEventListener("click", async() =>{
  await eel.get_date_js(
    document.getElementById("navDate").value
  );
})


