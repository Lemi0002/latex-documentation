import subprocess
import os
import sys
from dataclasses import dataclass
from typing import Callable


output_directory: str = 'build'
file_name_configuration: str = '.configuration'
directories: list[str] = [
]


def build_svg(file_name_source: str, file_name_target: str, file_source: str, file_target: str, directory: str) -> None:
    subprocess.run(['inkscape', '--export-type=pdf', os.path.join(directory, file_name_source), '--export-filename=' + os.path.join(directory, file_name_target)], check=True)


def build_tex(file_name_source: str, file_name_target: str, file_source: str, file_target: str, directory: str) -> None:
    subprocess.run(['tectonic', '--outfmt', 'pdf', file_name_source], cwd=directory, check=True)


def build_py(file_name_source: str, file_name_target: str, file_source: str, file_target: str, directory: str) -> None:
    subprocess.run(['python', '-m', f'{directory}.{file_name_source.replace('.py', '')}'], check=True)
    os.path.basename


@dataclass
class Job:
    source: str
    target: str
    build: Callable


jobs: list[Job] = [
    Job(source='.svg', target='.pdf', build=build_svg),
    Job(source='.tex', target='.pdf', build=build_tex),
    Job(source='.py', target='.pdf', build=build_py),
]

for directory in directories:
    for file_name_source in os.listdir(directory):
        for job in jobs:
            if file_name_source.endswith(job.source):
                file_name_target: str = file_name_source.replace(job.source, job.target)
                file_target: str = os.path.join(directory, file_name_target)
                file_source: str = os.path.join(directory, file_name_source)
                state_target: os.stat_result|None = None
                state_source: os.stat_result = os.stat(file_source)

                if os.path.exists(file_target):
                    state_target = os.stat(file_target)

                if ((state_target is None) or (state_source.st_mtime > state_target.st_mtime)):
                    print('>>> Exporting', file_name_target)
                    job.build(file_name_source, file_name_target, file_source, file_target, directory)

if os.path.exists(file_name_configuration):
    os.remove(file_name_configuration)

for argument in sys.argv[1:]:
    if argument == '--print':
        with open(file_name_configuration, 'a') as file:
            file.write('\\def\\printMode{}')
    else:
        print('FLAGS:')
        print('    --help    Print this messsage')
        print('    --print   Color links black for printing')
        exit()

if not os.path.exists(output_directory):
    os.mkdir(output_directory)

subprocess.run(['tectonic', '-r', '2', '--outdir', output_directory, '--outfmt', 'pdf', 'main.tex'], check=True)
