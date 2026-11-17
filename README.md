# Kitchen Rush

A single-player, 2D restaurant game built with Python and Pygame for CS 122. This version uses temporary shapes and text; artwork, animation, and sound are still to come.

## Install and run

Python 3 and Pygame are required. From the project folder:

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

Enter a username and press Enter. Returning players can use the same name to load their profile. At the menu, press Enter to continue at the highest unlocked level, or use 1/2 to select an unlocked level. Usernames are case-sensitive local profile names, not secure accounts.

## Controls

- **WASD or arrow keys:** move.
- **E:** interact with the nearest station, or pick up a nearby dropped item when your hands are empty. At a storage station, this takes an ingredient; at a processing station, it places a valid raw ingredient or retrieves the finished ingredient; at assembly, it adds the carried ingredient; at serving, it delivers a finished dish; at trash, it discards the carried item.
- **Q:** drop the carried item on the floor. Stand nearby with empty hands and press E to pick it up.
- **R near assembly:** discard the ingredients currently on that counter.
- **Tab:** show or hide the recipe guide.
- **After a round:** R retries, M returns to the menu, and N advances after reaching the target (if another level exists).

## How to play

Collect ingredients from the labeled stations at the top. Chop lettuce or tomato at Cutting (2 seconds); cook patty, tomato, or mushroom at Stove (4 seconds). Interact again with empty hands to retrieve the processed ingredient. Place the ingredients on Assembly one at a time. A complete recipe becomes a plated dish on the counter. Press E with empty hands to pick it up, then take it to Serve while a matching order is active. Trash can discard unwanted carried items; R at Assembly clears incomplete ingredients. Each round starts with three clean plates. Completing a dish consumes one; serving it sends a dirty plate to Return after 3 seconds of gameplay. Pick it up there, wash it at Sink for 3 seconds, pick it up again, and return it to either Assembly counter or Return to replenish the shared clean supply. Discarding an unserved plated dish returns its plate clean to storage. If no plate is available, the final ingredient remains in your hands until a clean plate is returned.

Recipes:

- **Burger:** raw bun + cooked patty.
- **Salad:** chopped lettuce + chopped tomato.
- **Soup:** cooked tomato + cooked mushroom.

Each correct order earns 100 points; each expired order costs 20 points. There can be up to three active orders. Each round lasts 120 seconds. Reach 100 points in Level 1 to unlock Level 2; Level 2 has faster orders and shorter deadlines, with a 200-point target. Score resets each round. A round ends when its overall timer expires, and the result is saved then. Closing the game mid-round does not save that round. Plate inventory and pending returns reset at the start of each round.

Recipe definitions and level settings live in `data/recipes.json` and `data/levels.json`. Station positions and pedestrian paths are in `src/layout.py`; station behavior is in `src/station.py`, pedestrian movement in `src/pedestrian.py`, and placeholder drawing in `src/rendering.py`. Pedestrians travel vertically along the crosswalk and block the chef; they wait when blocked and resume when their path clears. Ingredient processing rules are in `src/station.py`, so adding a recipe requiring a new preparation method also requires updating those rules.

## Saved profiles

Profiles are stored in `data/players.db`, created automatically and excluded from Git. The game remembers each username's best round score, highest unlocked level, and number of completed rounds. Lower scores or levels never overwrite higher ones. The database is local to this project folder; profiles do not sync between computers. SQLite storage is isolated in `src/save_manager.py` for a future browser-compatible replacement. Back up the database if moving the project and keeping profiles matters.

## Testing

```bash
python3 -m unittest discover -s tests -v
```

The tests cover core recipe, station, order, profile, round, and collision logic. Also play through both levels manually to assess navigation, readability, and difficulty.

## Project team

Pandas Express: Thy Tran and Alisha Pol. Gameplay uses placeholders ready for Alisha's artwork, animations, sounds, and visual design. Browser packaging and online hosting are not implemented.
