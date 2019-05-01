# Dropbox Backup

This is a python script that uploads entire folder to a folder in Dropbox.

You will need a Dropbox token for your account to use this program.
Check the instruction linked below to get your own.

https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/

## Usage

1. Clone this repository.
2. Rename `settings.yml.sample` to `settings.yml` and edit it.
3. Install requirements with `pip install -r requirements.txt`

Run `run.py`. Re-run it if the script failed by error.
The script will automatically skip already uploaded files.
