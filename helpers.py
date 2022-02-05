"""
Does the legwork of searching for matching tracks.

Contains:

(0) Create MessageAnnouncer class (adapted from: https://maxhalford.github.io/blog/flask-sse-no-deps/)
 - MessageAnnouncer
 - format_sse

(1) Search functions:
 - search_message
 - search_spotipy
 - search_db
 - search_lookup

(2) String parses (to clean title name):
 - clean_title
 - remove_punctuation
"""
from typing import Any, List, Dict, Union
import os
import re
import sqlite3
import queue # for MessageAnnouncer

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Localhost URL to access the application; Flask runs on port 5000 by default 
# Adapated from https://github.com/Deffro/statify/blob/dd15a6e70428bd36ecddb5d4a8ac3d82b85c9339/code/server.py#L553
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5000

# Get environment variables
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = f"{CLIENT_SIDE_URL}:{PORT}/callback"

SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private"

# Set up Spotipy
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE,
))


"""
(0) Create MessageAnnouncer class
(Adapted from: https://maxhalford.github.io/blog/flask-sse-no-deps/)
"""
class MessageAnnouncer:

    def __init__(self):
        """
        Creates a list listeners or queue objects.
        """
        self.listeners: List[queue.Queue] = []

    def listen(self):
        """
        Creates a new queue object, and adds it to self.listeners.
        Returns the queue object.	
        """
        q = queue.Queue(maxsize=5)
        self.listeners.append(q)
        self.listeners[-1].put_nowait(format_sse(data = "You have successfully connected."))
        return q

    def announce(self, message):
        """
        Goes through queues in listeners from last to first;
        if queue is full, delete that queue.
        """
        for q in reversed(self.listeners):
            # Tries to add message to queue, else raises exception queue.Full
            try:
                q.put_nowait(message)
            except queue.Full:
                del q

announcer = MessageAnnouncer()

def format_sse(data: str = "", event = None) -> str:
    """
    Formats data to the event-stream format.

    https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#event_stream_format
    """
    message = f"data: {data}\n\n"

    # If event is specified, prepend "event: {event}\n"
    if event is not None:
        message = f"event: {event}\n{message}"

    return message


"""
(1) Search functions:
    - search_message
    - search_spotipy
    - search_db
    - search_lookup
"""

def search_message(message: str, max_search_length: int = 10,
                   query_lookup: Dict[str, list] = dict(), failed_queries: set = set()) -> List[Union[list, Any]]:
    """
    search_message(message, max_search_length = 10)
    
    Returns a list of song names (change to ids) matching the message.
    Uses regex-style greedy search.

    Song names will be limited to [max_search_length] words (default is 10, can
    be adjusted.)

    Returns songs from Spotify API via spotipy library; if not, checks
    Spotify 1.2M songs dataset via an sqlite3 query.

    https://www.kaggle.com/rodolfofigueroa/spotify-12m-songs
    """
    
    # Split message into words
    message = remove_punctuation(message.casefold()).split()
    
    # Gets up to max_search_length words of message
    query_length = min(max_search_length, len(message))

    # List containing search functions to iterate over
    search_functions = [search_lookup,
                        search_spotipy,
                        search_db]

    # Splits query into prefix and suffix, decrementing prefix, until
    #  - prefix exactly matches a song
    #  - suffix can be expressed as a list of songs
    for i in range(query_length):

        prefix, suffix = message[:query_length - i], message[query_length - i:]
        prefix, suffix = " ".join(prefix), " ".join(suffix)

        announcer.announce(format_sse(data = prefix, event = "add"))

        # Only search if both prefix and suffix are not known to fail
        if not (prefix in failed_queries or suffix in failed_queries):
        
            # Looping through search functions,
            for search_function in search_functions:
             
                # Search for tracks matching prefix
                prefix_results = search_function(prefix, query_lookup=query_lookup)
                
                if prefix_results:
                    query_lookup[prefix] = prefix_results
                    print(f"Try: {prefix}")

                    # Base case: if prefix is whole message, suffix == "", so we should just return prefix
                    if suffix == "":
                        print(f"All done!")
                        announcer.announce(format_sse(event = "lock in"))
                        return [prefix_results]
                    
                    # Recursive case: make sure suffix it can be split into songs as well
                    else:
                        
                        # Search for tracks matching suffix
                        suffix_results = search_message(suffix, max_search_length = max_search_length,
                                                        query_lookup = query_lookup, failed_queries = failed_queries)
                        if suffix_results:
                            return [prefix_results] + suffix_results
                        
                        # Suffix cannot be split into songs: add to failed queries
                        else:
                            failed_queries.add(suffix)
                            print(f"\"{suffix}\" not found.")
            
                # Prefix not found in this search function
                else:
                    print(f"\"{prefix}\" not found in {search_function.__name__.replace('search_', '')}.")
        
        # Prefix not found, drop it
        announcer.announce(format_sse(event = "drop"))

    # Recursive case: failure
    return []

def search_lookup(query: str, query_lookup: Dict[str, list]) -> list:
    """
    Checks query_lookup (a dictionary created at the initial function call
    of search_message) and returns the results of the query if it has
    already been found.
    """
    # Checks query_lookup dict
    if query in query_lookup:
        return query_lookup[query]

    else:
        return []

def search_spotipy(query: str, query_lookup: Dict[str, list]) -> list:
    """
    Uses Spotify API via spotipy library to return a list of songs (name
    & id) which match the query.

    Note: the query_lookup parameter is not used. It is only included
    in the definition because query_lookup is passed to search_functions.
    """
    
    # Attributes to return
    attributes = ["name", "id"]

    # Search for tracks where the name matches query
    results = sp.search(q=f"track:\"{query}\"", type="track", limit=50)
    results = results["tracks"]["items"]
    results = [{ attr: item[attr] for attr in attributes } for item in results if remove_punctuation(clean_title(item["name"].casefold())) == remove_punctuation(query)]

    return results

def search_db(query: str, query_lookup: Dict[str, list]) -> list:
    """
    Searches tracks.db (1.2 million songs from Spotify from the Kaggle 
    database) to return a list of songs (name & id) which match the 
    query.

    https://www.kaggle.com/rodolfofigueroa/spotify-12m-songs 
    """
    # Import sqlite database
    tracks = sqlite3.connect("tracks.db")
    db = sqlite3.Cursor(tracks)

    # SQLite3 query 
    results = db.execute("SELECT name, id FROM tracks WHERE name_cleaned = ?", [remove_punctuation(query)]).fetchall()
    results = list(map(lambda item: {
        "name": item[0],
        "id": item[1],
    }, results))

    return results


"""
(2) String parses (to clean title name):
    - clean_title
    - remove_punctuation
"""

def clean_title(title):
    """
    Cleans title by performing the following transformations in order:
     - Remove substrings enclosed in (...) or [...] and preceding whitespace (using regex greedy matching)
     - Remove " - " and substring after 
     - Remove " feat(.)", " ft(.)", or " featuring" and substring after

    https://stackoverflow.com/questions/14596884/remove-text-between-and
    """
    # (Greedy) replace substrings between (...) and []
    title = re.sub(r"\s+\(.+\)", "", title)
    title = re.sub(r"\s+\[.+\]", "", title)

    # Remove " - " and subsequent substring
    title = re.sub(r" - .*", "", title)

    # Remove " feat(.) ", " ft(.) ", or " featuring " (but not "feature") and substring after
    title = re.sub(r"\W+((feat|ft)[:\.]?|featuring)\s.*", "", title)
    
    return title

def remove_punctuation(title):
    """
    Removes punctuation by performing the following transformations:
     - Delete XML escape sequences: &amp; &quot; &lt; &gt; &apos;
     - Replace "/", "//", etc. and surrounding whitespace with " " (in medley titles)
     - Replace "&" and surrounding whitespace with " and " 
     - Remove the following characters from the string: !"#$%'‘’“”()*+,-.:;<=>?@[\]^_—`{|}~
     - Strips surrounding whitespace
    """
    title = re.sub(r"&[amp|quot|lt|gt|apos];", "", title)
    title = re.sub(r"\s*\/+\s*", " ", title)
    title = re.sub(r"\s*&\s*", " and ", title)
    title = re.sub(r"[!\"#$%'‘’“”()*+,-.:;<=>?@[\\\]^_—`{|}~]", "", title)
    title = re.sub(r"\s{2,}", " ", title)
    return title.strip()


"""
Creates new Spotify playlist.
"""

def create_playlist(results):
    
    # Process items
    items = list(map(lambda songs: songs[0]["id"], results))

    # Create playlist
    playlist = sp.user_playlist_create(
        user=sp.me()["id"],
        name="Mixtape50",
        public=False,
        collaborative=False,
        description="Created with Mixtape50"
    )

    sp.playlist_add_items(playlist_id=playlist["id"], items=items)

    return