import argparse
import re
import subprocess
from pathlib import Path
from typing import Literal

from inquirer import List, prompt
from inquirer.shortcuts import confirm

rc_base_questions = [
    List(
        'rc_base',
        message='Which version is this a release candidate for?',
        choices=['patch', 'minor', 'major'],
    )
]

rc_next_step_questions = [
    List(
        'rc_next',
        message='You are already on a release candidate. What would you like to do?',
        choices=['Bump to next rc', 'Promote to final release'],
    )
]

main_bump_questions = [
    List(
        'bump_type',
        message='What kind of release are you preparing?',
        choices=['rc', 'patch', 'minor', 'major'],
    )
]


def bumpit(
    from_version: str,
    rule: Literal['major', 'minor', 'patch', 'rc'],
    rc_base: str | None = None,
    promote_rc: bool = False,
) -> tuple[str, str]:
    if '-' in from_version:
        main_version, pre_release = from_version.split('-')
    else:
        main_version = from_version
        pre_release = None

    major, minor, patch = map(int, main_version.split('.'))

    if rule == 'major':
        major += 1
        minor = 0
        patch = 0
        pre_release = None
    elif rule == 'minor':
        minor += 1
        patch = 0
        pre_release = None
    elif rule == 'patch':
        patch += 1
        pre_release = None
    elif rule == 'rc':
        if pre_release and pre_release.startswith('rc'):
            if promote_rc:
                pre_release = None
            else:
                rc_number = int(pre_release[2:]) + 1
                pre_release = f'rc{rc_number}'
        else:
            if rc_base == 'major':
                major += 1
                minor = 0
                patch = 0
            elif rc_base == 'minor':
                minor += 1
                patch = 0
            elif rc_base == 'patch':
                patch += 1
            else:
                raise ValueError("rc_base must be 'major', 'minor', or 'patch'")
            pre_release = 'rc1'
    else:
        raise ValueError("Invalid rule. Use 'major', 'minor', 'patch', or 'rc'.")

    to_version = f'{major}.{minor}.{patch}'
    if pre_release:
        to_version += f'-{pre_release}'

    return from_version, to_version


def bump_version(pyproject_file: Path) -> None:
    """Bump the version of a pyproject.toml file"""
    try:
        with open(pyproject_file, 'r') as f:
            pyproject = f.read()

        version_match = re.search(r'^\s*version\s*=\s*["\'](.+?)["\']', pyproject, re.MULTILINE)
        if not version_match:
            print('Could not find a valid version line.')
            raise SystemExit(1)
        version_line = version_match.group(0)
        version = version_match.group(1)
        from_version = version.split('+')[0]

        bump_type = None
        rc_base = None
        promote_rc = False

        if '-' in from_version and from_version.split('-')[1].startswith('rc'):
            rc_next_result = prompt(rc_next_step_questions)
            if not rc_next_result:
                print('Cancelled.')
                raise SystemExit(1)
            bump_type = 'rc'
            if rc_next_result['rc_next'] == 'Promote to final release':
                promote_rc = True
        else:
            result = prompt(main_bump_questions)
            if not result:
                print('No version bump requested')
                raise SystemExit(1)

            bump_type = result['bump_type']

            if bump_type == 'rc':
                rc_base_result = prompt(rc_base_questions)
                if not rc_base_result:
                    print('Cancelled.')
                    raise SystemExit(1)
                rc_base = rc_base_result['rc_base']

        from_version, to_version = bumpit(from_version, bump_type, rc_base, promote_rc)

        print(f'Bumping version from {from_version} to {to_version}')

        proceed = confirm(
            message=f'Is it correct? {from_version} -> {to_version}',
            default=True,
        )

        if proceed is True:
            with open(pyproject_file, 'w', newline='\n') as f:
                pyproject = pyproject.replace(version_line, f'version = "{to_version}"')
                f.write(pyproject)
            print(f'Bumped version from {from_version} to {to_version}')

            # commit?
            commit_changes = confirm(message='Do you want to commit the changes?', default=True)
            if commit_changes:
                try:
                    # Commit the changes using git
                    subprocess.run(['git', 'add', '.'], check=True)
                    subprocess.run(['git', 'commit', '-m', f'release: 🔖 {to_version}'], check=True)
                    print('Changes committed successfully.')
                except subprocess.CalledProcessError as e:
                    print(f'Error committing changes: {e}')
        else:
            print('Cancelled.')
            raise SystemExit(1)

    except KeyboardInterrupt:
        print('\nCancelled.')
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Bump the version of a pyproject.toml file interactively',
    )
    parser.add_argument(
        'path',
        type=Path,
        nargs='?',
        default=Path.cwd() / 'pyproject.toml',
        help='Path to the pyproject.toml file (defaults to the current directory)',
    )
    args = parser.parse_args()

    bump_version(args.path)
