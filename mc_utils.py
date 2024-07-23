from dataclasses import dataclass

@dataclass
class MCTime:
    hour : int = 0
    minute : int = 0
    daylight : bool = False
    tick : int = 0


def parseTime(servertime : str):
    mcdt = MCTime()
    time = int(servertime)
    mcdt.daylight = time >= 0 and time < 13700
    mcdt.hour = ((time // 1000) + 6) % 24
    mcdt.minute = ((time % 1000) * 6) // 100
    mcdt.tick = time
    return mcdt