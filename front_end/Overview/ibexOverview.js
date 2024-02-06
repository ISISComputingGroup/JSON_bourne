var PORT = 443;
var HOST = "https://dataweb2.isis.rl.ac.uk"

var INST_REFRESH = 5000;
var WALL_DISP_REFRESH = 2 * 60 * 1000;
var TIMEOUT = 2500;

function refresh_instruments() {
	$.ajax({
		url: HOST + ":" + PORT + "/",
		dataType: 'jsonp',
		data: {"Instrument": "all"},
		timeout: TIMEOUT,
		error: function(xhr, status, error){ 
			document.getElementById("time").setAttribute("style", "color:red")
		},
		jsonpCallback: "display_data"
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

/**
 *	Gets a colour for a particular run status.
 */
function getColourFromRunState(runState){
	switch (runState){
		case "RUNNING":
			return "LIGHTGREEN";
		case "SETUP":
			return "LIGHTBLUE";
		case "PAUSED":
			return "RED";
		case "WAITING" || "VETOING":
			return "GOLDENROD";
		case "ENDING" || "ABORTING":
			return "BLUE";
		case "PAUSING":
			return "DARK_RED";
		default:
			return "YELLOW"
	}
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
	
	newIframe.src = "https://epics-jenkins.isis.rl.ac.uk/plugin/jenkinswalldisplay/walldisplay.html?viewName=WallDisplay&jenkinsUrl=https%3A%2F%2Fepics-jenkins.isis.rl.ac.uk%2F"
	newIframe.height = String(windowHeight*2/5)+"px"
	newIframe.width = "100%"
	
	document.getElementById("internal").appendChild(newIframe);	
}


function on_click(elmnt) {
	window.open("https://dataweb.isis.rl.ac.uk/IbexDataweb/default.html?Instrument="+ elmnt.childNodes[0].nodeValue, '_blank').focus();
}

function display_data(data){
	var instruments = data["instruments"];
	var total_users = Object.keys(instruments).length;
	var TS2_instruments = ["LET", "POLREF", "NIMROD", "IMAT", "SANS2D", "LARMOR", "WISH", "INTER", "OFFSPEC", "ZOOM"];
	var misc_machines = ["WISH_SETUP", "DETMON", "IRIS_SETUP", "DEMO", "PEARL_SETUP", "HRPD_SETUP", "SELAB", "SOFTMAT", "ENGINX_SETUP", "CHIPIR", "MUSR", "CHRONUS", "ARGUS", "HIFI", "MOTION", "SXD"];
	clearBox("TS1buttons")
	clearBox("TS2buttons")
	clearBox("Miscbuttons")
	for (value in instruments){
		var newButton = document.createElement("button");
		var run_state = instruments[value]["run_state"]
		newButton.innerHTML = value + "<div style=\"background-color:" + getColourFromRunState(run_state) + ";color:black\">" +  run_state + "</div>"

		newButton.style.type = "btn";

		// Need to choose whether to display bigger or smaller buttons based on the
		// number of users, otherwise page might overflow and require scrolling
		var max_users_for_large_buttons = 20;
		if (total_users > max_users_for_large_buttons){
			ending = "btn-large";
		} else {
			ending = "btn-xl";
		};	
		var blockListStyle = document.createAttribute("class");
		if (instruments[value]["is_up"] == true){
			blockListStyle.value = 'btn btn-success '+ending;
		} else{
			blockListStyle.value = 'btn btn-danger '+ending;
		}
        newButton.setAttributeNode(blockListStyle);
		var blockListStyle = document.createAttribute("onclick");
        blockListStyle.value = "on_click(this)"
		newButton.setAttributeNode(blockListStyle);
		var div_id = "TS1buttons";
		if (TS2_instruments.includes(value)) {
			div_id = "TS2buttons"
		}
		if (misc_machines.includes(value)) {
			div_id = "Miscbuttons"
		}
		document.getElementById(div_id).appendChild(newButton);
	}
	var time = document.getElementById("time");
	var date = new Date();
	time.innerHTML = "Last updated at: " + date.toLocaleTimeString();
	time.setAttribute("style", "color:black");

	var error = document.getElementById("error");
	if (data["error"] == "") {
	    error.innerHTML ="";
	} else {
	    error.innerHTML = "Error: " + data["error"];
	}

}

var windowWidth = $(window).width();
var windowHeight = $(window).height();
var buttonHeight = $(window).height();

open_wall_display();

$(document).ready(refresh_instruments());

setInterval(refresh_instruments, INST_REFRESH);
setInterval(refresh_wall_display, WALL_DISP_REFRESH);
