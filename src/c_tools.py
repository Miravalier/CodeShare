import asyncio
import subprocess
from functools import partial
from pathlib import Path
from utils import random_id
from typing import Tuple


GCC_ARGS = []


async def async_subprocess(*args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(
        subprocess.check_output,
        args,
        stderr=subprocess.STDOUT,
        timeout=5,
    ))


async def compile(c_contents: str) -> Tuple[bool, bytes, Path]:
    exe_path = Path("/data/" + random_id())
    source_path = exe_path.with_suffix(".c")
    source_path.write_text(c_contents)

    try:
        output = await async_subprocess("gcc", source_path, "-o", exe_path, *GCC_ARGS)
        return True, output, exe_path
    except subprocess.CalledProcessError as error:
        return False, error.output, exe_path
    except subprocess.TimeoutExpired as error:
        return False, b"Compilation killed by timeout!", exe_path


async def run(exe_path: Path) -> Tuple[bool, bytes]:
    try:
        output = await async_subprocess(str(exe_path))
        return True, output
    except subprocess.CalledProcessError as error:
        return False, error.output
    except subprocess.TimeoutExpired as error:
        return False, b"Process killed by timeout!"
