# BotC Helper
A small Python project that simulates parts of ***Blood on the Clocktower: Trouble Brewing*** night flow for a Storyteller.
* Randomly assign roles based on player count
* Manage key game mechanics
* Walk through **night phases** interactively
* View a Storyteller-style **Grimoire (board state)**

---

## Features

### Role Assignment (Trouble Brewing subset)

Supports **5–15 players** using a distribution table:
* Demons / Minions / Outsiders / Townsfolk

**Role pools:**
* **Demon**: `Imp`
* **Minions**: `Poisoner`, `Spy`, `Baron`, `Scarlet Woman`
* **Outsiders**: `Butler`, `Drunk`, `Recluse`, `Saint`
* **Townsfolk**:
  `Washerwoman`, `Librarian`, `Investigator`, `Chef`, `Empath`,
  `Fortune Teller`, `Undertaker`, `Monk`, `Ravenkeeper`,
  `Virgin`, `Slayer`, `Soldier`, `Mayor`

---

### Implemented Mechanics

* **Drunk**
  * Assigned a fake Townsfolk role via `believed_role`
  * Acts as if they are that role
* **Spy**
  * Can *misregister* as a random Good role/alignment
  * Has access to the full board state
* **Poisoner**
  * Poisons one player per night (resets nightly)
* **Monk**
  * Protects one player per night (resets nightly)
* **Imp**
  * Selects a player to kill
  * Protected players survive
* **Scarlet Woman**
  * Becomes the Imp if the Imp dies and **5+ players remain**
* **Empath**
  * Automatically counts Evil neighbors
  * Returns incorrect info if **poisoned** or actually the **Drunk**
* **Grimoire Output**
  * `GameMgr.print_board()` shows full Storyteller view

---

## Unimplemented / In Progress

```
Legend:
[ ] Not started
[-] Partial
[x] Complete
[!] Bug / incorrect behavior
```

### Core Systems
* [ ] Game Master interface for overriding info (poison/drunk corrections)
* [ ] Persistent game state (save/load)
  * [ ] Editable raw state file
  * [ ] Reload game from file
* [ ] Separate logs:
  * [ ] Storyteller view
  * [ ] Player-facing info

### Gameplay
* [ ] Day phase (discussion → nominations → execution)
* [ ] Execution tracking + Undertaker integration
* [ ] Win conditions (e.g., Good wins if Demon dies)

### Roles & Logic
* [ ] Chef implementation
* [ ] Washerwoman / Librarian / Investigator token logic
* [ ] Recluse misregistration
* [ ] Full poison/drunk interaction system
* [ ] Special abilities:
  * Recluse, Saint, Virgin, Slayer, Soldier, Mayor

---

## Requirements
Uses **[uv](https://github.com/astral-sh/uv)** for dependency management.
Install `uv` (On macOS and Linux.)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Sync Dependencies
```bash
uv sync
source .venv/bin/activate
```

---

## Quick Start
```bash
python main.py
```
You’ll see:
* Initial seating + roles (Storyteller view)
* Night 1 prompts and results
* Grimoire output
* Night 2 progression
* Updated Grimoire

### Run Tests
```bash
PYTHONPATH=src pytest -v
```

---

## Grimoire / Board Output
Call:
```python
game.print_board()
```

### Example
```
Seat 01 | Alice   | Alive | Empath (Good)
Seat 02 | Bob     | DEAD  | Drunk (Thinks: Fortune Teller) [POISONED]
Seat 03 | Charlie | Alive | Spy (Registers: Washerwoman/Good)
```

#### Legend
* **True role** → `Role.name_role`
* **Drunk belief** → `Drunk (Thinks: X)`
* **Spy registration** → `Spy (Registers: role/alignment)`
* **Status flags**:
  * `[POISONED]`
  * `[PROTECTED]`
  * `DEAD`

---

## Project Structure
### Core Components
* **`RoleDistributor`**
  * Determines role counts based on player count

* **`Role`**
  * Represents a player
  * Handles night actions via `Action()`

* **`GameMgr`**
  * Owns game state and flow
  * Runs night phases and tracks effects

---

### Key State Fields
* `Role.name_role` → **true role**
* `Role.believed_role` → player’s perceived role (Drunk)
* `Role.registered_role` / `registered_alignment` → seen by info roles
* `Role.alive` → alive/dead state
* `Role.poisoned` → poisoned status
* `Role.protected` → Monk protection
* `GameMgr.killed_tonight` → tracks nightly deaths
