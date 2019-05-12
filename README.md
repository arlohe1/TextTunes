# Text Tunes - CIS192 Final Project

## Installation Instructions
This application can run locally on your device. Git clone this repository and pip install requirements.txt. Before running the application, you must create your own unique python file called "credentials.py", with a variable "CLIENT_ID" holding your unique client ID for Spotify, and another variable "CLIENT_SECRET" holding your secret key. This must be included in order to connect properly to Spotify. You can then cd into the main directory of this repository, and run the command "python server.py". The application should now be running on your localhost, port 5000.

## Application Instructions
Once running, the web application can be found by going to http://localhost:5000/ on your browser. Ensure that Spotify is open on your device(s) and your device(s) are connected to the Internet. Follow the prompts shown on the page. You can choose an existing playlist or an empty playlist. Once selected, your playlist will start playing, or, if the playlist is empty, once a song is added, song playback will commence.

### Using ngrok and Twilio to add songs via SMS
You can send POST requests to the '/sms' route of our application with a song search query, but our app is meant to be integrated with a true SMS component. This can be accomplished by using ngrok and Twilio. First, install ngrok and in the same directory that your ngrok file is saved to, and run the command './ngrok http 5000'. Now, copy the assigned forwarding address (it should be in the form of 'http://xxxxxx.ngrok.io/'). On Twilio, go to your assigned phone number's configurations, and under "Messaging," set the option "A MESSAGE COMES IN... WEBHOOK" to your forwarding address, with the route '/sms' following the address (ie., 'http://xxxxxx.ngrok.io/sms'). Now anyone should be able to text the Twilio number from any phone with a song query, and the returned song should be added to your chosen playlist.

## Routes
'/' - This route directs to the homepage.

'/go' - This route directs to the "Choose Device" page. If the user is not yet authorized on Spotify, they are prompted to login.

'/choosedevice' - The route to the page to choose a Spotify device.

'/chooseplaylist' - The route to the page to choose a Spotify playlist.

'/sms' - The route to send a POST request to with a song query.
