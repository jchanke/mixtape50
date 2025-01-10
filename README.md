# mixtape50

Creates a Spotify playlist that spells out a message.

## Installation

The easiest way to run this locally is via Docker:
```bash
docker pull josephchanke/mixtape50:latest
docker run -d \
  -p 5000:5000 \
  --name mixtape50 \
  -e FLASK_SECRET=your_secure_secret_key \
  josephchanke/mixtape50:latest
```
If you want to deploy this, remember to set `FLASK_SECRET` to something really secret. See the [Flask documentation](https://flask.palletsprojects.com/en/stable/tutorial/deploy/#configure-the-secret-key) for how to generate one.

The application should now be running on [http://localhost:5000](http://localhost:5000).

## Usage
After starting the application, enter your message -- and the application will generate a Spotify playlist that spells out the message!

Hope you have fun! 🎵

## To-dos
- [] Make the 'X' button on the modal close the modal
- [] Prevent the user from submitting a message if they aren't authenticated (check for `access_token` in `app.js`)
- [] Give the user an option to go back to create another mixtape, without re-loading the page
