# TODO

### Update ZeroBot
* Increase parallelism (extra process(es) during MCTS)
  * Investigate memory requirements
* Investigate batching samples
* Investigate changes to hyperparameters (basically everything in config)
   * Investigate game length as a function of victory_points_to_win
   * Investigate learning rate. Should it be higher? Start higher?
* Add Dirichlet noise to action selection
* Refactor get_legal_action_ids
    * Where should this live? Perhaps give it to the model.choose_action?
    * Preferably compute exactly once per turn

### Update Game
* Make random board possible
  * would need to update board.copy()

### Update Human player
* Allow trading. It's in the game, there's just no button for it.