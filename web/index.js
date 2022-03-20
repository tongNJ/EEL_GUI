


async function greetingFromPython(){
  document.getElementById('greeting').innerHTML = await eel.greeting()();
}
greetingFromPython();



document.getElementById('generateReport').addEventListener('click', async ()=>{
  let navDate = document.getElementById('navDate').value;
  let returnTable = await eel.sendNavDate(navDate)();
  document.getElementById('newData').innerHTML = returnTable;
},false);



//add event listener on Generate Report Button
document.getElementById('generateReport').addEventListener('click', ()=>{
    collectNavDate();
  },false);

async function getTableFromPython(){
  document.getElementById('data').innerHTML = await eel.read_data()();
  }
  
getTableFromPython();

// eel.expose(go_to)
// function go_to(url) {window.location.replace(url);};


document.getElementById('renderFileHtml').addEventListener('click', ()=>{
  window.location.replace('/files.html');
})

// document.getElementById('backIndex').addEventListener('click',()=>{
//   // location.href = 'index.html';
//   document.getElementById('filesDemo').innerHTML = 'abc';
// })







// function saveDate(){
//   let e = document.getElementById('navDate').value;
//   console.log(e);
//   document.getElementById('confirmation').innerText="You Selected: " + e;
// }

// document.getElementById('navDate').addEventListener("change", ()=>{
//   saveDate();
// })


// eel.expose(saveDate);
// function saveDate(){
//   let e= document.getElementById('navDate').value;
//   console.log(e);
//   document.getElementById('confirmation').innerText="You Selected: " + e;
//   return e
// }
// // console.log(e);

// document.getElementById('navDate').addEventListener("change", ()=>{
//   saveDate();
// })

// let a=3;

// eel.expose(send_data);
// function send_data(){
//   return a;
// }


