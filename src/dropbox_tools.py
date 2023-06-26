# To be run with nvcr.io/nvidia/pytorch:20.11-py3 docker image.
import dropbox
import logging
import requests

from requests.auth import HTTPBasicAuth

def download_file_from_dropbox(dbx: object, file_path: str, save_path: str):    
    try:
        # Download the file
        dbx.files_download_to_file(save_path, file_path)
        logging.info(f'File downloaded successfully to: {save_path}')
    except dropbox.exceptions.HttpError as e:
        logging.error(f'Error downloading the file: {e}')
        logging.info(f'Retrying download: {file_path}')
        download_file_from_dropbox(dbx, file_path, save_path)
    except Exception as e:
        logging.error(f'An error occurred: {e}')
        logging.info(f'Retrying download: {file_path}')
        download_file_from_dropbox(dbx, file_path, save_path)

def get_refresh_token(key: str, secret: str):
    auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(key, secret, token_access_type='offline', scope=['account_info.read', 'files.metadata.read', 'files.content.read'])
    authorize_url = auth_flow.start()
    print('Please authorize the app by visiting this URL:')
    print(authorize_url)
    authorization_code = input('Enter the authorization code: ')
    body = {'grant_type': 'authorization_code', 'code': authorization_code}
    response = requests.post('https://api.dropboxapi.com/oauth2/token', auth=HTTPBasicAuth(key, secret), data=body)
    return response.json()['refresh_token']

def authenticate():
    key = input('Please enter your dropbox app key: ')
    secret = input('Please enter your dropbox app secret: ')
    refresh_token = get_refresh_token(key, secret)
    dbx = dropbox.Dropbox(app_key=key, app_secret=secret, oauth2_refresh_token=refresh_token)
    return dbx