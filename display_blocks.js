var PORT = 60000;
var showPrivate = true;
var privateRunInfo = ["TITLE", "_USERNAME"];
var instrument = getURLParameter("Instrument");
var nodeInstTitle = document.createElement("H2");
var nodeConfigTitle = document.createElement("H2");
var instrumentState;
var showHidden;
var timeout = 1000;

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
    NUMSPECTRA: 'Number of Spectra'
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
		url: "http://dataweb.isis.rl.ac.uk:" + PORT + "/",
		dataType: 'jsonp',
		data: {"Instrument": instrument},
		timeout: timeout,
		error: function(xhr, status, error){ 
			window.location.replace("error.html")
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
    showHidden = document.getElementById("showHidden").checked;
	if ("DISPLAY" in instrumentState.inst_pvs) {
		showPrivate = getBoolean(instrumentState.inst_pvs["DISPLAY"]["value"]);
		delete instrumentState.inst_pvs["DISPLAY"];
	} else {
		showPrivate = true;
	}
    clear(nodeInstTitle);
    clear(nodeConfigTitle);

    nodeInstTitle.appendChild(document.createTextNode(instrument));
    nodeConfigTitle.appendChild(document.createTextNode("Configuration: " + instrumentState.config_name));

    document.getElementById("inst_name").appendChild(nodeInstTitle);
    document.getElementById("config_name").appendChild(nodeConfigTitle);

    // populate blocks
    var nodeGroups = document.getElementById("groups");
    getDisplayGroups(nodeGroups, instrumentState.groups);

    // populate run information
    var nodeInstPVs = document.getElementById("inst_pvs");
    var nodeInstPVList = document.createElement("UL");

    nodeInstPVs.appendChild(nodeInstPVList);
    getDisplayBlocks(nodeInstPVs, instrumentState.inst_pvs);
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
 * Adds html elements for a list of block objects to a given node.
 *
 * @param node The parent node.
 * @param blocks The list of block objects to display.
 * @return The updated node.
 */
function getDisplayBlocks(node, blocks) {
    clear(node)
    for (var key in blocks) {
        var block = blocks[key];
        if(block["visibility"] == false && !showHidden){
            continue;
        }

        var value = block["value"];
        var status_text = block["status"];
        var alarm = block["alarm"];

        var nodeBlock = document.createElement("LI");
        var attColour = document.createAttribute("color");
        var nodeBlockText = document.createTextNode(getTitle(key) + ":\u00A0\u00A0");

        // write block name
        nodeBlock.appendChild(nodeBlockText);

        // write status if disconnected
        if (status_text == "Disconnected") {
            var nodeBlockStatus = document.createElement("FONT");
            attColour.value = "BlueViolet";
            nodeBlockStatus.setAttributeNode(attColour);
            nodeBlockStatus.appendChild(document.createTextNode(status_text.toUpperCase()));
            nodeBlock.appendChild(nodeBlockStatus);
        }
        // write value if connected
        else if ((isInArray(privateRunInfo, key)) && !showPrivate) {
            var nodeBlockStatus = document.createElement("I");
            nodeBlockStatus.appendChild(document.createTextNode("Unavailable"));
            nodeBlock.appendChild(nodeBlockStatus);
        } else {
            nodeBlockText.nodeValue += value + "\u00A0\u00A0";
                // write alarm status if active
            if (!alarm.startsWith("null") && !alarm.startsWith("OK")) {
                var nodeBlockAlarm = document.createElement("FONT");
                attColour.value = "red";
                nodeBlockAlarm.setAttributeNode(attColour);
                nodeBlockAlarm.appendChild(document.createTextNode("(" + alarm + ")"));
                nodeBlock.appendChild(nodeBlockAlarm);
            }
        }
        node.appendChild(nodeBlock);
    }
    return node;
}

$(document).ready(refresh());

setInterval(refresh, 5000);