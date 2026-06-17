"""Terminal bell sound."""
import sys


class Sound:
    def __init__(self, enabled=True, volume=1, output=None):
        self.enabled = enabled
        self.volume = volume
        self.output = output or sys.stdout

    def beep(self, count=1):
        if not self.enabled or self.volume <= 0:
            return
        self.output.write("\a" * count * self.volume)
        self.output.flush()

    def correct(self):
        self.beep(1)

    def incorrect(self):
        self.beep(2)

    def win(self):
        self.beep(3)

    def lose(self):
        self.beep(2)
