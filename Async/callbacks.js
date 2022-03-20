//A callback is a function passed as an argument to another function.

function myDisplayer(some){
  document.getElementById('h2').innerHTML = some;
}

function myCalculator(num1,num2,callback) {
  let sum = num1 + num2;
  callback(sum);
}

myCalculator(6,7,myDisplayer);

//where callbacks really shine are in asynchronous functions, 
//where one function has to wait for another function
//like waiting for a file to load....
setTimeout(myFunction,3000);
function myFunction() {
  document.getElementById('demo').innerHTML = 'I Love You !';
}

function myFunction2(value){
  document.getElementById('demo2').innerHTML=value;
}
setTimeout(()=>{
  myFunction2('The second function!!');
}, 3000);
//-------------------------------------------------------------
setInterval(myFunction3,1000);
function myFunction3() {
  let d = new Date()
  document.getElementById('demo3').innerHTML = 
  d.getHours() + ":" +
  d.getMinutes() + ":" +
  d.getSeconds();
}
//--------------------------------------------------------------
function myFunction4(myCarContent){
  document.getElementById('demo4').innerHTML = myCarContent;
}

function getFile(callback){
  let req = new XMLHttpRequest();
  req.open('GET','mycar.html');
  req.onload = function(){
    if (req.status == 200){
      callback(this.responseText);
    } else {
      callback("Error: " + req.status);
    }
  }
  req.send();
}

getFile(myFunction4);
//--------------------------------------------------------------
// JavaScript Promises
// I promise a result!
// "Producing code" is code that can take some time
// "Consuming code" is code that must wait for the result
// A Promise is a JavaScript object that links producing code and consuming code
function myFunction5(some){
  document.getElementById('demo5').innerHTML = some;
}

let myPromise = new Promise(function(myResolve,myReject){
  let x = 1;
  //The producing code (this my take some time)
  if (x==0){
    myResolve('OK');
  } else {
    myReject('Error');
  }
});

myPromise.then(
  function(value) {myFunction5(value);},
  function(error) {myFunction5(error);}
);

//--------------------------------------------------------------
//Async and await make promises easier to write
//async makes a function return a Promise
//await makes a function wait for a Promise

let myPromise6 = new Promise(function(resolve,reject){
  setTimeout(() => {
    resolve('delayed but finally arrived');
  }, 3000); 
});

function myFunction7(){
  setTimeout(function(){ return 'delayed but finally arrived'},3000);
}

async function myFunction6() {
  document.getElementById('demo6').innerHTML = await myPromise6;
}
myFunction6();

//--------------------------------------------------------------