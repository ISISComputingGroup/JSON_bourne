var PORT = 60000;
var HOST = "http://localhost" 
//$('.btn').button();

function refresh() {
	$.ajax({
		url: HOST + ":" + PORT + "/",
		dataType: 'jsonp',
		data: {"Instrument": "all"},
		timeout: 1000,
		error: function(xhr, status, error){ 
			window.alert("Error: JSON not read");
		},
		success: function(data){ 
			//window.alert(JSON.stringify(data))
			display_data(data);
		}
	});
}

function clearBox(elementID){
    document.getElementById(elementID).innerHTML = "";
};

function sortObject(o) {
    var sorted = {},
    key, a = [];

    for (key in o) {
        if (o.hasOwnProperty(key)) {
            a.push(key);
        }
    }

    a.sort();

    for (key = 0; key < a.length; key++) {
        sorted[a[key]] = o[a[key]];
    }
    return sorted;
}

function display_data(data){
	var onlineClients = new Array();
	var offlineClients = new Array();
	for (value in data){
		if (data[value] == true){
			onlineClients.push(value);
		} else{
			offlineClients.push(value);
		};	
	};
	data = sortObject(data)

	document.getElementById("totalUsers").innerHTML = Object.keys(data).length;
	document.getElementById("onlineUsers").innerHTML = Object.keys(onlineClients).length;
	document.getElementById("offlineUsers").innerHTML = Object.keys(offlineClients).length;
	clearBox("buttons")
	for (value in data){
		var newButton = document.createElement("button");
		newButton.innerHTML = value
		document.getElementById("buttons").appendChild(newButton);
		newButton.style.type = "btn";
		var blockListStyle = document.createAttribute("class");
		if (data[value] == true){
			blockListStyle.value = 'btn btn-success btn-xl';
		} else{
			blockListStyle.value = 'btn btn-danger btn-xl';
		}
        newButton.setAttributeNode(blockListStyle);
	}
};

$(document).ready(refresh());

setInterval(refresh, 5000);