# Spotify API accessed via Spotipy library https://spotipy.readthedocs.io/en/2.19.0/

from crypt import methods
import os
import re
import sqlite3
import requests
import json

from flask import Flask, flash, redirect, render_template, request, session, url_for
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from markupsafe import escape

from helpers import search_message

# Configure app
app = Flask(__name__)

@app.route("/", methods = ["GET"])
def index():

       return 



