## Timings
N.B.  
Logging takes about .03s  
You can check timings by settings timings=true in the config.  
Make sure to turn off all other repetitive logs.

### cpu, serial
MCTNode __init__
* full game ~ 48s
* game.copy ~ .001s
* expand ~ .135
* backup ~ 0

### gpu, serial
* full game ~ 84s
* expand ~ .039s
* pre-expand ~1.8s

## Why?
I don't really know
Expand is much faster on GPU.  
First expand is s bit slower on GPU.  
However, a full search takes about the same amount of time?

### Questions
1. Why does a full search take the same time GPU vs CPU, even though each expand is much faster on GPU?
2. Why does GPU search take so much longer near the end of the game?
3. Why are GPU searches so variable? (I've seen 11.6s for a search, 74s for the next search)

GPU  
Search iteration time: 0.0
Search iteration time: 0.0
Search iteration time: 0.08901786804199219
Search iteration time: 0.09002113342285156
Search iteration time: 0.09001922607421875
Search iteration time: 0.09102249145507812
Search iteration time: 0.0910186767578125
Search iteration time: 0.09302091598510742
Search iteration time: 0.09102058410644531
Search iteration time: 0.09002017974853516
Search iteration time: 0.09302306175231934
Search iteration time: 0.09201931953430176
Search iteration time: 0.09102082252502441
Search iteration time: 0.09102201461791992
Search iteration time: 0.0910184383392334
Search iteration time: 0.09302186965942383


CPU  