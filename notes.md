
```
/usr/bin/ffmpeg -i /var/www/peertube/storage/videos/private/4dbc0b1c-5633-4e6e-b117-a375502676fe-720.mkv -y -acodec aac -vcodec libx264 -threads 2 -f mp4 -movflags faststart -max_muxing_queue_size 1024 -map_metadata -1 -pix_fmt yuv420p -channel_layout stereo -b:a 256k -vf scale=w=-2:h=720 -preset veryfast -maxrate:v 2607221.5 -bufsize:v 5214443 -b_strategy 1 -bf 16 -r 30 -level:v 3.1 -g:v 60 /var/www/peertube/storage/tmp/1-transcoded.mp4"
/usr/bin/ffmpeg -i /var/www/peertube/storage/videos/9122a13a-5aab-4fb7-8a49-fd4faa356e58-720.mp4 -y -acodec copy -vcodec copy -threads 2 -f mp4 -hls_time 4 -hls_list_size 0 -hls_playlist_type vod -hls_segment_filename /var/www/peertube/storage/tmp/hls/72306507-35c9-4d6c-819b-74f92d20a556-720-fragmented.mp4 -hls_segment_type fmp4 -f hls -hls_flags single_file /var/www/peertube/storage/tmp/hls/72306507-35c9-4d6c-819b-74f92d20a556-720.m3u8"
/usr/bin/ffmpeg -i /var/www/peertube/storage/streaming-playlists/hls/a9d62451-d028-48df-aaee-d47e81aee720/72306507-35c9-4d6c-819b-74f92d20a556-720-fragmented.mp4 -y -acodec copy -vcodec libx264 -threads 2 -f mp4 -movflags faststart -max_muxing_queue_size 1024 -map_metadata -1 -pix_fmt yuv420p -vf scale=w=-2:h=480 -preset veryfast -maxrate:v 1474560 -bufsize:v 2949120 -b_strategy 1 -bf 16 -r 30 -level:v 3.1 -g:v 60 -hls_time 4 -hls_list_size 0 -hls_playlist_type vod -hls_segment_filename /var/www/peertube/storage/tmp/hls/3dbffa88-2290-419c-b54e-20a0e80921b4-480-fragmented.mp4 -hls_segment_type fmp4 -f hls -hls_flags single_file /var/www/peertube/storage/tmp/hls/3dbffa88-2290-419c-b54e-20a0e80921b4-480.m3u8"
/usr/bin/ffmpeg -i /var/www/peertube/storage/streaming-playlists/hls/a9d62451-d028-48df-aaee-d47e81aee720/72306507-35c9-4d6c-819b-74f92d20a556-720-fragmented.mp4 -y -acodec copy -vcodec libx264 -threads 2 -f mp4 -movflags faststart -max_muxing_queue_size 1024 -map_metadata -1 -pix_fmt yuv420p -vf scale=w=-2:h=360 -preset veryfast -maxrate:v 1036800 -bufsize:v 2073600 -b_strategy 1 -bf 16 -r 30 -level:v 3.1 -g:v 60 -hls_time 4 -hls_list_size 0 -hls_playlist_type vod -hls_segment_filename /var/www/peertube/storage/tmp/hls/24e73fd4-3cba-473f-b853-af5a89c56302-360-fragmented.mp4 -hls_segment_type fmp4 -f hls -hls_flags single_file /var/www/peertube/storage/tmp/hls/24e73fd4-3cba-473f-b853-af5a89c56302-360.m3u8"
/usr/bin/ffmpeg -i /var/www/peertube/storage/streaming-playlists/hls/a9d62451-d028-48df-aaee-d47e81aee720/72306507-35c9-4d6c-819b-74f92d20a556-720-fragmented.mp4 -y -acodec copy -vcodec libx264 -threads 2 -f mp4 -movflags faststart -max_muxing_queue_size 1024 -map_metadata -1 -pix_fmt yuv420p -vf scale=w=-2:h=240 -preset veryfast -maxrate:v 522240 -bufsize:v 1044480 -b_strategy 1 -bf 16 -r 30 -level:v 3.1 -g:v 60 -hls_time 4 -hls_list_size 0 -hls_playlist_type vod -hls_segment_filename /var/www/peertube/storage/tmp/hls/9cd158c0-b5dd-47ca-8673-a16414310e1c-240-fragmented.mp4 -hls_segment_type fmp4 -f hls -hls_flags single_file /var/www/peertube/storage/tmp/hls/9cd158c0-b5dd-47ca-8673-a16414310e1c-240.m3u8"
/usr/bin/ffmpeg -i /var/www/peertube/storage/streaming-playlists/hls/a9d62451-d028-48df-aaee-d47e81aee720/72306507-35c9-4d6c-819b-74f92d20a556-720-fragmented.mp4 -y -acodec copy -vcodec libx264 -threads 2 -f mp4 -movflags faststart -max_muxing_queue_size 1024 -map_metadata -1 -pix_fmt yuv420p -vf scale=w=-2:h=144 -preset veryfast -maxrate:v 210124 -bufsize:v 420248 -b_strategy 1 -bf 16 -r 30 -level:v 3.1 -g:v 60 -hls_time 4 -hls_list_size 0 -hls_playlist_type vod -hls_segment_filename /var/www/peertube/storage/tmp/hls/12b09b39-c790-4906-ad25-14ca61457f16-144-fragmented.mp4 -hls_segment_type fmp4 -f hls -hls_flags single_file /var/www/peertube/storage/tmp/hls/12b09b39-c790-4906-ad25-14ca61457f16-144.m3u8"
```

```python
transcode = ['-i', '/var/www/peertube/storage/videos/private/4dbc0b1c-5633-4e6e-b117-a375502676fe-720.mkv', '-y',
             '-acodec',
             'aac', '-vcodec', 'libx264', '-threads', '2', '-f', 'mp4', '-movflags', 'faststart',
             '-max_muxing_queue_size',
             '1024', '-map_metadata', '-1', '-pix_fmt', 'yuv420p', '-channel_layout', 'stereo', '-b:a', '256k',
             '-vf',
             'scale=w=-2:h=720', '-preset', 'veryfast', '-maxrate:v', '2607221.5', '-bufsize:v', '5214443',
             '-b_strategy', '1',
             '-bf', '16', '-r', '30', '-level:v', '3.1', '-g:v', '60',
             '/var/www/peertube/storage/tmp/1-transcoded.mp4']
hsl_orig = ['-i', '/var/www/peertube/storage/videos/9122a13a-5aab-4fb7-8a49-fd4faa356e58-720.mp4', '-y', '-acodec',
            'copy',
            '-vcodec', 'copy', '-threads', '2', '-f', 'mp4', '-hls_time', '4', '-hls_list_size', '0',
            '-hls_playlist_type',
            'vod', '-hls_segment_filename',
            '/var/www/peertube/storage/tmp/hls/72306507-35c9-4d6c-819b-74f92d20a556-720-fragmented.mp4',
            '-hls_segment_type',
            'fmp4', '-f', 'hls', '-hls_flags', 'single_file',
            '/var/www/peertube/storage/tmp/hls/72306507-35c9-4d6c-819b-74f92d20a556-720.m3u8']

hsl_480 = [
    '-i',
    '/var/www/peertube/storage/streaming-playlists/hls/a9d62451-d028-48df-aaee-d47e81aee720/72306507-35c9-4d6c-819b-74f92d20a556-720-fragmented.mp4',
    '-y', '-acodec', 'copy', '-vcodec', 'libx264', '-threads', '2', '-f', 'mp4', '-movflags', 'faststart',
    '-max_muxing_queue_size', '1024', '-map_metadata', '-1', '-pix_fmt', 'yuv420p', '-vf',
    'scale=w=-2:h=480',
    '-preset', 'veryfast', '-maxrate:v', '1474560', '-bufsize:v', '2949120', '-b_strategy', '1', '-bf', '16',
    '-r', '30',
    '-level:v', '3.1', '-g:v', '60', '-hls_time', '4', '-hls_list_size', '0',
    '-hls_playlist_type', 'vod',
    '-hls_segment_filename',
    '/var/www/peertube/storage/tmp/hls/3dbffa88-2290-419c-b54e-20a0e80921b4-480-fragmented.mp4',
    '-hls_segment_type', 'fmp4',
    '-f', 'hls', '-hls_flags', 'single_file',
    '/var/www/peertube/storage/tmp/hls/3dbffa88-2290-419c-b54e-20a0e80921b4-480.m3u8']

hsl_360 = ['-i',
           '/var/www/peertube/storage/streaming-playlists/hls/a9d62451-d028-48df-aaee-d47e81aee720/72306507-35c9-4d6c-819b-74f92d20a556-720-fragmented.mp4',
           '-y', '-acodec', 'copy', '-vcodec', 'libx264', '-threads', '2', '-f', 'mp4', '-movflags', 'faststart',
           '-max_muxing_queue_size', '1024', '-map_metadata', '-1', '-pix_fmt', 'yuv420p', '-vf',
           'scale=w=-2:h=360',
           '-preset', 'veryfast', '-maxrate:v', '1036800', '-bufsize:v', '2073600', '-b_strategy', '1', '-bf', '16',
           '-r',
           '30', '-level:v', '3.1', '-g:v', '60', '-hls_time', '4', '-hls_list_size', '0', '-hls_playlist_type',
           'vod',
           '-hls_segment_filename',
           '/var/www/peertube/storage/tmp/hls/24e73fd4-3cba-473f-b853-af5a89c56302-360-fragmented.mp4',
           '-hls_segment_type',
           'fmp4', '-f', 'hls', '-hls_flags', 'single_file',
           '/var/www/peertube/storage/tmp/hls/24e73fd4-3cba-473f-b853-af5a89c56302-360.m3u8']

hsl_240 = ['-i',
           '/var/www/peertube/storage/streaming-playlists/hls/a9d62451-d028-48df-aaee-d47e81aee720/72306507-35c9-4d6c-819b-74f92d20a556-720-fragmented.mp4',
           '-y', '-acodec', 'copy', '-vcodec', 'libx264', '-threads', '2', '-f', 'mp4', '-movflags', 'faststart',
           '-max_muxing_queue_size', '1024', '-map_metadata', '-1', '-pix_fmt', 'yuv420p', '-vf',
           'scale=w=-2:h=240',
           '-preset', 'veryfast', '-maxrate:v', '522240', '-bufsize:v', '1044480', '-b_strategy', '1', '-bf', '16',
           '-r',
           '30', '-level:v', '3.1', '-g:v', '60', '-hls_time', '4', '-hls_list_size', '0', '-hls_playlist_type',
           'vod',
           '-hls_segment_filename',
           '/var/www/peertube/storage/tmp/hls/9cd158c0-b5dd-47ca-8673-a16414310e1c-240-fragmented.mp4',
           '-hls_segment_type',
           'fmp4', '-f', 'hls', '-hls_flags', 'single_file',
           '/var/www/peertube/storage/tmp/hls/9cd158c0-b5dd-47ca-8673-a16414310e1c-240.m3u8']

hsl_144 = ['-i',
           '/var/www/peertube/storage/streaming-playlists/hls/a9d62451-d028-48df-aaee-d47e81aee720/72306507-35c9-4d6c-819b-74f92d20a556-720-fragmented.mp4',
           '-y', '-acodec', 'copy', '-vcodec', 'libx264', '-threads', '2', '-f', 'mp4', '-movflags', 'faststart',
           '-max_muxing_queue_size', '1024', '-map_metadata', '-1', '-pix_fmt', 'yuv420p', '-vf',
           'scale=w=-2:h=144',
           '-preset', 'veryfast', '-maxrate:v', '210124', '-bufsize:v', '420248', '-b_strategy', '1', '-bf', '16',
           '-r', '30',
           '-level:v', '3.1', '-g:v', '60', '-hls_time', '4', '-hls_list_size', '0', '-hls_playlist_type', 'vod',
           '-hls_segment_filename',
           '/var/www/peertube/storage/tmp/hls/12b09b39-c790-4906-ad25-14ca61457f16-144-fragmented.mp4',
           '-hls_segment_type',
           'fmp4', '-f', 'hls', '-hls_flags', 'single_file',
           '/var/www/peertube/storage/tmp/hls/12b09b39-c790-4906-ad25-14ca61457f16-144.m3u8']
```
