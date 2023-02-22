function od(){
  const element = document.querySelector('body');
  element.innerHTML = 'Hello, World!';
}

function nvHome() {
  window.location.href="/user/home"
}

function nvAdmin() {
  window.location.href="/admin"
}
function nvUpdate() {
  window.location.href="/user/update"
}
function nvBase() {
  window.location.href="/"
}
function addTable(data) {
    var text1;
    var text2;
    var text3;
    var text4;
    var text5;
    var text6;
    var text7;
    size = data.length;
    var table = document.createElement('table');
    for (var i = 0; i < size; i++){
        var tr = document.createElement('tr');

        var td1 = document.createElement('td');
        var td2 = document.createElement('td');
        var td3 = document.createElement('td');
        var td4 = document.createElement('td');
        var td5 = document.createElement('td');
        var td6 = document.createElement('td');
        var td7 = document.createElement('td');
        for (var k=0; k<7;k++) {
            console.log(data[0].birthdate)
            text1 = document.createTextNode(data[i].id);
            text2 = document.createTextNode(data[i].username);
            text3 = document.createTextNode(data[i].firstname);
            text4 = document.createTextNode(data[i].middlename);
            text5 = document.createTextNode(data[i].lastname);
            text6 = document.createTextNode(data[i].birthdate);
            text7 = document.createTextNode(data[i].email);
        }
        td1.appendChild(text1);
        td2.appendChild(text2);
        td3.appendChild(text3);
        td4.appendChild(text4);
        td5.appendChild(text5);
        td6.appendChild(text6);
        td7.appendChild(text7);
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3);
        tr.appendChild(td4);
        tr.appendChild(td5);
        tr.appendChild(td6);
        tr.appendChild(td7);

        table.appendChild(tr);
}
document.body.appendChild(table);
}
function addOnlineTable(data) {
    var text1;
    var text2;
    var text3;
    var text4;
    size = data.length;
    var table = document.createElement('table');
    for (var i = 0; i < size; i++){
        var tr = document.createElement('tr');

        var td1 = document.createElement('td');
        var td2 = document.createElement('td');
        var td3 = document.createElement('td');
        var td4 = document.createElement('td');
        for (var k=0; k<7;k++) {
            console.log(data[0].birthdate)
            text1 = document.createTextNode(data[i].id);
            text2 = document.createTextNode(data[i].username);
            text3 = document.createTextNode(data[i].ipaddress);
            text4 = document.createTextNode(data[i].logindatetime);
        }
        td1.appendChild(text1);
        td2.appendChild(text2);
        td3.appendChild(text3);
        td4.appendChild(text4);
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3);
        tr.appendChild(td4);

        table.appendChild(tr);
}
document.body.appendChild(table);

}
function createUser(formData) {
  fetch('/user/create', {
    method: 'POST',
    headers:{
      "Content-type":"application/json"
    },
    body: JSON.stringify(formData)
  })
  .then(response => {
    if(response.ok){
        response.json()
          .then(data => {
            window.location.href="/"
          })
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}
function loginUser(formData) {
  fetch('/login', {
    method: 'POST',
    headers:{
      "Content-type":"application/json"
    },
    body: JSON.stringify(formData)
  })
  .then(response => {
    if(response.ok){
        response.json()
          .then(data => {
            console.log(data)
            localStorage.setItem("UserId",data["userId"])
            console.log(data["userName"])

            if(data["userName"] === "admin"){
              console.log(data["userName"])
              nvAdmin()
            }else {
             nvHome()
            }
          })
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

function deleteUser() {
  let usrid = localStorage.getItem("UserId")
  logoutUser()
  console.log(usrid)
  fetch('/user/delete/' + usrid, {
    method: 'DELETE',
    headers:{
      "Content-type":"application/json"
    },
  })
  .then(response => {
    if(response.ok){
        response.json()
          .then(data => {
            nvBase()
          })
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}
function logoutUser() {
  let usrid = localStorage.getItem("UserId")
  console.log(usrid)
  console.log("usrid")

  fetch('/logout/' + usrid ,{
    method: 'DELETE',
    headers:{
      "Content-type":"application/json"
    },
  })
  .then(response => {
    if(response.ok){
        response.json()
          .then(data => {
            nvBase()
          })
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

function updateUser(formData) {
  let usrid = localStorage.getItem("UserId")
  fetch('/user/update/' + usrid, {
    method: 'PUT',
    headers:{
      "Content-type":"application/json"
    },
    body: JSON.stringify(formData)
  })
  .then(response => {
    if(response.ok){
        response.json()
          .then(data => {
            window.location.href="/"
          })
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}
function listUsers() {
  fetch('/user/list', {
    method: 'GET',
    headers:{
      "Content-type":"application/json"
    },
    body: JSON.stringify()
  })
  .then(response => {
    if(response.ok){
        response.json()
          .then(data => {
            addTable(data)
          })
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

function listOnlineUsers() {
  fetch('/onlineusers', {
    method: 'GET',
    headers:{
      "Content-type":"application/json"
    },
    body: JSON.stringify()
  })
  .then(response => {
    if(response.ok){
        response.json()
          .then(data => {
            addOnlineTable(data)
          })
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
}