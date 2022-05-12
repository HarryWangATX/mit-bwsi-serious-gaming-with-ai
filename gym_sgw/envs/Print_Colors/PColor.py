class PFont:
    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strikethrough = '\033[09m'
    invisible = '\033[08m'


class PFore:
    reset = '\033[0m'
    black = '\033[30m'
    red = '\033[31m'
    green = '\033[32m'
    orange = '\033[33m'
    blue = '\033[34m'
    purple = '\033[35m'
    cyan = '\033[36m'
    lightgrey = '\033[37m'
    darkgrey = '\033[90m'
    lightred = '\033[91m'
    lightgreen = '\033[92m'
    yellow = '\033[93m'
    lightblue = '\033[94m'
    pink = '\033[95m'
    lightcyan = '\033[96m'


class PControl:
    reset = '\033[0m'
    cls = '\033[2J'
    home = '\033[H'


class PBack:
    reset = '\033[0m'
    black = '\033[40m'
    red = '\033[41m'
    green = '\033[42m'
    orange = '\033[48;2;230;93;35m'
    blue = '\033[44m'
    purple = '\033[45m'
    cyan = '\033[46m'
    lightgrey = '\033[48;2;136;132;140m'
    darkgrey = '\033[48;2;75;75;81m'  #old, too light -> #'\033[100m'
    lightred = '\033[101m'
    brown = '\033[48;2;114;52;21m'
    neonred = '\033[48;2;255;0;43m'
    tangerine = '\033[48;2;222;134;2m'