
import os
import sys
import functools
import requests
import configparser as config

LINKS = {
"neu": "playfab/northeurope",
"weu": "playfab/westeurope",
"eus": "playfab/eastus",
"cus": "playfab/centralus",
"japan": "playfab/japanwest",
"san": "playfab/southafricanorth",
"scus": "playfab/southcentralus",
"wus": "playfab/westus",
"bs": "playfab/brazilsouth",
"sea": "playfab/southeastasia",
"aue": "playfab/australiaeast",
"ause": "playfab/australiasoutheast"
    }

SETTINGS_NAME = "GameSettings.ini"
SEP = "\\"

SETTINGS_ROUTE = os.path.expanduser("~\\Documents\\My Games\\Rainbow Six - Siege\\")
SAVES_ROUTE = "C:\\Program Files (x86)\\Ubisoft\\Ubisoft Game Launcher\\savegames\\"

R6TAB = "https://tabstats.com/siege/player/"
R6TABSEARCH = "https://tabstats.com/siege/search/uplay/"
SEARCH_TEXT = "meta class=\"static\" itemprop=\"name\" content=\""

STEAM_SIEGE = "1843"
UPLAY_SIEGE = "635"

hracc = lambda uuid: "uPlay" if (get_account_type(uuid) == UPLAY_SIEGE) else "Steam"

class AccountException(Exception): pass

@functools.lru_cache(maxsize=256)
def get_ign(uuid: str) -> str:
    "Returns the IGN of the account associated with this uuid"
    req = requests.get(R6TAB + uuid)
    addr = req.text.find(SEARCH_TEXT) + len(SEARCH_TEXT)
    return req.text[addr:addr+15:].split(" ")[0]

@functools.lru_cache(maxsize=256)
def get_uuid(ign: str) -> str:
    "NON-FUNCTIONAL"
    raise Exception("Does not work. Do not use")
    print(R6TABSEARCH + ign)
    req = requests.get(R6TABSEARCH + ign)
    with open("test.txt", "w") as f:
        f.write(req.text)

@functools.lru_cache(maxsize=256)
def get_account_type(uuid: str) -> str: # returns None, STEAM_SIEGE, UPLAY_SIEGE
    "Attempt to find if the UUID given is associated with a uPlay or Steam account by checking uplay/savegames directory"
    try:
        routes = os.listdir(SAVES_ROUTE + uuid)
        if STEAM_SIEGE in routes:
            return STEAM_SIEGE
        elif UPLAY_SIEGE in routes:
            return UPLAY_SIEGE
        return
    except FileNotFoundError:
        return

def default_api() -> str:
    "returns `1` if Vulkan in settings. `0` otherwise."
    try:
        conf = load_config(SETTINGS_ROUTE + "settings.ini")
    except Exception:
        create_config(SETTINGS_ROUTE + "settings.ini")
        conf = load_config(SETTINGS_ROUTE + "settings.ini")
    return conf.get("MAIN", "VULKAN")

def create_config(route: str) -> None:
    "Creates siege.py's setting file"
    conf = config.ConfigParser()
    conf["MAIN"] = {"VULKAN": "0"}
    write_config(conf, route)

def load_config(route: str) -> config.ConfigParser:
    "Loads a `config.ConfigParser` from a given file route"
    conf = config.ConfigParser()
    with open(route, "r") as f:
        conf.read_string(f.read())
    return conf

def write_config(config: config.ConfigParser, route: str) -> None:
    "Writes given config to file route `route`"
    with open(route, "w") as f:
        config.write(f)

def get_routes(source: str) -> [str]:
    "Gets a list of all config file locations in a directory"
    routes = []
    for route in os.listdir(source):
        # uuids are 36 characters long and have 4 `-` characters in them
        if len(route) == 36 and len(route.split("-")) == 5:
            routes.append(source + route + SEP + SETTINGS_NAME)
    return routes

def get_configs(routes: [str]) -> [config.ConfigParser]:
    "Gets all config files from a list of file names"
    confs = []
    for route in routes:
        confs.append(load_config(route))
    return confs

def set_configs(confs: [config.ConfigParser], routes: [str]) -> None:
    "Sets all routes given to all confs given"
    for conf, route in zip(confs, routes):
        write_config(conf, route)

def launch_dx11(distro: str) -> None:
    "Uses os.startfile to launch Siege with DX11"
    os.startfile("uplay://launch/{}/".format(distro))

def launch_vulkan(distro: str) -> None:
    "Uses os.startfile to launch Siege with Vulkan"
    os.startfile("uplay://launch/{}/1".format(distro))

def region_swap(routes: [str], region: str) -> None:
    "Sets all routes' given regions to `region`"
    confs = get_configs(routes)
    for conf in confs:
        conf.set("ONLINE", "DataCenterHint", region)
    set_configs(confs, routes)

def update(routes: [str]) -> str:
    "Returns best UUID: Use most recent of the routes given (by win10 `date modified`) and replace other elements with that"
    best = 0, None
    for route in routes:
        time = os.path.getmtime(route)
        if time > best[0]:
            best = time, route
    uuid = best[1].split("\\")[-2]
    conf = load_config(best[1])
    set_configs((conf,)*len(routes), routes)
    return uuid
