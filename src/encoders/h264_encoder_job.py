import os.path
from io import BytesIO
from typing import Set, Generator

from peertube_api_client import ApiV1RunnersJobsJobUUIDAcceptPost200ResponseJob, RunnerJobType, \
    VODWebVideoTranscoding1Input, VODWebVideoTranscoding1Output

from encoders.abstract_job import AbstractEncoderJob
from subprocess_utils import ShellCommand


# Original FFMpeg commands:
# local-env-peertube-1   |   "shellCommand": "ffmpeg -n 15 /usr/bin/ffmpeg -i /var/www/peertube/storage/videos/private/ed9bbb92-4417-4109-98b7-d20d43f36aef-144.webm -y -acodec aac -vcodec libx264 -threads 2 -f mp4 -movflags faststart -max_muxing_queue_size 1024 -map_metadata -1 -pix_fmt yuv420p -channel_layout stereo -b:a 256k -vf scale=w=-2:h=144 -preset veryfast -maxrate:v 205348 -bufsize:v 410696 -b_strategy 1 -bf 16 -r 30 -level:v 3.1 -g:v 60 /var/www/peertube/storage/tmp/35-transcoded.mp4"
# local-env-peertube-1   |   "shellCommand": "ffmpeg -n 15 /usr/bin/ffmpeg -i /var/www/peertube/storage/videos/68babf8d-3494-4357-a092-d54401a2ba43-144.mp4 -y -acodec copy -vcodec copy -threads 2 -f mp4 -hls_time 4 -hls_list_size 0 -hls_playlist_type vod -hls_segment_filename /var/www/peertube/storage/tmp/hls/8302778b-d293-4a98-8d1f-acb40f752d2f-144-fragmented.mp4 -hls_segment_type fmp4 -f hls -hls_flags single_file /var/www/peertube/storage/tmp/hls/8302778b-d293-4a98-8d1f-acb40f752d2f-144.m3u8"
class H265EncoderJob(AbstractEncoderJob):
    def can_accept(self, inp: VODWebVideoTranscoding1Input, out: VODWebVideoTranscoding1Output,
                   job_type: RunnerJobType) -> bool:
        return True

    def get_supported_job_types(self) -> Set[RunnerJobType]:
        return {RunnerJobType.VOD_MINUS_WEB_MINUS_VIDEO_MINUS_TRANSCODING,
                RunnerJobType.VOD_MINUS_HLS_MINUS_TRANSCODING,
                RunnerJobType.VOD_MINUS_AUDIO_MINUS_MERGE_MINUS_TRANSCODING,
                RunnerJobType.LIVE_MINUS_RTMP_MINUS_HLS_MINUS_TRANSCODING}

    def transcode(self, job: ApiV1RunnersJobsJobUUIDAcceptPost200ResponseJob, target_dir: str, input_video: str) -> str:
        pass

    def transcode_generator(self,
                            job: ApiV1RunnersJobsJobUUIDAcceptPost200ResponseJob,
                            target_dir: str,
                            input_video: str) -> Generator[None, None, str]:
        output_file = os.path.splitext(os.path.basename(input_video))[0] + '_output.mp4'
        output_file = os.path.join(target_dir, output_file)
        command = ShellCommand('ffmpeg') \
            .args('-y') \
            .args('-i', input_video) \
            .args('-acodec', 'aac', '-vcodec', 'libx264', '-threads', '2', '-f', 'mp4', '-movflags', 'faststart',
                  '-max_muxing_queue_size', '1024', '-map_metadata', '-1', '-pix_fmt', 'yuv420p', '-channel_layout',
                  'stereo', '-vf', 'scale=w=-2:h=144', '-b_strategy', '1', '-bf', '16', '-r', '30', '-level:v', '3.1',
                  '-g:v', '60') \
            .args('-preset', 'veryfast') \
            .args('-bufsize:v', '410696', '-maxrate:v', '205348', '-b:a', '256k') \
            .args(output_file)

        print(command.get_command_str())

        g = command.run(timeout=5.0)
        total_stderr = BytesIO()
        try:
            while True:
                _, stderr = next(g)
                total_stderr.write(stderr)
                yield
        except StopIteration as ex:
            if ex.value != 0:
                raise RuntimeError(f'ffmpeg exited with {ex.value} status. Stderr:\n'
                                   f'{total_stderr.read().decode("UTF-8")}')

        return output_file
