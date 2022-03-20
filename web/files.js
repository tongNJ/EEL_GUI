// document.getElementById('backIndex').addEventListener('click',()=>{
//   // location.href = 'index.html';
//   document.getElementById('filesDemo').innerHtml = 'abc';
// })

let demo1 = document.getElementById('filesDemo2').innerText = 'a';
console.log(demo1);

document.getElementById('backIndex').addEventListener('click', ()=>{
  window.location.replace('/index.html');
})


document.getElementById('generateReport').addEventListener('click', async ()=>{
  document.getElementById('data').innerHTML = await eel.read_data()();
},false);


document.getElementById('checkFiles').addEventListener('click', async ()=>{
  document.getElementById('ffnav').innerHTML = await eel.check_files('ffnav','27022022')();
});

