import os

import conf
from utils import get_file_list, get_creation_time, get_created_at


mp4_files = get_file_list(".mp4")
for mp4_file_name in mp4_files:
    file_path = os.path.join(conf.SOURCE_DIR, f"{mp4_file_name}.mp4")
    creation_time = get_creation_time(file_path)
    created_at = get_created_at(file_path)

    match conf.RENAME_ACTION:
        case conf.RenameActions.INFO:
            print("file_path:", file_path)
            print("creation_time:", creation_time)
            print("created_at:", created_at)
            print(creation_time == created_at)
            print()
        case conf.RenameActions.RENAME_BY_META:
            new_file_path = os.path.join(conf.SOURCE_DIR, creation_time + ".mp4")
            os.rename(file_path, new_file_path)
        case conf.RenameActions.RENAME_BY_FS:
            new_file_path = os.path.join(conf.SOURCE_DIR, created_at + ".mp4")
            os.rename(file_path, new_file_path)
