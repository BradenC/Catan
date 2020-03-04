# Catan

Have you ever lost so many games of Settlers of Catan that you wanted to play against an opponent that knows nothing?
This program offers exactly that - no need to find Jon Snow.
Be careful though - play it too long and it will learn.

## Learning Algorithm

### Structure
This agent is based off of AlphaZero.  
At a high level, the agent alternates between two modes
1. Play games to generate data (current model vs current model)
2. Learn from that data (old model := current model. new model:= current model + training)
3. Play a few comparison games (new model vs old model).
4. The winner of the comparison games becomes the current model. Lather, rinse, repeat.

During example generation, the bot plays against itself and records the decisions made along the way.
After the game concludes, it updates those decision records with the final result of the game.
The decisions and results combine to become training samples and training targets to be fed into the CNN.

During comparison mode, (vs mode in this code) bots of two different versions are used.  
One bot has the most up-to-date version of the network. The other bot uses a previous version.
If the newer bot wins >=55% of the games, it is saved. Otherwise, the changes are reverted.

For more details, see [DeepMind's original AlphaZero work](https://arxiv.org/abs/1712.01815)

## Config

Internal configurable items can be found in `Catan/catan/config.json`.  
Some basic configuration can be accessed thru the command line. Try running `python catan --help`

## Setup

This worked for me.
```cmd
conda install pytorch cudatoolkit=10.1 -c pytorch
```
```cmd
cd whichever/directory/this/is/in
activate catan
python catan [--graphics]
```