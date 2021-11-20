# Spotify2Genius
### Spotify playlist to Genius lyrics api
#### Now with threads.

# What
A small flask api deployed on google cloud run that when given a spotify playlist id (the end of the url) will search the genius website for a matching song. \
If not found (genius api returned None) put in failed songs list. \
If it has a letter difference of over a set threshold it is flagged and added to a warning list. \
Else added to a successful list. \
The lyrics from the successful list are zipped and sent to a Google cloud storage bucket.




# Why
The files it creates and puts in the bucket will be used in a machine learning pipeline that will automatically train and deploy a model.
The main purpose of this lyric scrapper will be to use it as a template for future dataset creation cloud functions. 
This is a fun proof of concept of letting a user generating a dataset from a list. I Imagine instead of a spotify playlist it was list of accounts, hashtags, topics ect. from Twitter/Reddit/Blog Posts/...

# How
My client sends makes a post request to the entry endpoint specifying at a minimum a user, playlist_id, and project_name but can also set the debug, threshold, and num_threads.
This will start a thread that will process the request and send back a json of the jobs information and status. \
{user, playlist_id, project_name, num_threads, threshold, debug, job_id, status, start_time, end_time, thread, data} \
Now my client will just poll the endpoint with the job_id to see the status and when it finished collect the result \

####The job
Now the api will find the spotify playlist with the spotify api and get all the songs in that playlist. Then it will cut up that playlist into 
the number of threads set (default 4)  piece and will give each piece to a thread. Each thread will try to match the spotify song title and artist to a genius song with the genius api.
It will follow the rules above for determining if a song will be put in the threads local found, warning, or failed list. 
After the threads are done each threads local list will be merged into one master found, failed, warnings list.



 




# Current Stats
Tested on the play list 1000 best songs of all time 
https://open.spotify.com/playlist/7hDSJxfgDFNImclVNOaaEl
with a threshold = 5 and num_threads = 4 
Warnings: 142/1003 \
Failed:68/1003 \
Success:793/1003 \
--- 257.4001393318176 seconds --- \
Went through the 1003 songs in 4 minutes 17 sec  with 79% success rate.\

# Issues

Ways of improvement:
 - Allow the users to pass the warnings if they deemed acceptable
 - if warning try again check with same song without a dash (ie - Remastered 1998, - Radio Edit)
 - Allow users to manually enter a genius url of the lyrics
 - Allow user to upload their own lyrics (or any source material) to be included in the dataset
 - Improve data cleaning





