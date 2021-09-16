"""
Main application module.

This file is part of the vaccination.py.

(c) 2021 Temuri Takalandze <me@abgeo.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

from vaccination.core.task.main import MainTask


class App:
    """
    Application class.
    """

    @staticmethod
    def run() -> int:
        """
        Run application.

        :return: Exit code.
        """

        return MainTask().run()
