#!/share/apps/nmi_python/miniconda3/bin/python

s = '\033['
e = '\033[0m'
display_mode = {"d": "0;", "h": "1;", "u": "4;"}
foreground_colour = {"black": "30;", "red": "31;", "green": "32;", "yellow": "33;", "blue": "34;", "wine": "35;",
                     "cyan": "36;",
                     "white": "37;"}
background_colour = {"black": "40m", "red": "41m", "green": "42m", "yellow": "43m", "blue": "44m", "wine": "45m",
                     "cyan": "46m", "white": "47m"}


def colour(st, clr="red", back="black", dis="d"):
    new_str = s + display_mode[dis] + foreground_colour[clr] + background_colour[back] + st + e
    return new_str
