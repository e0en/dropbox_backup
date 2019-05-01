#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
import time
import os

import yaml
import dropbox


PWD = Path(__file__).parents[0].resolve()

with open(PWD / 'settings.yml') as fp:
    SETTING = yaml.load(fp.read())

SRC_FOLDER = SETTING['src_folder']
DST_FOLDER = SETTING['dst_folder']
LOG_FILE = PWD / SETTING['log_file']
DROPBOX_TOKEN = SETTING['dropbox_token']


def write_log(msg):
    with open(LOG_FILE, 'a') as fp:
        ts = time.time()
        fp.write(f'{ts}\t{msg}\n')


def upload_file(dbx, filepath: str):
    canonical_path = filepath[len(SRC_FOLDER):]
    dst_path = DST_FOLDER + canonical_path

    chunk_size = 10 << 20

    # open the file and upload it
    with open(filename, 'rb') as f:
        print(f'uploading {filename}')
        file_size = os.stat(filename).st_size

        if file_size < chunk_size:
            meta = dbx.files_upload(f.read(), dst_path,
                                    mode=dropbox.files.WriteMode("overwrite"))
            return

        offset = 0
        cursor = None
        is_start = True
        while True:
            chunk = f.read(chunk_size)
            offset += len(chunk)
            if is_start:
                res = dbx.files_upload_session_start(chunk)
                is_start = False
            elif len(chunk) == chunk_size:
                dbx.files_upload_session_append_v2(chunk, cursor)
            elif len(chunk) < chunk_size:
                commit_info = dropbox.files.CommitInfo(
                    path=dst_path, mode=dropbox.files.WriteMode('overwrite'))
                meta = dbx.files_upload_session_finish(chunk, cursor,
                                                       commit_info)
                return
                break
            elif not chunk:
                break
            cursor = dropbox.files.UploadSessionCursor(res.session_id,
                                                       offset=offset)
            print(f'...{offset >> 20} / {file_size >> 20}')


if __name__ == '__main__':
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    with open(PWD / 'used_files.txt', 'r') as fp:
        used_files = fp.read().strip().split('\n')

    with open(PWD / 'failed_files.txt', 'r') as fp:
        failed_files = fp.read().strip().split('\n')
        failed_files = {x.split('\t')[0] for x in failed_files}

    used_files = set(used_files)

    p = Path(SRC_FOLDER).glob('**/*')
    for f in p:
        if f.is_dir():
            continue

        filename = str(f)

        if filename.endswith('.DS_Store'):
            continue
        if filename in used_files:
            continue

        print(filename[len(SRC_FOLDER):])

        try:
            write_log(f'uploading {filename}')
            upload_file(dbx, filename)
            with open(PWD / 'used_files.txt', 'a') as fp:
                fp.write(filename + '\n')
            used_files.add(filename)
        except dropbox.exceptions.HttpError as e:
            write_log(f'failed to upload {filename}: e')
        except dropbox.exceptions.ApiError as e:
            with open(PWD / 'failed_files.txt', 'a') as fp:
                fp.write(f'{filename}\t{e}\n')
        except PermissionError as e:
            write_log(f'failed to upload {filename}: e')
            with open(PWD / 'failed_files.txt', 'a') as fp:
                fp.write(f'{filename}\t{e}\n')
        except Exception as e:
            write_log(f'failed to upload {filename}: e')
            with open(PWD / 'failed_files.txt', 'a') as fp:
                fp.write(f'{filename}\t{e}\n')
