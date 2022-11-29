import subprocess
from pathlib import Path
from utils import random_id
from typing import Tuple


GCC_ARGS = []


def compile(c_contents: str) -> Tuple[bool, bytes, Path]:
    exe_path = Path("/data/" + random_id())
    source_path = exe_path.with_suffix(".c")
    source_path.write_text(c_contents)

    try:
        output = subprocess.check_output(["gcc", source_path, "-o", exe_path, *GCC_ARGS], stderr=subprocess.STDOUT, timeout=5)
        return True, output, exe_path
    except subprocess.CalledProcessError as error:
        return False, error.output, exe_path


def run(exe_path: Path) -> Tuple[bool, bytes]:
    try:
        output = subprocess.check_output([str(exe_path)], stderr=subprocess.STDOUT, timeout=5)
        return True, output
    except subprocess.CalledProcessError as error:
        return False, error.output
