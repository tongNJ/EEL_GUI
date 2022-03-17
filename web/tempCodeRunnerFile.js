
document.getElementById("navDate").addEventListener("change", async() =>{
  var input = this.value;
  var newDate = new Date(input);
  console.log(input);
  console.log(newDate)
});