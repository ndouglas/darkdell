# _Wizardry VI: Bane of the Cosmic Forge_

I have a new project (I know, I know); I'm reverse-engineering the classic dungeon crawler game, Sir-Tech Software's _Wizardry VI: Bane of the Cosmic Forge_ (1990), in TypeScript.

My fifteenth birthday - 1995. I was in the eighth grade. And the middle school librarian, a genuinely kind and sweet man whose name sadly escapes me at the moment came to my math class (first class of the day) and gave me a birthday card which included $15. I was overjoyed, and begged my mother to take me to the one store in town that I knew had computer games: Radio Shack.

My mother had recently purchased a computer "for the family" (it was just her and me): a Packard Bell 486 DX-33MHz (with the Turbo button that would drop it down to 25MHz, natch). I didn't actually have any other computer games aside from the ones that came included with Windows 3.11 and those which I could get off BBSes. I had _some_ internet access, because my mom attended night classes in Albuquerque once a week and the school had a computer lab I could sneak into, but hadn't really gotten to exploit it yet.

As it turned out, Radio Shack only had a couple video games - a few new ones, which I couldn't afford, and some older ones. One of them was _Wizardry VI: Bane of the Cosmic Forge_. I read the back:

> True FRP Simulation!<br>
> Like a true game master. Bane of the Cosmic Forge rolls the dice, consults its charts and applies the rules. From the 400 items of armor and weaponry researched for authenticity - right down to their weights - to the realistic combat structure - incorporating Primary and Secondary attack- everything, absolutely everything, is calculated.<br>
> Full-Color, Animated Graphics!<br>
> You'll see swords swinging before your eyes; creatures of all shapes and forms will move before you; spells coming from your magician will swirl through the air. You'll walk under gargoyle-laden arches and watch candles flicker in their sconces.
> Your PC's internal speaker will play all of these digitized sounds without any add-on hardware. swords swinging, monsters venting their anger and spells letting fly.

and I thought that sounded pretty damned cool. I looked on the side and saw that my computer could handle the minimum requirements, which was even better news (I knew some of the new games coming out required 8MB of RAM, and I had to play tricks to get it to play _DOOM_).

If I remember correctly, this came out to exactly $15.

I remember excitedly reading the manual on the way home (we lived in Grants, an hour away from my middle school, so I had plenty of time to digest it) and felt quite knowledgeable by the time I got into the office.

This was some serious shit, obviously. I generated my characters as fast as I could, but not with undue haste, and proceeded into the dungeon. The sounds - the clicks and rasps - seemed so atmospheric through the twin external speakers. I picked locks, I forced open doors, I found treasure chests.

I remember jamming a door almost immediately. Something I'd missed in the manual, maybe, or didn't completely understand -- if you failed to pick a lock, or failed to force it open with raw strength, there was a chance that the door would jam and whatever lay behind it would be lost forever. As it turns out, as is somewhat common of games of its era, it's _very_ easy to render the game unwinnable.

I was not a terribly wise gamer back then, and I've never liked mapping, taking notes, etc, so what I learned of the castle map, I learned by raw memorization - just going into one room after another, and all of them repeatedly in sequence, and searching, or fighting things, or whatever. Progress was incredibly slow. I jammed doors and wasn't smart enough to save-scum. Every once in a while, I'd restart with a different cast of heroes, learning _some_ lessons... but not the most valuable ones.

At some point, I started my last game of _Bane of the Cosmic Forge_. I rolled up a good team and explored. I jammed a critical door and didn't realize it. I found a place where I could grind and earn experience quite efficiently, and so I raised my characters to quite serious levels (~12 or so), but because of the door I had jammed, I was stuck. I was unwilling to restart and unable to make further progress. I would still start the game every once in a while and maybe grind for more XP (which, of course, slowed), but I never escaped the castle.

Of course, I returned to the game a few years later with an emulator and a walkthrough and beat it, but that's not particularly interesting. What's interesting to me is the feeling of being alone in my room at night, the light of the CRT on my face, the clicks and drags and whirs of the castle around me, the strange groans and howls and screams of the monsters, the intrigue and wonder I could feel from minimal and monotonous graphics.

Anyway, I'm working now on reverse-engineering this game and creating an accurate port of it to TypeScript. I recently completed a port of _Zork_ from ZIL to Clojure, and found it a thoroughly fun and interesting project. I couldn't play _Zork_ again for the first time, but I could re-explore it, this time on an engineering level, and learn the code and data and patterns behind a game that meant to much to me.

_Zork_ is now open-source; _Wizardry VI_ is not, and that requires a lot of reverse engineering... but nevertheless, the tools exist.

I'm still in the early stages, but you can find my port here: https://wiz6.goldentooth.net/ It also includes a rich-featured data explorer to look at the sprites and fonts, demonstrate how images and text are drawn to the screen, dive into the decompiled functions, tinker with game mechanics, etc. If you check it out, I hope you enjoy! 😊

