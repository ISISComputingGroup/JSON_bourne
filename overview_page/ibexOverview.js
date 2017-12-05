var PORT = 60000;
var HOST = "http://dataweb.isis.rl.ac.uk"

var INST_REFRESH = 5000;
var WALL_DISP_REFRESH = 2 * 60 * 1000;
var TIMEOUT = 1000;

function refresh_instruments() {
	$.ajax({
		url: HOST + ":" + PORT + "/",
		dataType: 'jsonp',
		data: {"Instrument": "all"},
		timeout: TIMEOUT,
		error: function(xhr, status, error){ 
			document.getElementById("time").setAttribute("style", "color:red")
		},
		success: function(data){ 
			display_data(data);
		}
	});
}

function refresh_wall_display() {
	// Refresh the wall display as it has a memory leak
	var display = document.getElementById('wall_display');
	display.src = display.src;
}

function clearBox(elementID){
    document.getElementById(elementID).innerHTML = "";
}

function sortDictionary(o) {
    var sorted = {};
    var a = [];

    for (var key in o) {
        if (o.hasOwnProperty(key)) {
            a.push(key);
        };
    };

    a.sort();

    for (var i = 0; i < a.length; i++) {
        sorted[a[i]] = o[a[i]];
    }
    return sorted;
}

function create_new_window(){
	// create the container for jenkins builds or
	// instrument dataweb information
	clearBox("new_window");
	var newWindow = document.createElement("div");
	var newWindowStyle = document.createAttribute("class");
	
	newWindowStyle.value = "col-sm-12 well";
	newWindow.setAttributeNode(newWindowStyle);
	newWindow.id = "internal";
	
	document.getElementById("new_window").appendChild(newWindow);
}

function open_wall_display(){
	create_new_window()
	var newIframe = document.createElement("iframe");
	newIframe.setAttribute("id", "wall_display");
	
	newIframe.src = "http://epics-jenkins.isis.rl.ac.uk/plugin/jenkinswalldisplay/walldisplay.html?viewName=All&jenkinsUrl=http%3A%2F%2Fepics-jenkins.isis.rl.ac.uk%2F"
	newIframe.height = String(windowHeight*2/5)+"px"
	newIframe.width = "100%"
	
	document.getElementById("internal").appendChild(newIframe);	
}


function on_click(elmnt) {
	create_new_window();
	var newIframe = document.createElement("iframe");
	
	newIframe.src = "http://dataweb.isis.rl.ac.uk/IbexDataweb/default.html?Instrument="+ elmnt.innerHTML
	newIframe.height = "40%"
	newIframe.width = "100%"
	newIframe.frameborder = "0"
	
	document.getElementById("internal").appendChild(newIframe);
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
	
	data = sortDictionary(data);
	var total_users = Object.keys(data).length;
	
	document.getElementById("totalUsers").innerHTML = total_users;
	document.getElementById("onlineUsers").innerHTML = Object.keys(onlineClients).length;
	document.getElementById("offlineUsers").innerHTML = Object.keys(offlineClients).length;
	
	clearBox("buttons")
	for (value in data){
		var newButton = document.createElement("button");
		
		newButton.innerHTML = value

		newButton.style.type = "btn";

		// Need to choose whether to display bigger or smaller buttons based on the
		// number of users, otherwise page might overflow and require scrolling
		var max_users_for_large_buttons = 15;
		if (total_users > max_users_for_large_buttons){
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
	}
	var time = document.getElementById("time");
	var date = new Date();
	time.innerHTML = "Last updated at: " + date.toLocaleTimeString();
	time.setAttribute("style", "color:black");
}

var windowWidth = $(window).width();
var windowHeight = $(window).height();
var buttonHeight = $(window).height();

open_wall_display();

$(document).ready(refresh_instruments());

setInterval(refresh_instruments, INST_REFRESH);
setInterval(refresh_wall_display, WALL_DISP_REFRESH);