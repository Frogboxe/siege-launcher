
import sys
from siegeproc import *

DEBUG = False
VULKAN_TARGET = ["dx11", "vulkan"]

CMD_LENGTH = 36
cmd_conv = lambda txt: 1 + CMD_LENGTH - len(txt) // 2
even = lambda txt: (len(txt) % 2) == 0
cmd_line = lambda txt: (cmd_conv(txt) * '-') + '[' + txt + ']' + (cmd_conv(txt) * '-') + ('-' if even(txt) else '')
form = lambda txt, ln: txt.format(line0=cmd_line(ln))
err_msg = lambda: print("Invalid Arguments. Consult -help")

HELP = form("""
{line0}
-set dx11/vulkan
\tSets the Graphics API to use when launching the game.
-reg weu/neu/...
\tSets the region on all accounts to input region
\tFind full list with command -list
-list
\tReveals full list of regions to switch to
-uuid SiegePlayer6969
\tQuery R6TAB.com to find this player's UUID
-ign `uuid`
\tQuery R6TAB.com to find this UUID's IGN
\n
""", "HELP")

def display(uuid):
    print("\tUUID:\t\t{}\n\tAccount Name:\t{}\tAccount Type:\t{}\n".format(uuid, get_ign(uuid).ljust(8, " "), hracc(uuid)))

def list_routes(routes):
    for route in routes:
        uuid = route.split("\\")[-2]
        display(uuid)

class Routes:
    rtb = False
    def error(msg):
        print(cmd_line("ERROR"))
        print(msg)
        print(cmd_line("ERROR"))
        rtb = True

    def update(routes):
        print(cmd_line("UPDATE"))
        print("Updating settings files from found source:")
        uuid = update(routes)
        print("\tUUID:\t\t{}\n\tAccount Name:\t{}\tAccount Type:\t{}".format(uuid, get_ign(uuid), hracc(uuid)))
    
    def help():
        print(HELP)

    def api(state=None):
        if state in (0, 1, "0", "1"):
            state = VULKAN_TARGET[int(state)]
        if state not in VULKAN_TARGET:
            Routes.error("State `{}` given is not a valid state (Vulkan / DX11 / 0 / 1)")
        target = SETTINGS_ROUTE + "settings.ini"
        conf = load_config(target)
        oldState = conf.get("MAIN", "VULKAN")
        translated = VULKAN_TARGET[int(oldState)]
        index = VULKAN_TARGET.index(state)
        print("Loading old configuration; information:\n\t{}\n\tFound State:\t{}\tTranslated:\t{}"
              .format(target, oldState, translated))
        print("Saving new configuration; information:\n\t{}\n\tSet State:\t{}\tTranslated:\t{}"
              .format(target, index, state))
        conf.set("MAIN", "VULKAN", str(index))
        write_config(conf, target)

    def region(routes, regID):
        print(regID)
        print(cmd_line("REGION"))
        region = LINKS[regID]
        print("Switching region to `{}`\n\tData Centre:\t{}\n".format(regID, region))
        list_routes(routes)
        region_swap(routes, region)

    def list():
        print(cmd_line("LIST"))
        print("Listing all regions and region identifiers:")
        for key in LINKS:
            print("\t{}:\t\t{}".format(key, LINKS[key]))

    def get_ign(uuid):
        print(cmd_line("GET_IGN"))
        ign = get_ign(uuid)
        if ign == "":
            print("Cannot find IGN for UUID `{}`".format(uuid))
            return
        display(uuid)

    def launch(api):
        print(cmd_line("LAUNCH"))
        print("Launching Siege:\n\tAPI Used:\t{}\t\tLaunch Protocol:\t{}".format(VULKAN_TARGET[int(api)].upper(), UPLAY_SIEGE))
        if not DEBUG:
            if api == "1":
                launch_vulkan(UPLAY_SIEGE)
                print("Launch Vulkan Command sent")
            elif api == "0":
                launch_dx11(UPLAY_SIEGE)
                print("Launch DX11 Command sent")

def parse(argv=sys.argv):
    routes = get_routes(SETTINGS_ROUTE)
    api = default_api()
    if len(argv) > 1:
        if argv[1] == "-help" and not Routes.rtb:
            Routes.help()
        elif argv[1] == "-api" and not Routes.rtb:
            print(cmd_line("API_SET"))
            if len(argv) != 3:
                Routes.error("-api command requires an additional argument to define target api")
                return
            Routes.api(argv[2])    
        elif argv[1] == "-region" and not Routes.rtb:
            if len(argv) != 3:
                Routes.error("-region command requires an additional argument to define target region")
                return
            Routes.update(routes)
            Routes.region(routes, argv[2])
        elif argv[1] == "-list" and not Routes.rtb:
            Routes.list()
        elif argv[1] == "-update" and not Routes.rtb:
            Routes.update(routes)
        elif argv[1] == "-get-ign" and not Routes.rtb:
            if len(argv) != 3:
                Routes.error("-get-ign requires an input UUID")
                return
            Routes.get_ign(argv[2])
        elif argv[1] in LINKS and not Routes.rtb:
            region = argv[1]
            Routes.update(routes)
            Routes.region(routes, region)
            Routes.launch(api)
    Routes.rtb = False
    print(cmd_line("DONE"))

if __name__ == "__main__":
    if DEBUG:
        parse(["", "weu"])
    else:
        parse()
        cmd = input("->\t")
        while cmd.lower() not in ("q", "quit", "exit", "e", "close", "stop"):
            parse(("", *(cmd.split(" "))))
            cmd = input("->\t")
    


































