from __future__ import print_function
import httplib2
import os
import time
import datetime
import shutil
import zipfile
import subprocess

from apiclient import discovery
from apiclient.http import MediaFileUpload
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-backup.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Server Backup'


# The ID of the folder where the script will save your files
BACKUP_FOLDER_ID = 'YOUR_FOLDER_ID'

# All zips files created in the local tmp directory
# First argument : name of the zip file without the extension
# Second argument : path of the folder to zip
BACKUP_ZIPS = [
       ('letsencrypt', '/etc/letsencrypt')
   ]

# List of commands executed in a shell
BACKUP_COMMANDS = [
       ('echo test > test.test')
   ]

# All the files to backup
BACKUP_FILES = [
      ('tmp/letsencrypt.zip', ''),
      ('tmp/test.test', 'test/test')
   ]

FOLDER_IDS = {}

def commands():
    print("COMMANDS\n")
    for command in BACKUP_COMMANDS:
        print("Executing command " + command + " .... ", end="")
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        pout, perr = process.communicate()
        returnvalue = process.returncode
        print("DONE!")

def zipfiles(folder):
    print("\nZIPPING FILES\n")
    for f in BACKUP_ZIPS:
        name = f[0]
        path = f[1]
        print("Zip directory " + path + " in file " + name + " .... ", end="")
        zipf = zipfile.ZipFile(folder + "/" + name + ".zip", 'w', zipfile.ZIP_DEFLATED)
        zipdir(path, zipf)
        zipf.close()
        print("DONE!")


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def upload(service, f, folder_id):
    path = f[0]
    online_path = f[1]


    if len(online_path) > 0:
        folders = online_path.split("/")
        tmp_path = ""
        for folder in folders:
            tmp_path = tmp_path + folder + "/"
            if tmp_path in FOLDER_IDS:
                folder_id = FOLDER_IDS[tmp_path]
            else:
                folder_id = create_folder(service, folder, folder_id)
                FOLDER_IDS[tmp_path] = folder_id

    filename = os.path.basename(path)
    print("Upload file " + filename + " .... ", end='')

    media = MediaFileUpload(path, resumable=True)
    request = service.files().create(media_body=media, body={'name' : filename,
                                                             'parents' : [ folder_id ]})
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print("Uploaded %d%%." % int(status.progress() * 100))
        print("Upload complete!")


def create_folder(service, name, folder_id):
    file_metadata = {
      'name' : name,
      'mimeType' : 'application/vnd.google-apps.folder',
      'parents' : [ folder_id ]
    }
    file = service.files().create(body=file_metadata,
                                    fields='id').execute()
    return file.get('id')
	

def main():
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    commands()
    zipfiles("tmp")
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    ts = time.time()
    backup_folder_name = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    print("\nUPLOADING\n")
    print("Creating backup folder " + backup_folder_name)

    
    folder_id = create_folder(service, backup_folder_name, BACKUP_FOLDER_ID)

    for f in BACKUP_FILES:
        upload(service, f, folder_id)

    shutil.rmtree('tmp')

if __name__ == '__main__':
    main()

