#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import random
from argparse import ArgumentParser
from datetime import date, datetime, timedelta
from glob import glob
from subprocess import CalledProcessError, check_output

import yaml

stdin_parser = ArgumentParser(description='python and ffmpeg based playout')

stdin_parser.add_argument(
    '-c', '--config', help='file path to ffplayout.yml'
)

stdin_parser.add_argument(
    '-d', '--date', help='playlist date (yyyy-mm-dd)', nargs='+'
)

stdin_parser.add_argument(
    '-t', '--length',
    help='set length in "hh:mm:ss", default 24:00:00'
)

stdin_parser.add_argument(
    '-i', '--input', help='input folder'
)

stdin_parser.add_argument(
    '-o', '--output', help='output folder'
)

ARGS = stdin_parser.parse_args()


def read_config(path):
    with open(path, 'r') as config_file:
        return yaml.safe_load(config_file)


if ARGS.config and os.path.isfile(ARGS.config):
    CFG = read_config(ARGS.config)
elif os.path.isfile('/etc/ffplayout/ffplayout.yml'):
    CFG = read_config('/etc/ffplayout/ffplayout.yml')
else:
    print('No config file found!\nNo playlist generation is possible...')
    exit()


class MediaProbe(object):
    """
    get infos about media file, similare to mediainfo
    """

    def __init__(self):
        self.format = None
        self.audio = []
        self.video = []

    def load(self, file):
        cmd = ['ffprobe', '-v', 'quiet', '-print_format',
               'json', '-show_format', '-show_streams', file]

        try:
            info = json.loads(check_output(cmd).decode('UTF-8'))
        except CalledProcessError as err:
            print(f'MediaProbe error in: "{file}"\n{err}')
            self.audio.append(None)
            self.video.append(None)

            return

        self.format = info['format']

        for stream in info['streams']:
            if stream['codec_type'] == 'audio':
                self.audio.append(stream)

            if stream['codec_type'] == 'video':
                self.video.append(stream)


def daterange():
    if not ARGS.date:
        return [date.today().strftime('%Y-%m-%d')]
    elif '-' in ARGS.date and len(ARGS.date) == 3:
        start = ARGS.date[0]
        end = ARGS.date[2]
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()

        date_list = []
        for n in range(int((end_date - start_date).days) + 1):
            date_list.append((start_date + timedelta(n)).strftime('%Y-%m-%d'))

    else:
        date_list = ARGS.date

    return date_list


def write_json(data):
    if ARGS.output:
        out_path = ARGS.output
    else:
        out_path = CFG['playlist']['path']

    y, m, d = data['date'].split('-')
    _path = os.path.join(out_path, y, m)

    if not os.path.isdir(_path):
        os.makedirs(_path, exist_ok=True)

    output = os.path.join(_path, f'{data.get("date")}.json')

    if os.path.isfile(output):
        print(f'Playlist {output} already exists')
        return

    with open(output, "w") as outfile:
        print(f'create playlist for: {data["date"]}')
        json.dump(data, outfile, indent=4)


def main():
    source = ARGS.input if ARGS.input else CFG['storage']['path']
    ext = CFG['storage']['extensions']
    probe = MediaProbe()

    for _date in daterange():
        counter = 0
        loop = True
        data = {
            'channel': 'Channel 1',
            'date': _date,
            'length': ARGS.length if ARGS.length else '24:00:00',
            'program': []
        }

        store = glob(os.path.join(source, '**', f'*{ext}'), recursive=True)

        while loop:
            random.shuffle(store)

            for clip in store:
                probe.load(clip)

                try:
                    duration = float(probe.format.get('duration'))
                except (ValueError, TypeError):
                    continue

                node = {
                    'in': 0,
                    'out': duration,
                    'duration': duration,
                    'category': '',
                    'source': clip
                }

                data['program'].append(node)

                counter += duration

                if (ARGS.length and counter >= ARGS.length) \
                        or counter >= 86400:
                    loop = False
                    break

        write_json(data)


if __name__ == '__main__':
    main()
