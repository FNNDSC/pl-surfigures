from pathlib import Path
import shlex
import subprocess as sp
import time
from tempfile import TemporaryDirectory
from typing import Optional

from loguru import logger

from surfigures.inputs import InputSet
from surfigures.options import Options


def run_surfigures(input_set: InputSet, output_file: Path, options: Options) -> Optional[float]:
    """
    Returns ``None`` if there was an error, or the time spent running ``verify_surface_all.pl`` in seconds.
    """
    with TemporaryDirectory() as tmp_dir:
        sorted_inputs = input_set.expand(options, Path(tmp_dir))
        cmd = sorted_inputs.to_cmd(output_file)
        log_file = output_file.with_suffix('.log')
        logger.info('running: {} > {}', shlex.join(map(str, cmd)), log_file)
        start = time.monotonic_ns()
        with log_file.open('wb') as f:
            p = sp.run(cmd, stderr=sp.STDOUT, stdout=f)

    end = time.monotonic_ns()
    elapsed = (end - start) / 1e9
    ok = p.returncode == 0
    msg = f'{tuple(map(str, input_set.src))} --> {output_file} took {elapsed:.1f}s'
    if ok:
        logger.info(msg)
        return elapsed
    else:
        logger.error('{}, please check {}', msg, log_file)
        return None
