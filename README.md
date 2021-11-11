# Spotify2Genius
Spotify playlist to Genius lyrics api
A small flask api deployed on google cloud run that when given a spotify playlist id (the end of the url) will seach the genius website for a matching song title
if not found put in failed songs list 
if it has a letter diffrence of over 5 it is added to a warning list
else added to a successful list 
the lyrics from the successful list are ziped and sent to a google cloud storage bucket
returns a list of the songs title to the client 
