var PORT = 60000;
var HOST = "http://dataweb.isis.rl.ac.uk" 
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
			//window.alert(JSON.stringify(data));
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
        };
    };

    a.sort();

    for (key = 0; key < a.length; key++) {
        sorted[a[key]] = o[a[key]];
    }
    return sorted;
}

function close_window(){
	clearBox("new_window");
};

function create_new_window(){
	clearBox("new_window");
	var newWindow = document.createElement("div");
	var newWindowStyle = document.createAttribute("class");
	newWindowStyle.value = "col-sm-12 well";
	newWindow.setAttributeNode(newWindowStyle);
	newWindow.id = "internal";
	document.getElementById("new_window").appendChild(newWindow);
	var closeButton = document.createElement("button");
	closeButton.innerHTML = "x";
	var blockListStyle = document.createAttribute("onclick");
    blockListStyle.value = "close_window()";
	closeButton.setAttributeNode(blockListStyle);
	document.getElementById("internal").appendChild(closeButton);	
};

function open_wall_display(){
	create_new_window()
	var newIframe = document.createElement("iframe");
	newIframe.src = "http://epics-jenkins.isis.rl.ac.uk/plugin/jenkinswalldisplay/walldisplay.html?viewName=All&jenkinsUrl=http%3A%2F%2Fepics-jenkins.isis.rl.ac.uk%2F"
	newIframe.height = String(windowHeight*2/5)+"px"
	newIframe.width = "100%"
	//newIframe.frameborder = "0"
	document.getElementById("internal").appendChild(newIframe);
	
	
}


function on_click(elmnt) {
	create_new_window();
	var newIframe = document.createElement("iframe");
	newIframe.src = "http://dataweb.isis.rl.ac.uk/IbexDataweb/default.html?Instrument="+ elmnt.innerHTML
	newIframe.height = String(windowHeight*2/5)+"px"
	newIframe.width = "100%"
	newIframe.frameborder = "0"
	document.getElementById("internal").appendChild(newIframe);
		//<iframe src="https://waffle.io/ISISComputingGroup/IBEX" height = "100%" width = "100%" frameborder = "0" ></iframe>

	//window.location = "http://dataweb.isis.rl.ac.uk/IbexDataweb/default.html?Instrument="+ elmnt.innerHTML
};

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
	data = sortObject(data);
	var total_users = Object.keys(data).length;
	document.getElementById("totalUsers").innerHTML = total_users;
	document.getElementById("onlineUsers").innerHTML = Object.keys(onlineClients).length;
	document.getElementById("offlineUsers").innerHTML = Object.keys(offlineClients).length;
	clearBox("buttons")
	for (value in data){
		var newButton = document.createElement("button");
		newButton.innerHTML = value

		newButton.style.type = "btn";
		//newButton.onclick = function(event,newButton) {
		//window.location = "http://dataweb.isis.rl.ac.uk/IbexDataweb/default.html?Instrument="+newButton.innerHTML;
		//};
		if (total_users >15){
			ending = "btn-large";
		} else {
			ending = "btn-xl";
			};	
		var blockListStyle = document.createAttribute("class");
		if (data[value] == true){
			blockListStyle.value = 'btn btn-success '+ending;
		} else{
			blockListStyle.value = 'btn btn-danger '+ending;
		}
        newButton.setAttributeNode(blockListStyle);
		var blockListStyle = document.createAttribute("onclick");
        blockListStyle.value = "on_click(this)"
		newButton.setAttributeNode(blockListStyle);

		document.getElementById("buttons").appendChild(newButton);

	};
};

$(document).ready(refresh());
var windowWidth = $(window).width();
var windowHeight = $(window).height();
var buttonHeight = $(window).height();
open_wall_display();

setInterval(refresh, 5000);