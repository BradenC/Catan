# Catan

Have you ever lost so many games of Settlers of Catan that you wanted to play against an opponent that knows nothing?
This program offers exactly that as an alternative to finding Jon Snow.
Be careful though - play it too long and it will learn.

## Learning Algorithm

### Structure
This agent is based off of AlphaZero.  
At a high level, the agent alternates between two modes - example generating and comparison

During example generation, the bot plays against itself and records the decisions made along the way.
After the game concludes, it updates those decision records with the final result of the game.
The decisions and results combine to become training samples and training targets to be fed into the CNN.

During comparison mode, (vs mode in this code) two bots are used.  
One bot has the most up-to-date version of the CNN. The other bot uses a previous version.
If the newer bot wins >=55% of the games, it is saved. Otherwise, the changes are reverted.

For more details, see [DeepMind's original AlphaZero work](https://arxiv.org/abs/1712.01815)

## Config

All configurable items can be found in `Catan/catan/config.json`