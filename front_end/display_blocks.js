var PORT = 60000;
var HOST = "http://dataweb.isis.rl.ac.uk"

var instrument = getURLParameter("Instrument");
var nodeInstTitle = document.createElement("H2");
var nodeConfigTitle = document.createElement("H2");
var instrumentState;
var showHidden;
var timeout = 4000;

dictInstPV = {
    RUNSTATE: 'Run Status',
    RUNNUMBER: 'Run Number',
    _RBNUMBER: 'RB Number',
    TITLEDISP: 'Show Title',
    STARTTIME: 'Start Time',
    RUNDURATION: 'Total Run Time',
    RUNDURATION_PD: 'Period Run Time',
    GOODFRAMES: 'Good Frames (Total)',
    GOODFRAMES_PD: 'Good Frames (Period)',
    RAWFRAMES: 'Raw Frames (Total)',
    RAWFRAMES_PD: 'Raw Frames (Period)',
    PERIODSEQ: 'Period Sequence',
    COUNTRATE: 'Count Rate',
    DAEMEMORYUSED: 'DAE Memory Used',
    TOTALCOUNTS: 'Total DAE Counts',
    DAETIMINGSOURCE: 'DAE Timing Source',
    MONITORSPECTRUM: 'Monitor Spectrum',
    MONITORFROM: 'Monitor From',
    MONITORTO: 'Monitor To',
    NUMTIMECHANNELS: 'Number of Time Channels',
    NUMSPECTRA: 'Number of Spectra',
	SIM_MODE: 'DAE Simulation mode'
};

dictLongerInstPVs = {
    "1:1:LABEL" : "1:1:VALUE",
    "2:1:LABEL" : "2:1:VALUE",
    "3:1:LABEL" : "3:1:VALUE",
    "1:2:LABEL" : "1:2:VALUE",
    "2:2:LABEL" : "2:2:VALUE",
    "3:2:LABEL" : "3:2:VALUE",
    "BANNER:MIDDLE:LABEL" : "BANNER:MIDDLE:VALUE",
    "BANNER:RIGHT:LABEL"  : "BANNER:RIGHT:VALUE",
    "BANNER:LEFT:LABEL"   : "BANNER:LEFT:VALUE",
}


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

    // populate blocks
    var nodeGroups = document.getElementById("groups");
    getDisplayGroups(nodeGroups, instrumentState.groups);

    // populate run information
    var nodeInstPVs = document.getElementById("inst_pvs");
    var nodeInstPVList = document.createElement("ul");

    getDisplayRunInfo(nodeInstPVs, instrumentState.inst_pvs);

    nodeInstTitle.appendChild(document.createTextNode(instrument));
    nodeConfigTitle.appendChild(document.createTextNode("Configuration: " + instrumentState.config_name));

    document.getElementById("config_name").appendChild(nodeConfigTitle);

	setVisibilityMode('block');
}


function clearBox(elementID){
    document.getElementById(elementID).innerHTML = "";
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
    try {
        // after upgrade script
        addItemToTable(inst_details["inst_pvs"]["1:1:LABEL"]["value"], inst_details["inst_pvs"]["1:1:VALUE"]["value"]);
        addItemToTable(inst_details["inst_pvs"]["2:1:LABEL"]["value"], inst_details["inst_pvs"]["2:1:VALUE"]["value"]);
        addItemToTable(inst_details["inst_pvs"]["3:1:LABEL"]["value"], inst_details["inst_pvs"]["3:1:VALUE"]["value"]);

        newPartOfTable();

        addItemToTable(inst_details["inst_pvs"]["2:2:LABEL"]["value"], inst_details["inst_pvs"]["2:2:VALUE"]["value"]);
        addItemToTable(inst_details["inst_pvs"]["1:2:LABEL"]["value"], inst_details["inst_pvs"]["1:2:VALUE"]["value"]);
        addItemToTable(inst_details["inst_pvs"]["3:2:LABEL"]["value"], inst_details["inst_pvs"]["3:2:VALUE"]["value"]);
    } catch(err) {
        // before upgrade script

        addItemToTable("Good / Raw Frames", inst_details["inst_pvs"]["GOODFRAMES"]["value"]+"/"+inst_details["inst_pvs"]["RAWFRAMES"]["value"]);
        addItemToTable("Current / Total", inst_details["inst_pvs"]["BEAMCURRENT"]["value"]+"/"+inst_details["inst_pvs"]["TOTALUAMPS"]["value"]);
        addItemToTable("Monitor Counts", inst_details["inst_pvs"]["MONITORCOUNTS"]["value"]);

        newPartOfTable();

        addItemToTable("Start Time", inst_details["inst_pvs"]["STARTTIME"]["value"]);
        addItemToTable("Run Time", inst_details["inst_pvs"]["RUNDURATION_PD"]["value"]);
        addItemToTable("Period", inst_details["inst_pvs"]["PERIOD"]["value"]+"/"+inst_details["inst_pvs"]["NUMPERIODS"]["value"]);

    }


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
    var splitter = " "
    if (name.slice(-1) != ":") splitter = ": ";
	var elem = document.createElement("h4");
	var textnode = document.createTextNode(name + splitter + value);
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
        var displayBlocks = getDisplayBlocks(nodeBlockList, blocks, true);

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
 * @param linkGraph link to block history graph.
 * @return The updated node.
 */
function displayOneBlock(node, block, blockName, linkGraph) {
    if(block["visibility"] == false && !showHidden){
        return;
    }

    var value = block["value"];
    var status_text = block["status"];
    var alarm = block["alarm"];

    var rc_inrange = block["rc_inrange"];
    var rc_enabled = block["rc_enabled"];
    var nodeBlock = document.createElement("LI");
    var nodeBlockNameText = document.createTextNode(blockName + ":\u00A0\u00A0");

    if (linkGraph) {
        var linkBlock = document.createElement("a");
        linkBlock.target = "_blank";
        linkBlock.href = "https://shadow.nd.rl.ac.uk/grafana/d/wMlwwaHMk/block-history?viewPanel=2&orgId=1&var-block=" +
                         blockName + "&var-inst=" + instrument.toUpperCase().replace(/-/g, "_");
        linkBlock.appendChild(nodeBlockNameText);
        nodeBlock.appendChild(linkBlock);
    } else {
        nodeBlock.appendChild(nodeBlockNameText);
    }

    // write status if disconnected
    if (status_text == "Disconnected") {
        writeStatus(nodeBlock, status_text);
    // write value, range info & alarms
    } else {
        nodeBlockValueText = document.createTextNode(value + ":\u00A0\u00A0");
        nodeBlock.appendChild(nodeBlockValueText);
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
 * Adds html elements from a list of block objects to a given node.
 *
 * @param node The parent node.
 * @param blocks The list of block objects to display.
 * @param linkGraph link to history graph.
 * @return The updated node.
 */
function getDisplayBlocks(node, blocks, linkGraph) {
    ignore_pvs = [
        "1:1:VALUE", "2:1:VALUE", "3:1:VALUE", "1:2:VALUE", "2:2:VALUE", "3:2:VALUE", "BANNER:RIGHT:VALUE", "BANNER:LEFT:VALUE", "BANNER:MIDDLE:VALUE", 
        "BEAMCURRENT", "PERIOD", "NUMPERIODS", "TOTALUAMPS", "MONITORCOUNTS", "SHUTTER", "_USERNAME", "TITLE"
    ];
    
    for (var key in blocks) {
        if (key in dictInstPV) {
            continue
        }
        if (key in dictLongerInstPVs) {
            var block = blocks[key];
            if (block["value"] != "") {
                var label = block["value"].slice(0, -1);
                displayOneBlock(node, blocks[dictLongerInstPVs[key]], label, linkGraph);
            }
        } else if (ignore_pvs.indexOf(key) >= 0) {
            // Do nothing
        } else {
            var block = blocks[key];
            displayOneBlock(node, block, key, linkGraph);
        }
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

    // Add variable parameters at the top of the list
    getDisplayBlocks(node, blocks, false);

    // Add the fixed parameters
    for (var key in dictInstPV) {
        if (key in blocks) {
            var block = blocks[key];
            displayOneBlock(node, block, getTitle(key), false);
        }
    }
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
	nodeBlockInrange.style = "color:" + colour
    nodeBlockInrange.appendChild(document.createTextNode(mark_status));
    nodeBlock.appendChild(nodeBlockInrange);
}

function writeAlarmInfo(nodeBlock, alarm) {
    var nodeBlockAlarm = document.createElement("a");
    nodeBlockAlarm.style = "color:red"
    nodeBlockAlarm.href = "https://github.com/ISISComputingGroup/ibex_user_manual/wiki/Blocks#alarms"
    nodeBlockAlarm.target = "_blank"
	nodeBlockAlarm.appendChild(document.createTextNode("(" + alarm + ")"));
    nodeBlock.appendChild(nodeBlockAlarm);
}

// At the start, assume we can't connect
// This will update when a connection is made
$(document).ready(displayError());

$(document).ready(refresh());

setInterval(refresh, 5000);
