# PokecordCatcher
Selfbot to catch pokemon when they spawn for the Pokecord discord bot

Example config:
```
{
  "token": "<your token>",
  "priority": ["Groudon", "Geodude"],
  "catch_rate": 90,
  "delay": 2,
  "delay_on_priority": true
}
```

Needs python 3.6+, uses fstrings, if you want to use it on a lower version just replace the fstrings with formats.
Keep catch rate low delay high for it to act normally.  
Priority pokemon bypass catch rate.
If a priority pokemon is caught it will be removed from priority list in the current session, manually remove it from config if you restart.
Catch Rate is a percentage out of 100.  
Delay is in seconds.
delay_on_priority can be set to true or false, false means it won't wait and will instantly catch a pokemon if its in priority.
To find out how to get your token visit [Token Tutorial](https://github.com/TheRacingLion/Discord-SelfBot/wiki/Discord-Token-Tutorial).  
Preferably run this on an alt and trade, selfbots violate discord TOS and you can get banned.  
