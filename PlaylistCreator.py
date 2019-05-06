# Created by Ada
# quick script to make vlc playlists out of album folders
# Requires mutagen module to get track data: https://mutagen.readthedocs.io/en/latest/index.html

import os
from mutagen.flac import FLAC
import urllib.parse

data_tags = ["location", "title", "creator", "album", "trackNum", "annotation", "duration"]
application = 'application="http://www.videolan.org/vlc/playlist/0"'

# Pass in string with track/file name. Returns dictionary with track info
def get_track_data(track_name):
    # Gets Artist, Album,
    raw_data = FLAC(track_name)
    # Fix different names of data between VLC and mutagen.
    # Removed old key, and adds it back as the new key
    raw_data['annotation'] = raw_data.pop('comment')
    raw_data['creator'] = raw_data.pop('artist')
    raw_data['trackNum'] = raw_data.pop('tracknumber')

    # Add 'duration', which is an integer of seconds|| three digits of miliseconds
    # Returns as list to keep consistency with rest of data
    raw_data['duration'] = [str(int((raw_data.info.length) * 1000))]

    # urllib.parse replaces unsafe ASCII characters with URL encoding. e.g. " " -> "%20"
    location = str(os.getcwd().replace('\\','/')) + '/' + track_name
    location = urllib.parse.quote(location).replace('%3A',':')
    raw_data['location'] =  ('file:///' + location)
    return raw_data

def format_tag(tag, information):
    return f'<{tag}>{information}</{tag}>\n'

# n should be the number of the track, indexed by '0'
def format_track(n, track_name):
    track_data = get_track_data(track_name)
    track = ''
    for tag in data_tags:
        track += '\t' + format_tag(tag, track_data[tag][0])
    track += f'\t<extension application="http://www.videolan.org/vlc/playlist/0">\n\t\t<vlc:id>{n}</vlc:id>\n\t</extension>\n'
    track = format_tag('track', track)
    return track + '\n'

file_header = """<?xml version="1.0" encoding="UTF-8"?>
<playlist xmlns="http://xspf.org/ns/0/" xmlns:vlc="http://www.videolan.org/vlc/playlist/ns/0/" version="1">
    <title>Playlist</title>\n"""

def main():
    # ignore album cover pictures and other random stuff.
    tracklist = [x for x in os.listdir() if (x.split('.')[-1] =='flac')]
    playlist = ''
    for n, track in enumerate(tracklist):
        playlist += format_track(n, track) + '\n'

    playlist = format_tag('trackList', playlist)
    footer = ''.join( [f'<vlc:item tid="{i}"/>' for i in range(len(tracklist))] )
    footer = f'<extension {application}>{footer}\n</extension>'
    playlist = file_header + playlist + footer + '</playlist>\n'
    with open('album.xspf','w') as f:
        print(playlist, file=f)

main()
