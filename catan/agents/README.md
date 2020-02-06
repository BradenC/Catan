# Catan Bot Model

## Game State Tensor Representation

The game state is represented by a 22x15x22 tensor

#### Layers 0-5 represent the board
The value stored represents the relative chance that hex gets rolled

* [:][:][0] is for wood
* [:][:][1] is for brick
* [:][:][2] is for grain
* [:][:][3] is for sheep
* [:][:][4] is for ore
* [:][:][5] is for desert

#### Layers 6-11 are binary representations of players' pieces
The value is 1 if a player has that piece here, 0 otherwise

* [:][:][6] is for the current player's roads
* [:][:][7] is for the current player's settlements
* [:][:][8] is for the current player's cities

* [:][:][9]  is for the opponent's roads
* [:][:][10] is for the opponent's settlements
* [:][:][11] is for the opponent's cities

#### Layers 12-21 represent the cards held by each player
##### TODO
Entire layer contains the same natural number

* [:][:][12] is for the current player's wood
* [:][:][13] is for the current player's brick
* [:][:][14] is for the current player's grain
* [:][:][15] is for the current player's sheep
* [:][:][16] is for the current player's ore

* [:][:][17] is for the opponent's wood
* [:][:][18] is for the opponent's brick
* [:][:][19] is for the opponent's grain
* [:][:][20] is for the opponent's sheep
* [:][:][21] is for the opponent's ore