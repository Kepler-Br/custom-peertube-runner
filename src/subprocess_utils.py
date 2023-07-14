import subprocess
from io import BytesIO
from typing import List, Optional, Generator, Tuple, Self

from barkeputils import default_if_none


def execute_shell_generator(command: List[str], timeout: Optional[float] = None) -> \
        Generator[tuple[Optional[BytesIO], Optional[BytesIO]], None, int]:
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        try:
            proc_stdout, proc_stderr = proc.communicate(timeout=timeout)
            yield proc_stdout, proc_stderr
            break
        except subprocess.TimeoutExpired as ex:
            yield ex.stdout, ex.stderr
    return proc.returncode


class ShellCommand:
    def __init__(self, executable: str, args: Optional[List[str]] = None):
        self._arg_list = default_if_none(args, [])
        self._executable = executable

    def args(self, *args) -> Self:
        self._arg_list.extend(args)

        return self

    def get_command_str(self) -> str:
        return ' '.join([self._executable, *self._arg_list])

    def run(self, timeout: Optional[float] = None) -> \
            Generator[tuple[Optional[BytesIO], Optional[BytesIO]], None, int]:
        return execute_shell_generator(command=[self._executable, *self._arg_list], timeout=timeout)

    def block(self) -> Tuple[bytes, bytes, int]:
        proc = subprocess.Popen([self._executable, *self._arg_list], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        return stdout, stderr, proc.returncode
