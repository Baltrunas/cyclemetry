import argparse

from utils import get_file_list


def main(action, directory):
    match action:
        case 'all':
            ...
            print("Doing all")
        case 'rename_media':
            print("Rename media file")
        case 'split_gpx':
            print("Split gpx file")
        case 'overlay':
            print("Create overlay")
        case 'demo':
            print("Create demo")
        case _:
            raise ValueError("Invalid action")

    print("Dir:", directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GoPro Overlay')
    parser.add_argument('action', help='Action', choices=['greet', 'bye'])
    parser.add_argument('--dir', help='Directory')
    parser.add_argument('--exclude', help='Exclude files')

    args = parser.parse_args()
    action = args.action
    directory = args.dir

    ls = get_file_list(".gpx", exclude=[])

    main(action, directory)
