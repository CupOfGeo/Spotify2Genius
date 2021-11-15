# Spotify2Genius
Spotify playlist to Genius lyrics api

A small flask api deployed on google cloud run that when given a spotify playlist id (the end of the url) will seach the genius website for a matching song title \
if not found put in failed songs list \
if it has a letter diffrence of over 5 it is added to a warning list \
else added to a successful list \
the lyrics from the successful list are ziped and sent to a google cloud storage bucket \
returns a list of the songs title to the client 


Tested on the play list 1000 best songs of all time 
https://open.spotify.com/playlist/7hDSJxfgDFNImclVNOaaEl
Went through the 1003 songs in under 20 mins with 79% success rate
Warnings: 142/1003
Failed:68/1003
Success:793/1003

Ways of improvement:
 - Allow the users to pass the warnings if they deemed acceptable
 - if warning try again check with same song without a dash (ie - Remastered 1998, - Radio Edit) 
 - additionally, to the point above check by artist (may or may not be an improvement)
 - Allow users to manually enter a genius url of the lyrics
 - Allow user to upload their own lyrics (or any source material) to be included in the dataset


The main purpose of this will be to use it as a template for future dataset creation cloud functions. 
This is just for fun and proof of concept of letting a user just pick what data they want and generating a dataset.





