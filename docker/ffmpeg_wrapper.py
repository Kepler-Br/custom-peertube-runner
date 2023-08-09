#!/bin/python3
import os
import subprocess
import sys
from enum import Enum
from typing import List, Optional

ffmpeg_bin_path = '/usr/bin/ffmpeg'
# good is the default and recommended for most applications.
# best is recommended if you have lots of time and want the best compression efficiency.
# realtime is recommended for live / fast encoding.
ffmpeg_deadline = 'good'
ffmpeg_crf = '31'
print_argv = False
if print_argv:
    log_file = open('/home/node/ffmpeg_wrapper_logs/logs.log', 'a')
else:
    log_file = sys.stderr


class ArgparseError(Exception):
    pass


class SimpleArgParser:
    def __init__(self):
        self._flags = set()
        self._args = set()

    def add_argument(self, name: str, is_flag: bool = False) -> 'SimpleArgParser':
        if is_flag:
            if name in self._flags:
                raise ArgparseError(f'Flag with name {name} already exists')
            self._flags.add(name)
        else:
            if name in self._args:
                raise ArgparseError(f'Arg with name {name} already exists')
            self._args.add(name)

        return self

    def parse(self, args: List[str]) -> List[List[str]]:
        parsed: List[List[str]] = []

        i = 0
        while i < len(args):
            arg = args[i]
            if arg in self._flags:
                parsed.append([arg])
            elif arg in self._args:
                key = arg
                assert (i + 1) < len(args)
                value = args[i + 1]
                parsed.append([key, value])
                i += 1
            elif arg.startswith('-'):
                raise ArgparseError(f'it appears that {arg} is not a registered flag')
            else:
                parsed.append([arg])
            i += 1
        return parsed


class TranscodingType(Enum):
    WEB_VIDEO_TRANSCODING = 1
    HLS_TRANSCODING_COPY = 2
    HLS_TRANSCODING = 3
    UNKNOWN = 4


def determine_transcoding_type(argv: List[str]) -> TranscodingType:
    set_argv = {*argv}
    if 'hls' in set_argv:
        if argv[argv.index('-vcodec') + 1] == 'copy':
            return TranscodingType.HLS_TRANSCODING_COPY
        return TranscodingType.HLS_TRANSCODING
    elif {'-pix_fmt'}.issubset(set_argv):
        return TranscodingType.WEB_VIDEO_TRANSCODING
    return TranscodingType.UNKNOWN


def get_simple_arg_parser() -> SimpleArgParser:
    return SimpleArgParser() \
        .add_argument('output_file') \
        .add_argument('-i') \
        .add_argument('-h', is_flag=True) \
        .add_argument('-y', is_flag=True) \
        .add_argument('-acodec') \
        .add_argument('-vcodec') \
        .add_argument('-threads') \
        .add_argument('-f') \
        .add_argument('-movflags') \
        .add_argument('-max_muxing_queue_size') \
        .add_argument('-map_metadata') \
        .add_argument('-pix_fmt') \
        .add_argument('-vf') \
        .add_argument('-preset') \
        .add_argument('-maxrate:v') \
        .add_argument('-bufsize:v') \
        .add_argument('-b_strategy') \
        .add_argument('-bf') \
        .add_argument('-r') \
        .add_argument('-level:v') \
        .add_argument('-g:v') \
        .add_argument('-b:a') \
        .add_argument('-hls_time') \
        .add_argument('-hls_list_size') \
        .add_argument('-hls_playlist_type') \
        .add_argument('-hls_segment_filename') \
        .add_argument('-hls_segment_type') \
        .add_argument('-hls_flags') \
        .add_argument('-channel_layout')


class FfmpegCommand:
    def __init__(self, argv: List[str], write_random_to_file: Optional[str] = None,
                 remove_files_after_complete: Optional[List[str]] = None):
        self._argv = argv
        self._write_random_to_file = write_random_to_file
        self._remove_files_after_complete = remove_files_after_complete

    def _run_with_timeout(self):
        proc = subprocess.Popen([ffmpeg_bin_path, *self._argv], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            try:
                stdout, stderr = proc.communicate(timeout=60)
                if proc.returncode != 0:
                    print(f'{ffmpeg_bin_path} returned not 0', file=sys.stderr)
                    print(stderr.decode('UTF-8'), file=sys.stderr)
                    print(stdout.decode('UTF-8'), file=sys.stdout)
                    print(f'{ffmpeg_bin_path} returned not 0', file=log_file
                    print(stderr.decode('UTF-8'), file=log_file)
                    print(stdout.decode('UTF-8'), file=log_file)
                    return proc.returncode
                print(stderr.decode('UTF-8'), file=sys.stderr)
                print(stdout.decode('UTF-8'), file=sys.stdout)
                break
            except subprocess.TimeoutExpired as ex:
                with open(self._write_random_to_file, 'ba') as fp:
                    # 512 because max_muxing_queue_size is 1024? Dunno
                    fp.write(b'lo' * 512)
            # Remove trash from file. Just in case
            with open(self._write_random_to_file, 'wb') as fp:
                pass
            if self._remove_files_after_complete is not None:
                for file_to_remove in self._remove_files_after_complete:
                    os.remove(file_to_remove)

    def _run_blocking(self):
        proc = subprocess.Popen([ffmpeg_bin_path, *self._argv], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            print(f'{ffmpeg_bin_path} returned not 0', file=sys.stderr)
            print(stderr.decode('UTF-8'), file=sys.stderr)
            print(stdout.decode('UTF-8'), file=sys.stdout)
            print(f'{ffmpeg_bin_path} returned not 0', file=log_file)
            print(stderr.decode('UTF-8'), file=log_file)
            print(stdout.decode('UTF-8'), file=log_file)
            return proc.returncode
        print(stderr.decode('UTF-8'), file=sys.stderr)
        print(stdout.decode('UTF-8'), file=sys.stdout)
        if self._remove_files_after_complete is not None:
            for file_to_remove in self._remove_files_after_complete:
                os.remove(file_to_remove)

    def exec(self):
        # Trick peertube runner into thinking that ffmpeg is working. Probably a bad idea, but meh.
        # Might result in corrupted files on the server end
        if self._write_random_to_file is not None:
            self._run_with_timeout()
        else:
            self._run_blocking()


def generate_transcode_command(args: List[List[str]]) -> List[FfmpegCommand]:
    output_file = args[-1][0]
    flag_arguments = dict(map(lambda x: (x[0], x[1:]), filter(lambda x: x[0].startswith('-'), args)))
    input_file = flag_arguments['-i'][0]
    audio_codec = flag_arguments['-acodec'][0]
    container_type = flag_arguments['-f'][0]
    movflags = flag_arguments['-movflags'][0]
    max_muxing_queue_size = flag_arguments['-max_muxing_queue_size'][0]
    map_metadata = flag_arguments['-map_metadata'][0]
    pixel_format = flag_arguments['-pix_fmt'][0]
    channel_layout = ['-channel_layout',
                      flag_arguments['-channel_layout'][0]] if '-channel_layout' in flag_arguments else []
    bitrate_audio = ['-b:a', flag_arguments['-b:a'][0]] if '-b:a' in flag_arguments else []
    video_dimensions = flag_arguments['-vf'][0]
    b_strategy = flag_arguments['-b_strategy'][0]
    b_frames = flag_arguments['-bf'][0]
    framerate = flag_arguments['-r'][0]
    g_v = flag_arguments['-g:v'][0]

    first_pass = ['-i', input_file,
                  '-y', '-acodec', audio_codec, '-vcodec', 'libvpx-vp9', '-f', 'null',
                  '-movflags', movflags, '-map_metadata', map_metadata, '-pix_fmt', pixel_format,
                  *channel_layout, *bitrate_audio, '-vf', video_dimensions,
                  '-deadline', ffmpeg_deadline, '-b_strategy', b_strategy, '-bf', b_frames, '-r', framerate,
                  '-g:v', g_v, '-pass', '1', '-b:v', '0', '-passlogfile', output_file, '-crf', ffmpeg_crf,
                  '/dev/null']
    second_pass = ['-i', input_file,
                   '-y', '-acodec', audio_codec, '-vcodec', 'libvpx-vp9', '-f', container_type,
                   '-movflags', movflags, '-map_metadata', map_metadata, '-pix_fmt', pixel_format,
                   *channel_layout, *bitrate_audio, '-vf', video_dimensions,
                   '-deadline', ffmpeg_deadline, '-b_strategy', b_strategy, '-bf', b_frames, '-r', framerate,
                   '-g:v', g_v, '-pass', '2', '-b:v', '0', '-passlogfile', output_file, '-crf', ffmpeg_crf,
                   '-max_muxing_queue_size', max_muxing_queue_size,
                   output_file]

    return [FfmpegCommand(first_pass, write_random_to_file=output_file),
            FfmpegCommand(second_pass, remove_files_after_complete=[f'{output_file}-0.log'])]


def generate_hls_copy_command(args: List[List[str]]) -> List[FfmpegCommand]:
    output_file = args[-1][0]
    flag_arguments = dict(map(lambda x: (x[0], x[1:]), filter(lambda x: x[0].startswith('-'), args)))
    input_file = flag_arguments['-i'][0]
    hls_time = flag_arguments['-hls_time'][0]
    hls_list_size = flag_arguments['-hls_list_size'][0]
    hls_playlist_type = flag_arguments['-hls_playlist_type'][0]
    hls_segment_filename = flag_arguments['-hls_segment_filename'][0]
    hls_segment_type = flag_arguments['-hls_segment_type'][0]
    hls_flags = flag_arguments['-hls_flags'][0]

    command = [
        '-i', input_file,
        '-acodec', 'copy', '-vcodec', 'copy', '-f', 'mp4', '-hls_time', hls_time, '-hls_list_size', hls_list_size,
        '-hls_playlist_type', hls_playlist_type, '-hls_segment_filename', hls_segment_filename,
        '-hls_segment_type', hls_segment_type, '-f', 'hls', '-hls_flags', hls_flags,
        output_file
    ]

    return [FfmpegCommand(command)]


def generate_hls_command(args: List[List[str]]) -> List[FfmpegCommand]:
    output_file = args[-1][0]
    flag_arguments = dict(map(lambda x: (x[0], x[1:]), filter(lambda x: x[0].startswith('-'), args)))
    input_file = flag_arguments['-i'][0]
    movflags = flag_arguments['-movflags'][0]
    max_muxing_queue_size = flag_arguments['-max_muxing_queue_size'][0]
    map_metadata = flag_arguments['-map_metadata'][0]
    pixel_format = flag_arguments['-pix_fmt'][0]
    video_dimensions = flag_arguments['-vf'][0]
    b_strategy = flag_arguments['-b_strategy'][0]
    b_frames = flag_arguments['-bf'][0]
    framerate = flag_arguments['-r'][0]
    g_v = flag_arguments['-g:v'][0]

    hls_time = flag_arguments['-hls_time'][0]
    hls_list_size = flag_arguments['-hls_list_size'][0]
    hls_playlist_type = flag_arguments['-hls_playlist_type'][0]
    hls_segment_filename = flag_arguments['-hls_segment_filename'][0]
    hls_segment_type = flag_arguments['-hls_segment_type'][0]
    hls_flags = flag_arguments['-hls_flags'][0]

    first_pass = [
        '-i', input_file,
        '-y', '-acodec', 'copy', '-vcodec', 'libvpx-vp9', '-f', 'null', '-movflags', movflags,
        '-max_muxing_queue_size', max_muxing_queue_size, '-map_metadata', map_metadata, '-pix_fmt', pixel_format,
        '-vf', video_dimensions,
        '-deadline', ffmpeg_deadline, '-b_strategy', b_strategy, '-bf', b_frames, '-pass', '1', '-passlogfile',
        output_file, '-r', framerate,
        '-g:v', g_v,
        '/dev/null'
    ]
    second_pass = [
        '-i', input_file,
        '-y', '-acodec', 'copy', '-vcodec', 'libvpx-vp9', '-f', 'mp4', '-movflags', movflags,
        '-max_muxing_queue_size', max_muxing_queue_size, '-map_metadata', map_metadata, '-pix_fmt', pixel_format,
        '-vf', video_dimensions, '-deadline', ffmpeg_deadline, '-b_strategy', b_strategy, '-bf', b_frames,
        '-r', framerate, '-pass', '2', '-passlogfile', output_file, '-g:v', g_v, '-hls_time', hls_time,
        '-hls_list_size', hls_list_size,
        '-hls_playlist_type', hls_playlist_type, '-hls_segment_filename', hls_segment_filename,
        '-hls_segment_type', hls_segment_type, '-f', 'hls', '-hls_flags', hls_flags,
        output_file
    ]

    return [FfmpegCommand(first_pass, write_random_to_file=output_file),
            FfmpegCommand(second_pass, remove_files_after_complete=[f'{output_file}-0.log'])]


def passthrough(argv: List[str]) -> int:
    if print_argv:
        print('ffmpeg command:', ' '.join(argv), file=log_file)

    proc = subprocess.Popen([ffmpeg_bin_path, *argv], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    print(stderr.decode('UTF-8'), file=sys.stderr)
    print(stdout.decode('UTF-8'), file=sys.stdout)
    print(stderr.decode('UTF-8'), file=log_file)
    print(stdout.decode('UTF-8'), file=log_file)
    return proc.returncode


def main(argv: List[str]) -> int:
    if print_argv:
        print('input ffmpeg command:', ' '.join(argv), file=log_file)

    job_type = determine_transcoding_type(argv)
    if job_type == TranscodingType.UNKNOWN:
        print('Unknown ffmpeg command passed!', file=log_file)
        print('Command:', file=log_file)
        print(' '.join(argv), file=log_file)
        return -1
    simple_arg_parser = get_simple_arg_parser()

    parsed = simple_arg_parser.parse(argv)

    if job_type == TranscodingType.WEB_VIDEO_TRANSCODING:
        command = generate_transcode_command(parsed)
    elif job_type == TranscodingType.HLS_TRANSCODING_COPY:
        command = generate_hls_copy_command(parsed)
    elif job_type == TranscodingType.HLS_TRANSCODING:
        command = generate_hls_command(parsed)
    else:
        raise RuntimeError('Should not be reached')

    for sub_command in command:
        sub_command.exec()
        # if print_argv:
        #     print('output ffmpeg command:', ' '.join(sub_command), file=log_file)
        # proc = subprocess.Popen([ffmpeg_bin_path, *sub_command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # stdout, stderr = proc.communicate()
        # if proc.returncode != 0:
        #     print(f'{ffmpeg_bin_path} returned not 0', file=sys.stderr)
        #     print(stderr.decode('UTF-8'), file=sys.stderr)
        #     print(stdout.decode('UTF-8'), file=sys.stdout)
        #     print(f'{ffmpeg_bin_path} returned not 0', file=log_file)
        #     print(stderr.decode('UTF-8'), file=log_file)
        #     print(stdout.decode('UTF-8'), file=log_file)
        #     return proc.returncode
        # print(stderr.decode('UTF-8'), file=sys.stderr)
        # print(stdout.decode('UTF-8'), file=sys.stdout)

    return 0


if __name__ == '__main__':
    filtered_argv = sys.argv[1:]
    if '-encoders' in filtered_argv or '-formats' in filtered_argv:
        sys.exit(passthrough(filtered_argv))
    sys.exit(main(filtered_argv))
