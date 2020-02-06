# TODO

### Update ZeroBot
* Increase parallelism (extra process(es) during MCTS)
  * Investigate memory requirements
* Convert float -> int where possible. Are ints faster/more efficient?
* Investigate batching samples
* Investigate changes to hyperparameters (basically everything in config)
   * Investigate game length as a function of victory_points_to_win
   * Investigate learning rate. Should it be higher? Start higher?
* Investigate loss function
  * Is it correct?
* Add Dirichlet noise to action selection
* Add ability to learn from playing against (or with) a human
* Refactor get_legal_action_ids
    * Where should this live? Perhaps give it to the model.choose_action?
    * Preferably compute exactly once per turn

### Update Game
* Make random board possible
  * would need to update board.copy()

### Update Human player
* Allow human move selection in the choose_action paradigm
* Human is probably broken atm. I haven' tested it in a while