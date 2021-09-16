"""
This file is part of the vaccination.py.

(c) 2021 Temuri Takalandze <me@abgeo.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

from vaccination import __version__, __copyright__, __email__
from vaccination.core.app import App


def __print_banner() -> None:
    print("__     __             _             _   _             ")
    print(r"\ \   / /_ _  ___ ___(_)_ __   __ _| |_(_) ___  _ __  ")
    print(r" \ \ / / _` |/ __/ __| | '_ \ / _` | __| |/ _ \| '_ \ ")
    print(r"  \ V / (_| | (_| (__| | | | | (_| | |_| | (_) | | | |")
    print(r"   \_/ \__,_|\___\___|_|_| |_|\__,_|\__|_|\___/|_| |_|")
    print(f"\n     v{__version__} {__copyright__} ({__email__})\n")


def main() -> int:
    """
    Main function.
    :return: Exit code.
    """

    __print_banner()
    return App.run()


if __name__ == "__main__":
    import sys

    sys.exit(main())
