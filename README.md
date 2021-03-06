# mixtape50

Creates a Spotify playlist that spells out a message. View the about page [here](https://jchanke.github.io/mixtape50).

- [1. Installation (beginner-friendly!)](#1-installation-beginner-friendly)
    - [1.1. Clone the repository](#11-clone-the-repository)
    - [1.2. Create a virtual environment](#12-create-a-virtual-environment)
    - [1.3. Install dependencies](#13-install-dependencies)
    - [1.4. Get the API keys from Spotify](#14-get-the-api-keys-from-spotify)
    - [1.5. Authorise mixtape50](#15-authorise-mixtape50)
- [2. Run the app](#2-run-the-app)

## 1. Installation (beginner-friendly!)

Ensure you have Python 3 installed on your machine.

### 1.1. Clone the repository

For example, to clone this project to a new folder (which you might name `mixtape50`):

```bash
~ $ mkdir mixtape50
~ $ cd mixtape50
~/mixtape50 $ git clone https://github.com/jchanke/mixtape50.git
```

This creates a local copy of the files on your computer.

### 1.2 Create a virtual environment

Once in your folder, run this command to create a 'virtual environment'. (That way whatever python libraries you install won't interfere with your existing python setup. Pretty neat, huh?)

```bash
~/mixtape50 $ python -m venv venv
```

This creates a virtual environment called `venv` inside the `mixtape50` folder:

```bash
(venv) ~/mixtape50 $
```

### 1.3. Install dependencies

mixtape50 is built mainly with two python libraries.

* [spotipy](https://spotipy.readthedocs.io/en/2.19.0/) is an interface for the [Spotify Web API](https://developer.spotify.com/documentation/web-api/), which allows mixtape50 to create playlists in your account.
* [flask](https://flask.palletsprojects.com/en/2.0.x/) is a library that the application itself is built with. It organises the information on the site, so when you enter the right address, you are taken to the right page. (And a bit more.)

Since the python virtual environment has the `pip` module pre-installed, you can install everythng with one command by reading the `requirements.txt` text file (make sure you are in your virtual environment first!):

```
(venv) ~/mixtape50 $ pip install -r requirements.txt
```

### 1.4. Get the API keys from Spotify

Sign in at the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) with your Spotify account.

* Click **Create An App**
* Fill in a **App name** and **App description** (e.g. `Mixtape50` & `Creates a playlist with song titles matching a user's input.` It doesn't matter what you choose.)
* Click on your new app > **Edit settings**, and add `http://127.0.0.1:5000/callback` to the **Redirect URIs**.

One last thing! From the dashboard, get the **Client ID** and **Client Secret** (both hexadecimal numbers) and enter this into your terminal (replacing `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` with your own values, of course):

```bash
(venv) ~/mixtape50 $ export SPOTIPY_CLIENT_ID=d234a39...
(venv) ~/mixtape50 $ export SPOTIPY_CLIENT_SECRET=68cdff4...
(venv) ~/mixtape50 $ export FLASK_ENV=development
```

Now you're all set up!

### 1.5. Authorise mixtape50

In the terminal, start the `helpers.py` module (in interactive `-i` mode) and call the `search_spotipy` method:

```bash
(venv) ~/mixtape50 $ python -i helpers.py
```
```python
>>> search_spotipy("track: hello world!", type="track", limit=50)
```

A page should open, allowing you to sign into your Spotify account.

## 2. Run the app

In your terminal window, run:

```bash
(venv) ~mixtape50 $ flask run
```

If successful, you should see text like this:

```
* Environment: development
* Debug mode: on
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: 123-456-789
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) to view the app!
