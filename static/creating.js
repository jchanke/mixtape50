var evtSource = new EventSource("/listen");
var eventList = document.getElementById("tracks-list");
var statusBar = document.getElementById("status");
var uponComplete = document.getElementById("upon-complete");

evtSource.onopen = () => console.log("Connection requested...");
evtSource.onmessage = (event) => console.log(event.data);
evtSource.onerror = (error) => console.error("EventSource failed:", error);

evtSource.addEventListener("add", addPrefix);
evtSource.addEventListener("drop", removePrefix);

// Success:
evtSource.addEventListener("lock in", lockIn);
evtSource.addEventListener("send songs", getSongs);
evtSource.addEventListener("send playlist", displayPlaylist);

// Failure:
evtSource.addEventListener("failed", handleFailure);

function addPrefix(event) {
    console.log("add: " + event.data);

    // First, lock in previous track
    if (eventList.lastChild != null)
    {
        eventList.lastChild.className = "track m-1 px-1";
    }

    // Create a div ("newTrack")
    var newTrack = document.createElement("div");
    newTrack.innerHTML = event.data;
    newTrack.className = "m-1 px-1";

    // Add newTrack to eventList
    eventList.appendChild(newTrack);
}

function removePrefix(event) {
    console.log("drop: " + event.data);
    eventList.removeChild(eventList.lastChild);
}

function lockIn(event) {
    console.log("lock in");

    // Lock in last newTrack
    eventList.lastChild.className = "track m-1 px-1";

    // Update status from 'Searching:' to 'Success!'
    statusBar.innerHTML = "Success!";
}

function getSongs(event) {
    console.log("received songs");

    // Parse songsList as a JSON object
    var songsList = JSON.parse(event.data);
    
    // Log each song in songsList
    for (var i = 0; i < songsList.length; i++)
    {
        console.log(songsList[i]);
    }
}

function displayPlaylist(event) {
    console.log("creating playlist");
    var playlistId = event.data;
    uponComplete.innerHTML = `<iframe src="https://open.spotify.com/embed/playlist/${playlistId}" width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>    `
}

function handleFailure(event) {
    console.log("no results");

    // Close connection to evtSource
    evtSource.close()

    // Prompt user to try again
    statusBar.innerHTML = "Not found.";
    uponComplete.innerHTML = "Close this window to try again!";
}