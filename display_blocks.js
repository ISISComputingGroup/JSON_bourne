var PORT = 60000;
var showPrivate = true;
var privateRunInfo = ["TITLE", "_USERNAME"];
var instrument = getURLParameter("Instrument");
var instrumentState;

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

function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)
            || [null, ''])[1].replace(/\+/g, '%20')) || null;
}

function isInArray(list, elem) {
    return list.indexOf(elem) > -1;
}

function getBoolean(stringval) {
    bool = true
    if (stringval.toUpperCase() == "NO") {
        bool = false;
    }
    return bool;
}

function refresh() {
    $.ajax({
    url: "http://localhost:" + PORT + "/",
//    url: "http://NDW1720:" + PORT + "/",
    dataType: 'jsonp',
    data: {"Instrument": instrument},
    jsonpCallback: "parseObject"
    });
}

$(document).ready(refresh())

function parseObject(obj) {
    instrumentState = obj;
    var nodeInstTitle = document.createElement("H2");
    var nodeConfigTitle = document.createElement("H2");

    nodeInstTitle.appendChild(document.createTextNode(instrument));
    nodeConfigTitle.appendChild(document.createTextNode("Configuration: " + instrumentState.config_name));

    document.getElementById("inst_name").appendChild(nodeInstTitle);
    document.getElementById("config_name").appendChild(nodeConfigTitle);

    // populate blocks list
    var groupTitles = Object.keys(instrumentState.groups);
    for (i = 0; i < groupTitles.length; i++) {
        var groupTitle = groupTitles[i];
        var blocks = instrumentState.groups[groupTitle];
        var nodeGroups = document.getElementById("groups");

        var nodeTitle = document.createElement("H3");
        nodeGroups.appendChild(nodeTitle);
        nodeTitle.appendChild(document.createTextNode(checkTitle(groupTitle)));

        var nodeBlockList = document.createElement("UL");
        nodeGroups.appendChild(nodeBlockList);

        var blockListStyle = document.createAttribute("style");
        blockListStyle.value = 'padding-left:20px';
        nodeBlockList.setAttributeNode(blockListStyle);
        console.log(instrumentState)
        getDisplayBlocks(nodeBlockList, blocks)

    }

    // populate run information
    showPrivate = getBoolean(obj.inst_pvs["DISPLAY"]["value"]);
    delete obj.inst_pvs["DISPLAY"];

    var instpv_titles = Object.keys(obj.inst_pvs);
    var nodeInstPVs = document.getElementById("inst_pvs");
    var nodeInstPVList = document.createElement("UL");
    nodeInstPVs.appendChild(nodeInstPVList);

    for (i = 0; i < instpv_titles.length; i++) {
        var title = instpv_titles[i];
        var value = obj.inst_pvs[title]["value"];
        var status_text = obj.inst_pvs[title]["status"];
        var alarm = obj.inst_pvs[title]["alarm"];

        var nodePV = document.createElement("LI");
        var nodePVText = document.createTextNode(dictInstPV[title] + ":\u00A0\u00A0");
        var attColour = document.createAttribute("color");

        // write pv name
        nodePV.appendChild(nodePVText);

        // write status if disconnected
        if (status_text == "Disconnected") {
            var nodePVStatus = document.createElement("FONT");
            attColour.value = "BlueViolet";
            nodePVStatus.setAttributeNode(attColour);
            nodePVStatus.appendChild(document.createTextNode(status_text.toUpperCase()));
            nodePV.appendChild(nodePVStatus);
        }
        // write value if connected
        else if ((isInArray(privateRunInfo, instpv_titles[i])) && !showPrivate) {
            var nodePVStatus = document.createElement("I");
            nodePVStatus.appendChild(document.createTextNode("Unavailable"));
            nodePV.appendChild(nodePVStatus);
        } else {
            nodePVText.nodeValue += value + "\u00A0\u00A0"
            // write alarm status if active
            if (!alarm.startsWith("null") && !alarm.startsWith("OK")) {
                var nodePVAlarm = document.createElement("FONT");
                attColour.value = "red";
                nodePVAlarm.setAttributeNode(attColour);
                nodePVAlarm.appendChild(document.createTextNode("(" + alarm + ")"));
                nodePV.appendChild(nodePVAlarm);
            }
        }
        nodeInstPVList.appendChild(nodePV);
    }
}

function checkTitle(title) {
    if (title === "NONE") {
        title = "OTHER";
    }
    return title;
}


function getDisplayBlocks(node, blocks) {
    // clear
    while (node.firstChild) {
        node.removeChild(node.firstChild);
    }

    // populate
    for (var key in blocks) {
        var block = blocks[key]
        var value = block["value"];
        var status_text = block["status"];
        var alarm = block["alarm"];

        var nodeBlock = document.createElement("LI");
        var attColour = document.createAttribute("color");
        var nodeBlockText = document.createTextNode(key + ":\u00A0\u00A0");

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
        else {
            nodeBlockText.nodeValue += value + "\u00A0\u00A0"
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
}

// function toggleHidden(state) {
//     state is bool
// }