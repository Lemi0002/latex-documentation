import os
import sys
import argparse
import subprocess
import importlib.util
from importlib.machinery import ModuleSpec
from dataclasses import dataclass
from typing import Callable


def install_requirements(path: str) -> bool:
    if sys.prefix == sys.base_prefix:
        print("error: no virtual environment is active")
        return False

    subprocess.run([
        "pip",
        "install",
        "-r",
        os.path.join(path, "requirements.txt"),
    ])
    return True


def export_print_configuration(path: str, file_name: str) -> None:
    with open(os.path.join(path, file_name), 'a') as file:
        file.write('\\def\\printMode{}')


def run_build(path: str) -> None:
    output_directory: str = 'build'
    directories: list[str] = [
    ]

    def build_svg(file_name_source: str, file_name_target: str, file_source: str, file_target: str, directory: str) -> None:
        subprocess.run(['inkscape', '--export-type=pdf', os.path.join(directory, file_name_source), '--export-filename=' + os.path.join(directory, file_name_target)], check=True)

    def build_tex(file_name_source: str, file_name_target: str, file_source: str, file_target: str, directory: str) -> None:
        subprocess.run(['tectonic', '--outfmt', 'pdf', file_name_source], cwd=directory, check=True)

    def build_py(file_name_source: str, file_name_target: str, file_source: str, file_target: str, directory: str) -> None:
        subprocess.run(['python', '-m', f'{directory}.{file_name_source.replace('.py', '')}'], check=True)

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
        directory: str = os.path.join(path, directory)
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

    if not os.path.exists(os.path.join(path, output_directory)):
        os.mkdir(os.path.join(path, output_directory))

    subprocess.run(['tectonic', '-r', '2', '--outdir', os.path.join(path, output_directory), '--outfmt', 'pdf', 'main.tex'], check=True)


if __name__ == "__main__":
    script_path: str = os.path.dirname(os.path.realpath(__file__))
    script_basename_head: str = os.path.basename(__file__).split(".")[0]

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog=f"{script_basename_head}",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="run various project related commands"
    )

    parser.add_argument(
        "-r", "--requirements",
        default=False,
        action="store_true",
        help="install python requirements into an active virtual environment"
    )
    parser.add_argument(
        "-p", "--print",
        default=False,
        action="store_true",
        help="color links black for printing"
    )

    namespace: argparse.Namespace = parser.parse_args()
    file_name_configuration: str = '.configuration'

    if namespace.requirements:
        install_requirements(script_path)
        exit(0)

    if os.path.exists(file_name_configuration):
        os.remove(file_name_configuration)

    if namespace.print:
        export_print_configuration(script_path, file_name_configuration)

    run_build(script_path)
