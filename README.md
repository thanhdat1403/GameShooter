# GameShooter

A 2D shooter game developed with Python and Pygame.

## Overview

GameShooter is a 2D shooter project featuring player movement, enemy AI, shooting mechanics, multiple levels, projectiles, grenades, mines, explosions, items, health management, animations, and level progression.

The game uses CSV files to store level data and includes separate audio and image assets for the gameplay experience.

## Features

- 2D shooter gameplay
- Player movement and shooting
- Enemy AI
- Health and damage system
- Ammunition and grenades
- Mines and explosions
- Item pickups
- Character animations
- Multiple levels
- Level progression
- CSV-based level data
- Sound effects and background music
- Sprite-based graphics

## Controls

| Key | Action |
|---|---|
| A | Move left |
| D | Move right |
| Space | Shoot |
| Q | Grenade |
| W | Jump |
| M | Mine |
| ESC | Exit |

## Levels

The game currently contains three level data files:

- `level1_data.csv`
- `level2_data.csv`
- `level3_data.csv`

After completing a level, the game loads the next level automatically.

## Technologies

- Python
- Pygame
- CSV
- Object-oriented programming

## Project Structure

```text
GameShooter/
+-- audio/
+-- img/
+-- level1_data.csv
+-- level2_data.csv
+-- level3_data.csv
+-- button.py
+-- shooter_tut1.py
+-- requirements.txt
+-- LICENSE
+-- README.md