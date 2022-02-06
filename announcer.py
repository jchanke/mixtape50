"""
Creates an 'announcer' object to send messages from the server
to the client. Implements the 'server-sent events' (SSE) paradigm.

Contains:

(1) MessageAnnouncer class definition (adapted from: https://maxhalford.github.io/blog/flask-sse-no-deps/)

(2) Helper functions
 - format_sse (formats data into the text/event-stream format, see: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#event_stream_format)
"""

from typing import Any, List, Dict, Union
import queue

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

def format_sse(event = None, data: str = "") -> str:
    """
    Formats data to the event-stream format.

    https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#event_stream_format
    """
    message = f"data: {data}\n\n"

    # If event is specified, prepend "event: {event}\n"
    if event is not None:
        message = f"event: {event}\n{message}"

    return message
