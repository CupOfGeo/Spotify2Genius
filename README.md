# Spotify2Genius
### Spotify playlist to Genius lyrics api

# What
A small flask api deployed on google cloud run that when given a spotify playlist id (the end of the url) will seach the genius website for a matching song. \
If not found put in failed songs list. \
If it has a letter difference of over a set threshold it is flagged and added to a warning list. \
Else added to a successful list. \
The lyrics from the successful list are zipped and sent to a google cloud storage bucket. \
Returns a list of the successful songs title to the client.

# Why
The files it creates and puts in the bucket will be used in a machine learning pipeline that will automatically train and deploy a model.
The main purpose of this lyric scrapper will be to use it as a template for future dataset creation cloud functions. 
This is a fun proof of concept of letting a user generating a dataset from a list. I Imagine instead of a spotify playlist it was list of accounts, hashtags, topics ect. from Twitter/Reddit/Blog Posts/...



# Current Stats
Tested on the play list 1000 best songs of all time 
https://open.spotify.com/playlist/7hDSJxfgDFNImclVNOaaEl
Went through the 1003 songs in under 20 mins with 79% success rate.\
Failed:68/1003 \
Warnings: 142/1003 (with a threshold of 5) \
Success:793/1003 \


# Issues

Ways of improvement:
 - Allow the users to pass the warnings if they deemed acceptable
 - if warning try again check with same song without a dash (ie - Remastered 1998, - Radio Edit)
 - Allow users to manually enter a genius url of the lyrics
 - Allow user to upload their own lyrics (or any source material) to be included in the dataset
 - Improve data cleaning

More critical issues:
 - At the moment when it fails it just prints Error need more informative message and redundancy to at least alert 
   something that it failed.
 - 





