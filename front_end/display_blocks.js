var PORT = 60000;
var HOST = "http://dataweb.isis.rl.ac.uk"

var instrument = getURLParameter("Instrument");
var nodeInstTitle = document.createElement("H2");
var nodeConfigTitle = document.createElement("H2");
var nodeTimeDiffTitle = document.createElement("H2");
var instrumentState;
var showHidden;
var timeout = 4000;

dictInstPV = {
    RUNSTATE: 'Run Status',
    RUNNUMBER: 'Run Number',
    _RBNUMBER: 'RB Number',
    _USERNAME: 'User(s)',
    TITLE: 'Title',
    TITLEDISP: 'Show Title',
    STARTTIME: 'Start Time',
    RUNDURATION: 'Total Run Time',
    RUNDURATION_PD: 'Period Run Time',
    GOODFRAMES: 'Good Frames (Total)',
    GOODFRAMES_PD: 'Good Frames (Period)',
    RAWFRAMES: 'Raw Frames (Total)',
    RAWFRAMES_PD: 'Raw Frames (Period)',
    PERIOD: 'Current Period',
    NUMPERIODS: 'Number of Periods',
    PERIODSEQ: 'Period Sequence',
    BEAMCURRENT: 'Beam Current',
    TOTALUAMPS: 'Total Uamps',
    COUNTRATE: 'Count Rate',
    DAEMEMORYUSED: 'DAE Memory Used',
    TOTALCOUNTS: 'Total DAE Counts',
    DAETIMINGSOURCE: 'DAE Timing Source',
    MONITORCOUNTS: 'Monitor Counts',
    MONITORSPECTRUM: 'Monitor Spectrum',
    MONITORFROM: 'Monitor From',
    MONITORTO: 'Monitor To',
    NUMTIMECHANNELS: 'Number of Time Channels',
    NUMSPECTRA: 'Number of Spectra',
    SHUTTER: 'Shutter Status',
    SIM_MODE: 'DAE Simulation mode',
    TIME_OF_DAY: 'Instrument time',
};

/**
 * Gets the proper display title for a PV.
 *
 * @param {string} title The actual title of the PV.
 * @return {string} The title for display on the page.
 */
function getTitle(title) {
    if (title in dictInstPV){
        return dictInstPV[title];
    }
    return title;
}

/**
 * Checks whether a given group is the "None" group and replaces the title with "Other" if so.
 *
 * @param {string} title The title of the group.
 * @return {string} The correct title for the group.
 */
function checkGroupNone(title) {
    if (title === "NONE") {
        title = "OTHER";
    }
    return title;
}

/**
 * Returns the value of a parameter set in the URL.
 *
 * @param {string} name The name of the parameter.
 * @return {string} The value of the parameter.
 */
function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)
            || [null, ''])[1].replace(/\+/g, '%20')) || null;
}

/**
 * Checks whether a list contains a certain element.
 *
 * @param list The list of elements.
 * @param elem The element to look for in the list.
 * @return {boolean} Whether elem is contained in list.
 */
function isInArray(list, elem) {
    return list.indexOf(elem) > -1;
}

/**
 * Converts a String PV value ("YES" / "NO") into a boolean.
 *
 * @param stringval The string to convert.
 * @return {boolean} The resulting boolean value.
 */
function getBoolean(stringval) {
    if (stringval.toUpperCase() == "NO") {
        return false;
    }
    return true;
}

/**
 * Clears a given node of all child elements.
 *
 * @param node The node to be cleared.
 */
function clear(node) {
    while (node.firstChild) {
        node.removeChild(node.firstChild);
    }
}

/**
 * Fetches the latest instrument data.
 */
function refresh() {
	$.ajax({
		url: HOST + ":" + PORT + "/",
		dataType: 'jsonp',
		data: {"Instrument": instrument},
		timeout: timeout,
		error: function(xhr, status, error){
			displayError();
		},
		success: function(data){
			parseObject(data);
		}
	});
}

/**
 * Parses fetched instrument data into a human-readable html page.
 */
function parseObject(obj) {
    // set up page
    instrumentState = obj;
	createTitle(obj)
    showHidden = document.getElementById("showHidden").checked;
    clear(nodeInstTitle);
    clear(nodeConfigTitle);
    clear(nodeTimeDiffTitle);

    // populate blocks
    var nodeGroups = document.getElementById("groups");
    getDisplayGroups(nodeGroups, instrumentState.groups);

    // populate run information
    var nodeInstPVs = document.getElementById("inst_pvs");
    var nodeInstPVList = document.createElement("ul");

    getDisplayRunInfo(nodeInstPVs, instrumentState.inst_pvs);

    getDisplayTimeDiffInfo(instrumentState);

    nodeInstTitle.appendChild(document.createTextNode(instrument));
    nodeConfigTitle.appendChild(document.createTextNode("Configuration: " + instrumentState.config_name));

    document.getElementById("config_name").appendChild(nodeConfigTitle);

	setVisibilityMode('block');
}


function clearBox(elementID){
    document.getElementById(elementID).innerHTML = "";
}

function getDisplayTimeDiffInfo(instrumentState){
    if (instrumentState.outdated)  {
      nodeTimeDiffTitle.appendChild(document.createTextNode("There is a time shift of " + instrumentState.time_diff + " seconds between the instrument and the web server. Dataweb may not be updating correctly."));
      document.getElementById("time_diff").appendChild(nodeTimeDiffTitle);
      document.getElementById("time_diff").style.color = "RED";
    }
}

/**
 * creates a Title at the top looking similar to the IBEX GUI
 */
function createTitle(inst_details){
	clearBox("top_bar");
  document.body.style.padding = '20px'
	document.getElementById("top_bar").innerHTML = "<div id = \"inst_name\"></div><table style=\"width:100%\"><tr id = table_part><th id = \"next_part\" style = \"padding: 10px; width:33%; background-color:lightgrey ; border: black 2px solid\";></th></tr></table>";
	runStatus = inst_details["inst_pvs"]["RUNSTATE"]["value"];

	colour = getColourFromRunState(runStatus);

	document.getElementById("inst_name").style.padding = "10px";
	document.getElementById("inst_name").style.backgroundColor = colour;
	document.getElementById("inst_name").style.border = "black 2px solid";
	var title = document.createElement("h2");
	title.innerHTML = instrument.toUpperCase() + " is " + runStatus;
	var blockListClass = document.createAttribute("class");
	blockListClass.value = "text-center";
	title.setAttributeNode(blockListClass);
	document.getElementById("inst_name").appendChild(title);

	addItemToTable("Title", inst_details["inst_pvs"]["TITLE"]["value"]);
	addItemToTable("Users", inst_details["inst_pvs"]["_USERNAME"]["value"]);

	newPartOfTable();

	addItemToTable("Good / Raw Frames", inst_details["inst_pvs"]["GOODFRAMES"]["value"]+"/"+inst_details["inst_pvs"]["RAWFRAMES"]["value"]);
	addItemToTable("Current / Total", inst_details["inst_pvs"]["BEAMCURRENT"]["value"]+"/"+inst_details["inst_pvs"]["TOTALUAMPS"]["value"]);
	addItemToTable("Monitor Counts", inst_details["inst_pvs"]["MONITORCOUNTS"]["value"]);

	newPartOfTable();

	addItemToTable("Start Time", inst_details["inst_pvs"]["STARTTIME"]["value"]);
	addItemToTable("Run Time", inst_details["inst_pvs"]["RUNDURATION_PD"]["value"]);
	addItemToTable("Period", inst_details["inst_pvs"]["PERIOD"]["value"]+"/"+inst_details["inst_pvs"]["NUMPERIODS"]["value"]);

}

/**
 *	Gets a colour for a particular run status.
 */
function getColourFromRunState(runState){
	switch (runStatus){
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

/**
  *	Create a new part of the table in the top bar.
  */
function newPartOfTable(){
	document.getElementById("next_part").removeAttribute("id");
	document.getElementById("table_part").innerHTML += "<th id = \"next_part\" style = \"padding: 10px; background-color:lightgrey; width:33%; border: black 2px solid\";></th>";
}

/**
  *	Add an item to the table in the top bar.
  */
function addItemToTable(name, value) {
	var elem = document.createElement("h4");
	var textnode = document.createTextNode(name + ": " + value);
	elem.appendChild(textnode)
	document.getElementById("next_part").appendChild(elem);
}

/**
 * Display an error when connection to server couldn't be made.
 */
function displayError() {

    clear(nodeInstTitle);
    clear(nodeConfigTitle);
    nodeConfigTitle.appendChild(document.createTextNode("Could not connect to " + instrument + ", check IBEX server is running."));

	document.getElementById("top_bar").innerHTML = instrument;
	document.getElementById("config_name").appendChild(nodeConfigTitle);

	setVisibilityMode('none');
}

/*
 *  Sets the visibility of the run information, blocks and checkbox
 */
 function setVisibilityMode(mode){
	document.getElementById("run_information").style.display = mode;
	document.getElementById("blocks").style.display = mode;
	document.getElementById("showHiddenContainer").style.display = mode;
 }

/**
 * Adds html elements for a list of group objects to a given node.
 *
 * @param node The parent node.
 * @param groups The list of group objects to display.
 * @return The updated node.
 */
function getDisplayGroups(node, groups) {
    clear(node);
    for (var key in groups) {
        var group = groups[key];
        var nodeGroups = document.getElementById("groups");

        var nodeBlockList = document.createElement("UL");

        var blocks = instrumentState.groups[key];
        var displayBlocks = getDisplayBlocks(nodeBlockList, blocks);

        // Do not display empty groups
        if (displayBlocks.childElementCount != 0) {
            var nodeTitle = document.createElement("H3");
            nodeGroups.appendChild(nodeTitle);
            nodeTitle.appendChild(document.createTextNode(checkGroupNone(key)));
            nodeGroups.appendChild(nodeBlockList);

            var blockListStyle = document.createAttribute("style");
            blockListStyle.value = 'padding-left:20px';
            nodeBlockList.setAttributeNode(blockListStyle);

            node.appendChild(displayBlocks);
        }
    }
    return node;
}

/**
 * Adds a single block html element to the parent node
 *
 * @param node The parent node.
 * @param block The block to add.
 * @param blockName The name of the block to display.
 * @return The updated node.
 */
function displayOneBlock(node, block, blockName) {
    if(block["visibility"] == false && !showHidden){
        return;
    }

    var value = block["value"];
    var status_text = block["status"];
    var alarm = block["alarm"];

    var rc_inrange = block["rc_inrange"];
    var rc_enabled = block["rc_enabled"];
    var nodeBlock = document.createElement("LI");
    var nodeBlockText = document.createTextNode(blockName + ":\u00A0\u00A0");

    // write block name
    nodeBlock.appendChild(nodeBlockText);

    // write status if disconnected
    if (status_text == "Disconnected") {
	    writeStatus(nodeBlock, status_text);
    // write value, range info & alarms
    } else {
        nodeBlockText.nodeValue += value + "\u00A0\u00A0";
        // write range information about the PV
        if (rc_enabled === "YES" && (rc_inrange === "YES" || rc_inrange === "NO")) {
            writeRangeInfo(nodeBlock, rc_inrange);
        }
        // write alarm status if active
        if (!alarm.startsWith("null") && alarm !== "") {
            writeAlarmInfo(nodeBlock, alarm);
        }
    }
    node.appendChild(nodeBlock);
}

/**
 * Adds html elements for a list of block objects to a given node.
 *
 * @param node The parent node.
 * @param blocks The list of block objects to display.
 * @return The updated node.
 */
function getDisplayBlocks(node, blocks) {
    for (var key in blocks) {
        var block = blocks[key];
        displayOneBlock(node, block, key);
    }

	return node;
}

/**
 * Adds html elements for the list of instrument information.
 *
 * @param node The parent node.
 * @param blocks The list of instrument blocks.
 * @return The updated node.
 */
function getDisplayRunInfo(node, blocks){
    clear(node)
    // Add all in order first
    for (var key in dictInstPV) {
        if (key in blocks) {
            var block = blocks[key];
            displayOneBlock(node, block, getTitle(key));
            delete blocks[key]
        }
    }

    // Add any left over on to the end
    getDisplayBlocks(node, blocks);
}

function writeStatus(nodeBlock, status_text) {
	var nodeBlockStatus = document.createElement("span");
	nodeBlockStatus.style = "color:blueviolet"
	nodeBlockStatus.appendChild(document.createTextNode(status_text.toUpperCase()));
	nodeBlock.appendChild(nodeBlockStatus);
}

function writeRangeInfo(nodeBlock, rc_inrange) {
    var nodeBlockInrange = document.createElement("span");
    var colour = "Red";
    var mark_status = "\u274C"; // unicode cross mark

    if (rc_inrange == "YES") {
        colour = "Green";
        mark_status = "\u2713"; // unicode check mark
    }
	nodeBlockInrange.style = "color:"+color
    nodeBlockInrange.appendChild(document.createTextNode(mark_status));
    nodeBlock.appendChild(nodeBlockInrange);
}

function writeAlarmInfo(nodeBlock, alarm) {
    var nodeBlockAlarm = document.createElement("span");
    nodeBlockAlarm.style = "color:red"
	nodeBlockAlarm.appendChild(document.createTextNode("(" + alarm + ")"));
    nodeBlock.appendChild(nodeBlockAlarm);
}

// At the start, assume we can't connect
// This will update when a connection is made
$(document).ready(displayError());

$(document).ready(refresh());

setInterval(refresh, 5000);
