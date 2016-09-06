# backupscript-server
Backup script to Google Drive for linux servers. Can zip, upload files and execute commands

For complete documentation, please visit : [https://gitcommit.fr/backup-script-for-google-drive/](https://gitcommit.fr/backup-script-for-google-drive/)

# Configuration

When the script starts, a tmp folder is created and can be used to save all sorts of file. It is the default path for zip file. At the end of the script, this folder is deleted.

## Backup folder

The backup script will upload all your files in a specific Google Drive repository. You have to put the id of that repository where the backup will take place.

```language-python
BACKUP_FOLDER_ID = 'YOUR_FOLDER_ID'
```
The name of the backup folder is a simple timestamp.

## Zips

You can zip entire folders. The BACKUP_ZIPS variable is an array of tuple, the first argument being the name of the zip and the second argument the path of the folder to zip.

```language-python
BACKUP_ZIPS = [
        ('letsencrypt', '/etc/letsencrypt')
]
```

Here, the script will zip the entire folder `/etc/letsencrypt` and save it to `pathofyourscript/tmp/letsencrypt.zip`.


## Commands

You can execute all sorts of command like saving your database in a file. The BACKUP_COMMANDS variable is an array of string containing the command to run in a shell. Here the command will create a file `test.test` in the tmp folder containing the string "test".


```language-python
BACKUP_COMMANDS = [
        ('echo test > tmp/test.test')
]
```

## Backup files

You can save all sorts of files. The BACKUP_FILES variable is an array of tuple. The first argument being the path of the file and the second the Google Drive directory to create and to save to.

```language-python
BACKUP_FILES = [
        ('tmp/letsencrypt.zip', ''),
        ('tmp/test.test', 'test/test')
]
```
