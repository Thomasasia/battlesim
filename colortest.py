from termcolor import colored

colors = {}

colors["black"] = "black"
colors["red"]="red"
colors["green"]="green"
colors["yellow"]="yellow"
colors["blue"]="blue"
colors["magenta"]="magenta"
colors["cyan"]="cyan"
colors["white"]="white"
colors["light_grey"]="light_grey"
colors["dark_grey"]="dark_grey"
colors["light_red"]="light_red"
colors["light_green"]="light_green"
colors["light_yellow"]="light_yellow"
colors["light_blue"]="light_blue"
colors["light_magenta"]="light_magenta"
colors["light_cyan"]="light_cyan"

for key in colors.keys():
    print(colored(key, colors[key]))