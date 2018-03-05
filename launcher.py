import sys
from pokecordcatcher import Poke

if __name__ == "__main__":
    try:
        config_path = sys.argv[1]
    except:
        config_path = 'config.json'

    bot = Poke(config_path)
    bot.run()
