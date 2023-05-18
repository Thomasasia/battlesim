help = {}
help["turn"]="""turn : t or turn / performs turns of normal combat. this is the default command when pressing enter without input.
\t(optional)count : number of turns to do, default 1"""
help["kill"]="""kill random soldiers : kill or k / kills soldiers at random
\tkills : number of kills. -1 kills everything
\tarmy : army to kill from
\t(optional)regiment : regiment name or number to kill from. default is randomly
\t(optional)rank : rank number to kill from. default is randomly"""
help["range_toggle"]="""range_toggle : range or r / toggles the abiltiy of the regiment or army to engage in ranged combat
\t(optional)toggle : 0 for false, 1 for true. without this, both armies will have their flag flipped
\t(optional)army : name or number of the army to modify. without this, both will be modified
\t(optionalregiment : name or number of the regiment to apply the range flag to, in case you dont want to stop the entire army but just part of it."""
help["morale_change"]="""morale_change : morale or m / changes the morale of the specified regiment
\tarmy : name or number of the army
\tregiment : name or number of the regiment
\tmorale : how much to change the morale by. can be positive or negative."""
help["change_ranks"]="""change_ranks : cr or ranks / changes the number of ranks that a regiment is divided into.
\tarmy : army name or number
\tregiment : regiment name or number to change
\tranks : new number of ranks. must be greater than zero."""
help["kss"]="""kss : kss / kills soldiers of a specific type
\t soldier name : name of the type of soldier to kill
\t kills : number of soldiers to kill. -1 kills all
\t army : army name or number to kill from
\t(optional) regiment : regiment name or number to kill from. without this, it will be distributed across the whole army
\t(optional) rank number : the rank in the regiment to kill from. if this is unset, it will be distributed across the regiment / army"""
help["add"]="""add_soldiers : add / adds soldiers of a certain type to a regiment
\tnumber : number of soldiers to add
\tsoldier type : name of the soldier template from the soldier library
\tarmy : name or number of the army to add the soldiers to
\tregiment : name or number of the regiment to add the soldiers to"""
help["advantage"]="""battle_advantage : adv or advantage / gives a one turn battle (dis)advantage to the chosen army
\tarmy name : army name or number to apply advantage to
\tadvantage : float value from 0.0 to 100.0 for combat advantage"""
help["swap"]="""swap : swap / swaps the places of two regiments in an army
\tarmy name : army name or number
\tregiment 1 : name or number of the first regiment
\tregiment 2 : name or number of the second regiment"""
help["assault"]="""assault : ass or assault / performs special melee combat between the two regiments
\tregiment 1 : the name or number of the regiment in the first army to fight
\tregiment 2 : the name or number of the regiment in the second army to fight"""
help["display_troops"]="""display_troops : troops / prints a list of all troops in the troop library
\t(optional) army name : the name or number of an army, prints all troops present in that army, with numbers."""
help["display_army"]="""display_army : show / displays one or both armies.
\t(optional) army name : the name or number of the army to display. without this both armies will be displayed. but if done like this, extra information will be displayed."""
help["log"]="""log : log / displays the game log.
\t(optional) Type : the type of log to display, either 'battle' 'b' or 'message' 'm'. default 'message'
\t(optional) Age : how many turns back you want the log to go. 1 is the current turn, 2 is the previous turn. default 2"""
help["verbose"]="Toggle verbose : verbose / toggles the verbose setting, to avoid printing the armies and showing the log after each command"
help["help"]="Help : h or help / Tells you about a command \n\t(optional) Command : command to ask about, ie kill"
help["exit"]="exit : type exit to quit"
