var evtSource = new EventSource("/listen");
var eventList = document.getElementById("tracks-list");

evtSource.onopen = () => console.log("Connection requested...");
evtSource.onmessage = (event) => console.log(event.data);
evtSource.onerror = (error) => console.error("EventSource failed:", error);

evtSource.addEventListener("add", addPrefix);
evtSource.addEventListener("drop", removePrefix);
evtSource.addEventListener("lock in", lockIn);
evtSource.addEventListener("send songs", getSongs)

function addPrefix(event) {
    // DEBUG:
    console.log("add: " + event.data);

    // First, lock in previous track
    if (eventList.lastChild.firstChild != null)
    {
        eventList.lastChild.firstChild.className = "track";
    }

    // Create a span ("newElement")
    // ┌──────────┬──────────┐
    // │ newTrack │ newSpace │
    // └──────────┴──────────┘
    var newElement = document.createElement("span");
    var newTrack = document.createElement("span");
    var newSpace = document.createElement("span");
    newTrack.innerHTML = event.data;
    newSpace.innerHTML = " ";
    newElement.appendChild(newTrack);
    newElement.appendChild(newSpace);
    eventList.appendChild(newElement);
}

function removePrefix(event) {
    // DEBUG:
    console.log("drop: " + event.data);

    eventList.removeChild(eventList.lastChild);
}

function lockIn(event) {
    // DEBUG:
    console.log("lock in");
    eventList.lastChild.lastChild.remove(); // remove last newSpace
    eventList.lastChild.lastChild.className = "track"; // lock in last track
}

function getSongs(event) {
    // DEBUG:
    console.log("received songs");

    // Parse songsList as a JSON object
    var songsList = JSON.parse(event.data);
    
    // Log each song in songsList
    for (var i = 0; i < songsList.length; i++)
    {
        console.log(songsList[i]);
    }
    
    evtSource.close();
}