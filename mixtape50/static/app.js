import { cleanTitle, removePunctuation, sleep } from './util.js';

/**
 * +-----------------------------+
 * | Authentication with Spotify |
 * +-----------------------------+
 * 
 * This is an example of a basic node.js script that performs
 * the Authorization Code with PKCE oAuth2 flow to authenticate 
 * against the Spotify Accounts.
 *
 * For more information, read
 * https://developer.spotify.com/documentation/web-api/tutorials/code-pkce-flow
 * 
 * Source:
 * https://github.com/spotify/web-api-examples/tree/master/authorization/authorization_code_pkce
 * 
 */

const clientId = '55a7da6ecd234a3986568cdff560d96b'; // clientId for mixtape50, not secret
const redirectUrl = 'https://mixtape50.onrender.com';         // your redirect URL - must be localhost URL and/or HTTPS

const authorizationEndpoint = "https://accounts.spotify.com/authorize";
const tokenEndpoint = "https://accounts.spotify.com/api/token";
const scope = 'playlist-modify-public playlist-modify-private playlist-read-private';

// Data structure that manages the current active token, stores it in memory
const currentToken = (() => {
  let tokenData = {
    access_token: null,
    refresh_token: null,
    expires_in: null,
    expires: null
  };

  return {
    get access_token() { return tokenData.access_token; },
    get refresh_token() { return tokenData.refresh_token; },
    get expires_in() { return tokenData.expires_in; },
    get expires() { return tokenData.expires; },

    save: function (response) {
      const { access_token, refresh_token, expires_in } = response;

      tokenData.access_token = access_token;
      tokenData.refresh_token = refresh_token;
      tokenData.expires_in = expires_in;

      const now = new Date();
      tokenData.expires = new Date(now.getTime() + (expires_in * 1000));
    },

    clear: function () {
      tokenData = {
        access_token: null,
        refresh_token: null,
        expires_in: null,
        expires: null
      };
    }
  };
})();


async function redirectToSpotifyAuthorize() {
  const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  const randomValues = crypto.getRandomValues(new Uint8Array(64));
  const randomString = randomValues.reduce((acc, x) => acc + possible[x % possible.length], "");

  const code_verifier = randomString;
  const data = new TextEncoder().encode(code_verifier);
  const hashed = await crypto.subtle.digest('SHA-256', data);

  const code_challenge_base64 = btoa(String.fromCharCode(...new Uint8Array(hashed)))
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');

  window.localStorage.setItem('code_verifier', code_verifier)

  const authUrl = new URL(authorizationEndpoint)
  const params = {
    response_type: 'code',
    client_id: clientId,
    scope: scope,
    code_challenge_method: 'S256',
    code_challenge: code_challenge_base64,
    redirect_uri: redirectUrl,
  };

  authUrl.search = new URLSearchParams(params).toString();
  window.location.href = authUrl.toString();
}


// Soptify API Calls
async function getToken(code) {
  let code_verifier = localStorage.getItem('code_verifier');
  const response = await fetch(tokenEndpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      client_id: clientId,
      grant_type: 'authorization_code',
      code: code,
      redirect_uri: redirectUrl,
      code_verifier: code_verifier,
    }),
  });

  return await response.json();
}


async function getUserID() {
  const response = await fetch("https://api.spotify.com/v1/me", {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${currentToken.access_token}` },
  });
  const data = await response.json();
  return data.id;
}


async function getTrackWithTitle(message) {
  const params = new URLSearchParams({
    q: `track:"${message}"`,
    type: "track",
    limit: 50,
  });

  const response = await fetch("https://api.spotify.com/v1/search?" + params.toString(), {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${currentToken.access_token}` },
  });

  return await response.json();
}


/**
 * Creates a Spotify playlist with the given tracks.
 * @param {String} title The title of the playlist.
 * @return {String} The playlist ID.
 */
async function userPlaylistCreate(title) {
  // Currently, we're using the first track for each matching song
  const userId = await getUserID();
  const response = await fetch(`https://api.spotify.com/v1/users/${userId}/playlists`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${currentToken.access_token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: title,
      description: 'Created with Mixtape50: https://github.com/jchanke/mixtape50.',
      public: false,
      collaborative: false,
    }),
  });
  const playlistID = await response
    .json()
    .then(data => data.id);
  return playlistID;
}


async function playlistAddTracks(playlistID, tracksList) {
  const response = await fetch(`https://api.spotify.com/v1/playlists/${playlistID}/tracks`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${currentToken.access_token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      uris: tracksList.map((track) => `spotify:track:${track.id}`),
    }),
  });
}

// Click handlers
async function loginWithSpotifyClick() {
  await redirectToSpotifyAuthorize();
}


/** 
 * +-----------------------------+
 * |         Page logic          |
 * +-----------------------------+
 */
// On page load, try to fetch auth code from current browser search URL
const args = new URLSearchParams(window.location.search);
const code = args.get('code');

// If we find a code, we're in a callback, do a token exchange
if (code) {
  const token = await getToken(code);
  currentToken.save(token);

  // Remove code from URL so we can refresh correctly.
  const url = new URL(window.location.href);
  url.searchParams.delete("code");

  const updatedUrl = url.search ? url.href : url.href.replace('?', '');
  window.history.replaceState({}, document.title, updatedUrl);
}


// If we don't have a token, we're not logged in, so render the login modal
if (!currentToken.access_token) {
  var loginModal = new bootstrap.Modal(document.getElementById("login-modal"), {});
  loginModal.show();
}


/**
 * +-----------------------------+
 * |         Updating UI         |
 * +-----------------------------+
 */
// DOM elements
var trackList = document.getElementById("tracks-list");
var statusBar = document.getElementById("status");
var uponComplete = document.getElementById("upon-complete");


async function addPrefix(title) {
  if (trackList.lastChild != null) {
    trackList.lastChild.className = "track m-1 px-1";
  }
  var newTrack = document.createElement("div");
  newTrack.innerHTML = title;
  newTrack.className = "m-1 px-1";
  trackList.appendChild(newTrack);
}

async function dropPrefix(title) {
  trackList.removeChild(trackList.lastChild);
}

async function lockIn() {
  // Lock in last newTrack
  trackList.lastChild.className = "track m-1 px-1";
  statusBar.innerHTML = "Success!";
}

function displayPlaylist(playlistID) {
  uponComplete.innerHTML = `<iframe src="https://open.spotify.com/embed/playlist/${playlistID}" width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>    `
}

function handleFailure(event) {
  // Prompt user to try again
  statusBar.innerHTML = "Not found.";
  uponComplete.innerHTML = "Reload this page to try again!";
}


/**
 * +-----------------------------+
 * |         Core logic          |
 * +-----------------------------+
 */

/**
 * A thin wrapper around `getTrackWithTitle` that keeps only the tracks that
 * match the cleaned message. Equivalent to `search_spotipy` in the original
 * implementation.
 * @param {string} query - The message to search.
 * @returns {Promise<Array>} - Returns a promise that resolves to an array of 
 * Spotify Track objects.
 */
async function searchSpotify(query) {
  const data = await getTrackWithTitle(query);
  if (!data.tracks) {
    return [];
  }
  const tracks = data.tracks.items;
  const cleanedQuery = removePunctuation(query.toLowerCase());
  const result = tracks.flatMap((track) => {
    const cleanedTitle = removePunctuation(cleanTitle(track.name.toLowerCase()));
    return cleanedTitle == cleanedQuery ? [track] : [];
  });
  return result;
}


/**
 * Makes an API call to the database to search for a track with the given title.
 * @param {string} message - The message to search.
 * @returns {Promise<Array>} - Returns a promise that resolves to an array of 
 * Spotify Track objects.
 */
async function searchDatabase(query) {
  const response = await fetch(`/search?q=${query}`);
  return response.json();
}


/**
 * Checks if the query is a valid Spotify track, by querying the lookup table,
 * the Spotify API, and then the database lookup, in that order.
 * @param {string} query - The query to search.
 * @param {Object} queryLookup - Memoization lookup for successful queries.
 * @returns {Promise<Array>} - Returns a promise that resolves to a list of 
 * Spotify Track objects, whose titles all match the query. Otherwise, returns 
 * an empty list.
 */
async function searchMessage(query) {
  const tracksFromSpotify = await searchSpotify(query);
  if (tracksFromSpotify.length > 0) {
    return tracksFromSpotify;
  }
  const tracksFromDatabase = await searchDatabase(query);
  if (tracksFromDatabase.length > 0) {
    return tracksFromDatabase;
  }
  return [];
}


/**
 * Memoize searchMessage.
 */
function memoize(fn) {
  const cache = {};
  // Here, arg is a String, so we can use it as a key directly
  return async function (...args) {
    const key = JSON.stringify(args);
    if (cache[key]) {
      return cache[key];
    }
    const result = await fn.apply(this, args);
    cache[key] = result;
    return result;
  }
}


/**
 * Splits message into tracks, side effects are handled externally.
 * @param {string} message - The message to search.
 * @param {number} maxSearchLength - Maximum number of words to search.
 * @param {Set} failedQueries - Set of failed queries.
 * @returns {Promise<Array>} - Returns a promise that resolves to an array of 
 * lists of Spotify Track objects, where each list of tracks corresponds to a
 * matching substring of the message.
 */
async function findMixtape(
  message,
  maxSearchLength = 10,
  failedQueries = new Set(),
  memoSearchMessageFn = null,
) {
  const memoSearchMessage = memoSearchMessageFn || memoize(searchMessage);

  // Clean message and split into words
  const cleanedMessage = removePunctuation(message.toLowerCase());
  const words = cleanedMessage.split(' ');
  const queryLength = Math.min(words.length, maxSearchLength);

  for (let i = 0; i < queryLength; i++) {
    const prefixList = words.slice(0, queryLength - i)
    const suffixList = words.slice(queryLength - i)
    const prefix = prefixList.join(' ');
    const suffix = suffixList.join(' ');
    addPrefix(prefix);
    if (failedQueries.has(suffix)) {
      sleep(100);
      dropPrefix(prefix);
      continue;
    }
    const prefixTracks = await memoSearchMessage(prefix);
    if (prefixTracks.length == 0) {
      sleep(100);
      dropPrefix(prefix);
      continue;
    }
    if (!suffix) {
      sleep(100);
      lockIn();
      return [prefixTracks];
    }
    const suffixTracks = await findMixtape(
      suffix,
      maxSearchLength,
      failedQueries,
      memoSearchMessage,
    );
    if (suffixTracks.length == 0) {
      sleep(100);
      dropPrefix(prefix);
      continue;
    }
    sleep(100);
    return [prefixTracks].concat(suffixTracks)
  }
  failedQueries.add(cleanedMessage);
  sleep(100);
  return [];
}


/**
 * Main logic for when user submits a message.
 */
async function onSubmitMessage() {
  // DOM elements
  var message = document.getElementById("message").value;
  const messageInputContainer = document.getElementById("message-input-container")
  const mixtapeContainer = document.getElementById("mixtape-container")

  // Update page when user submits message
  document.title = "Creating Mixtape...";
  messageInputContainer.hidden = true;
  mixtapeContainer.hidden = false;

  // Core logic of search
  const findMixtapeResults = await findMixtape(message);
  if (findMixtapeResults.length == 0) {
    handleFailure();
    return;
  }
  const playlistID = await userPlaylistCreate("mixtape50");
  // Currently, we're using the first track for each matching song
  const tracksList = findMixtapeResults.map((song) => song[0]);
  playlistAddTracks(playlistID, tracksList);
  displayPlaylist(playlistID);
}

/**
 * Expose callback functions to global scope
 */
window.onSubmitMessage = onSubmitMessage;
window.loginWithSpotifyClick = loginWithSpotifyClick;
