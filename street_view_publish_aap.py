from flask import Flask
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.streetview.publish_v1.gapic import street_view_publish_service_client as client
import google.oauth2.credentials
import os
import requests
from google.streetview.publish_v1.proto import resources_pb2
from googleapiclient.http import MediaIoBaseDownload
import time
import io


app = Flask(__name__)


@app.route('/publishimage')
def publish_image():
    from flask import request
    latitude = request.args.get('lat')
    longitude = request.args.get('long')
    folder_id = request.args.get('folderid')
    place_id = request.args.get('placeid')
    print(latitude)
    print(longitude)
    print(folder_id)
    print(place_id)
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/streetviewpublish','https://www.googleapis.com/auth/drive']
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('Credential file path',SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    drive_service = build('drive', 'v3', credentials=creds)
    page_token = None
    response = drive_service.files().list(q="'"+folder_id+"'"+" in parents",
                                          spaces='drive',
                                          fields='nextPageToken, files(id, name)',
                                          pageToken=page_token).execute()
    for file in response.get('files', []):
        request = drive_service.files().get_media(fileId=str(file.get('id')))
        fh = io.FileIO(str(file.get('name')), 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        credentials = google.oauth2.credentials.Credentials(creds.token)
        # Create a client and request an Upload URL.
        streetview_client = client.StreetViewPublishServiceClient(credentials=credentials)
        upload_ref = streetview_client.start_upload()
        print(upload_ref.upload_url)
        with open(str(file.get('name')), "rb") as f:
            print("Uploading file: " + f.name)
            raw_data = f.read()
            headers = {
                "Authorization": "Bearer " + creds.token,
                "Content-Type": "image/jpeg",
                "X-Goog-Upload-Protocol": "raw",
                "X-Goog-Upload-Content-Length": str(len(raw_data)),
            }
            r = requests.post(upload_ref.upload_url, data=raw_data, headers=headers)
            print("Upload response: " + str(r))

        capture_time = int(time.time())
        url_publishimage = 'https://streetviewpublish.googleapis.com/v1/photo?key=AIzaSyC2ul8LwHStS8KtmHCkk-jBTW__f2m9mIs'

        headers_publishimage = {
            "Authorization": "Bearer " + creds.token,
            "Content-Type": "application/json"
        }

        data_publishimage = {
            "uploadReference":
                {
                    "uploadUrl": upload_ref.upload_url
                },
            "pose":
                {
                    "heading": 105.0,
                    "latLngPair":
                        {
                            "latitude": latitude,
                            "longitude": longitude
                        }
                },
            "captureTime":
                {
                    "seconds": str(capture_time)
                },
            "places": [
                {
                    "name": "Westside",
                    "languageCode": "en",
                    "placeId": place_id
                }
            ]
        }
        res_publishimage = requests.post(url_publishimage, json=data_publishimage, headers=headers_publishimage)
        print(res_publishimage)
        os.remove(file.get('name'))
    return str(longitude)

if __name__ == '__main__':
    app.run()
