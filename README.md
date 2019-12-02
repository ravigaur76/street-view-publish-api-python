# street-view-publish-api-python
In this Article I will show how we can publish google drive 360 images to google street view using python flask.

Install below libraries one by one.

apt-get install python3-pip  
pip3 install flask  
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib  
pip3 install gapic-google-maps-streetview-publish-v1

You have to download credential file from your google cloud project.For more info visit below link - 
https://developers.google.com/adwords/api/docs/guides/authentication

Find place id using visit this link.
https://developers.google.com/places/place-id

Find latitude & longitude
https://support.google.com/maps/answer/18539?co=GENIE.Platform%3DDesktop&hl=en

Now Download file file street_view_publish_aap.py and enter your credential file path.

Run command - sudo python3 street_view_publish_aap.py

Replace parameter and hit URL in your browser - 
http://127.0.0.1:5000/publishimage?lat=lat&long=long&folderid=drivefolderid&placeid=placeid



