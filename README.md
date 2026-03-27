# Blood on the Clocktower Discord Bot

## Description
This project runs a Blood on the Clocktower–style game in Discord. It models players, roles, alignments, and status effects, such as being drunk, poisoned, or protected. The bot automatically schedules night actions, conducts day execution votes, and sends direct messages (DMs) to players with their private information.

## Features
* **Automated Game Loop**: The bot schedules night actions, conducts day execution votes, and handles sending DMs with private information to players.
* **Role Behaviors**: The engine encodes per-role behaviors, such as the Imp kill, Poisoner poison, and Monk protect. It also includes Game Master (GM) override hooks that allow a storyteller to replace automated outcomes.
* **Discord UI Integration**: It provides Discord UI components for lobby management, seat ordering, GM selection, execution polls, and DM-based dropdowns and polls.
* **Encounters Subsystem**: The project includes an encounters subsystem meant for side events or narrative beats. This system features a registry, a dependency graph, and a deck of encounter cards.

## Architecture & Core Modules
* **Domain Model**: Core game enums and a mutable status container are centralized in `botc/enums.py`. The Player entity is defined in `botc/player.py`.
* **Role Behavior System**: Abstract role behaviors are defined in `botc/behaviors/base.py`. Concrete role implementations for Townsfolk, Demons, Minions, and Outsiders are eagerly imported to populate a global registry.
* **Game Orchestration**: The `GameManager` acts as the central orchestrator. It composes a PlayerManager, DayManager, NightManager, DiscordManager, and EventManager.
* **Discord Integration**: A BotManager handles Discord intents, cog loading, and guild-scoped app-command syncing. Admin slash commands are provided for lobby setup, seat ordering, and GM selection.
* **Polling System**: A PollManager handles GM volunteer polls using Discord's native Poll feature. It also manages day execution votes using a custom dropdown view.

## Setup & Configuration
* **Environment Variables**: The project requires a `.env` file containing `DISCORD_TOKEN` and `SERVER_ID`. The `SERVER_ID` is used to select the test guild for application command syncing.
* **Permissions**: The bot relies on `discord.py` 2.x and requires privileged intents for `message_content` and `members`.

## Usage & Commands
* **Lobby Management**: Admin slash commands include `open_lobby` to reset the lobby state and post a join view, and `start_game` to close the lobby and begin the game.
* **Seat Ordering**: The `set_seats` command allows locking the seating order based on mentioned users.
* **Player Interactions**: Players make selections through direct messages, receiving either Discord UI dropdowns or native Discord Polls depending on the number of options.

## Future Improvements
* **Identity Management**: The bot currently relies heavily on username or global_name string matching. A planned improvement is migrating to Discord user IDs for joining, routing, and voting to improve safety and avoid issues with non-unique names.
