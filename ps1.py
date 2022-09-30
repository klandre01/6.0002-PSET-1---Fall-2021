################################################################################
# 6.0002 Fall 2021
# Problem Set 1
# Name: Karen Andre
# Collaborators: Angelica Whipple
# Time: 10 hours

from state import State

##########################################################################################################
## Problem 1
##########################################################################################################

def load_election(filename):
    """
    Reads the contents of a file, with data given in the following tab-separated format:
    State[tab]Democrat_votes[tab]Republican_votes[tab]EC_votes

    Please ignore the first line of the file, which are the column headers, and remember that
    the special character for tab is '\t'

    Parameters:
    filename - the name of the data file as a string

    Returns:
    a list of State instances
    """
    # TODO
    file = open(filename, 'r')
    lines = file.readlines()
    states = []
    for i in range(1, len(lines)):
        attr = lines[i].split('\t') # list of attributes for State
        states.append(State(attr[0], attr[1], attr[2], attr[3]))
    return states
    


##########################################################################################################
## Problem 2: Helper functions
##########################################################################################################

def election_winner(election):
    """
    Finds the winner of the election based on who has the most amount of EC votes.
    Note: In this simplified representation, all of EC votes from a state go
    to the party with the majority vote.

    Parameters:
    election - a list of State instances

    Returns:
    a tuple, (winner, loser) of the election i.e. ('dem', 'rep') if Democrats won, else ('rep', 'dem')
    """
    # TODO
    dem_votes, rep_votes = 0, 0
    for state in election:
        votes = state.get_ecvotes()
        if state.get_winner() == "dem":
            dem_votes += votes
        else:
            rep_votes += votes
    if dem_votes > rep_votes:
        return ("dem", "rep")
    return ("rep", "dem")


def winner_states(election):
    """
    Finds the list of States that were won by the winning candidate (lost by the losing candidate).

    Parameters:
    election - a list of State instances

    Returns:
    A list of State instances won by the winning candidate
    """
    # TODO
    states = []
    winner = election_winner(election)[0]
    for state in election:
        if state.get_winner() == winner:
            states.append(state)
    return states


def ec_votes_to_flip(election, total=538):
    """
    Finds the number of additional EC votes required by the loser to change election outcome.
    Note: A party wins when they earn half the total number of EC votes plus 1.

    Parameters:
    election - a list of State instances
    total - total possible number of EC votes

    Returns:
    int, number of additional EC votes required by the loser to change the election outcome
    """
    # TODO
    vote_majority = total/2 + 1
    loser_votes = 0
    loser = election_winner(election)[1]
    for state in election:
        if state.get_winner() == loser:
            loser_votes += state.get_ecvotes()
    return int(vote_majority - loser_votes)



##########################################################################################################
## Problem 3: Brute Force approach
##########################################################################################################

def combinations(L):
    """
    Helper function to generate powerset of all possible combinations
    of items in input list L. E.g., if
    L is [1, 2] it will return a list with elements
    [], [1], [2], and [1,2].

    Parameters:
    L - list of items

    Returns:
    a list of lists that contains all possible
    combinations of the elements of L
    """

    def get_binary_representation(n, num_digits):
        """
        Inner function to get a binary representation of items to add to a subset,
        which combinations() uses to construct and append another item to the powerset.

        Parameters:
        n and num_digits are non-negative ints

        Returns:
            a num_digits str that is a binary representation of n
        """
        result = ''
        while n > 0:
            result = str(n%2) + result
            n = n//2
        if len(result) > num_digits:
            raise ValueError('not enough digits')
        for i in range(num_digits - len(result)):
            result = '0' + result
        return result

    powerset = []
    for i in range(0, 2**len(L)):
        binStr = get_binary_representation(i, len(L))
        subset = []
        for j in range(len(L)):
            if binStr[j] == '1':
                subset.append(L[j])
        powerset.append(subset)
    return powerset

def brute_force_swing_states(winner_states, ec_votes):
    """
    Finds a subset of winner_states that would change an election outcome if
    voters moved into those states, these are our swing states. Iterate over
    all possible move combinations using the helper function combinations(L).
    Return the move combination that minimises the number of voters moved. If
    there exists more than one combination that minimises this, return any one of them.

    Parameters:
    winner_states - a list of State instances that were won by the winner
    ec_votes - int, number of EC votes needed to change the election outcome

    Returns:
    A list of State instances such that the election outcome would change if additional
    voters relocated to those states
    The empty list, if no possible swing states
    """
    # TODO
    best_combo = None
    min_voters = None
    possible_move_combinations = combinations(winner_states)
    for combo in possible_move_combinations:
        moved_voters = 0    # represents how many voters had to move
        ec_flip = 0 # represents flipped electoral college votes
        for item in combo:
            moved_voters += item.get_margin() + 1
            ec_flip += item.get_ecvotes()
        if (ec_flip >= ec_votes) and (min_voters == None or moved_voters < min_voters):
            best_combo = combo
            min_voters = moved_voters
    if best_combo == None:
        return []
    return best_combo



##########################################################################################################
## Problem 4: Dynamic Programming
## In this section we will define two functions, move_max_voters and move_min_voters, that
## together will provide a dynamic programming approach to find swing states. This problem
## is analagous to the complementary knapsack problem, you might find Lecture 1 of 6.0002 useful
## for this section of the pset.
##########################################################################################################

def find_max_voters(winner_states, max_votes, memo = None):
    """
    Helper function for move_max_voters. Will find the maximum voters moved without exceeding max_votes.
    winner_states: the states in which the winning candidate won electoral votes. These are the states being considered
    max_votes: max number of electoral votes
    """
    if memo is None:
        memo = {}
    if (len(winner_states), max_votes) in memo: # if this scenario has already been encountered
        result = memo[(len(winner_states), max_votes)]
    elif winner_states == [] or max_votes == 0: # if there are no states to make combos out of or no room in knapsack
        result = (0, [])
    elif winner_states[0].get_ecvotes() > max_votes: # next state doesn't fit in knapsack
        result = find_max_voters(winner_states[1:], max_votes, memo)
    else:
        state = winner_states[0]
        # if we choose to flip this state
        voters_flipped, flipped = find_max_voters(winner_states[1:], max_votes - state.get_ecvotes(), memo)
        voters_flipped += (state.get_margin() + 1)
        # if we choose not to flip this state
        not_voters_flipped, not_flipped = find_max_voters(winner_states[1:], max_votes, memo)
        # comparing choice to flip state vs. not
        if voters_flipped > not_voters_flipped:
            result = (voters_flipped, flipped + [state])
        else:
            result = (not_voters_flipped, not_flipped)
    memo[(len(winner_states), max_votes)] = result  # so we don't repeat these steps for the same scenario
    return result

def move_max_voters(winner_states, ec_votes):
    """
    Finds the largest number of voters needed to relocate to get at most ec_votes
    for the election loser.

    Analogy to the knapsack problem:
        Given a list of states each with a weight(ec_votes) and value(margin+1),
        determine the states to include in a collection so the total weight(ec_votes)
        is less than or equal to the given limit(ec_votes) and the total value(voters displaced)
        is as large as possible.

    Parameters:
    winner_states - a list of State instances that were won by the winner
    ec_votes - int, the maximum number of EC votes

    Returns:
    A list of State instances such that the maximum number of voters need to be relocated
    to these states in order to get at most ec_votes
    The empty list, if every state has a # EC votes greater than ec_votes
    """
    # TODO
    num_voters, flipped_states = find_max_voters(winner_states, ec_votes)
    return flipped_states



def move_min_voters(winner_states, ec_votes_needed):
    """
    Finds a subset of winner_states that would change an election outcome if
    voters moved into those states. Should minimize the number of voters being relocated.
    Only return states that were originally won by the winner (lost by the loser)
    of the election.

    Hint: This problem is simply the complement of move_max_voters. You should call
    move_max_voters with ec_votes set to (#ec votes won by original winner - ec_votes_needed)

    Parameters:
    winner_states - a list of State instances that were won by the winner
    ec_votes_needed - int, number of EC votes needed to change the election outcome

    Returns:
    A list of State instances such that the election outcome would change if additional
    voters relocated to those states (also can be referred to as our swing states)
    The empty list, if no possible swing states
    """
    # TODO
    ec_votes_won = 0
    for state in winner_states:
        ec_votes_won += state.get_ecvotes()
    non_swing_states = move_max_voters(winner_states, ec_votes_won - ec_votes_needed)
    # [expr for elem in iterable if test]
    swing_states = [item for item in winner_states if item not in non_swing_states]
    return swing_states


##########################################################################################################
## Problem 5
##########################################################################################################

def relocate_voters(election, swing_states, states_with_pride = ['AL', 'AZ', 'CA', 'TX']):
    """
    Finds a way to shuffle voters in order to flip an election outcome. Moves voters
    from states that were won by the losing candidate (states not in winner_states), to
    each of the states in swing_states. To win a swing state, you must move (margin + 1)
    new voters into that state. Any state that voters are moved from should still be won
    by the loser even after voters are moved. Also finds the number of EC votes gained by
    this rearrangement, as well as the minimum number of voters that need to be moved.
    Note: You cannot move voters out of Alabama, Arizona, California, or Texas.

    Parameters:
    election - a list of State instances representing the election
    swing_states - a list of State instances where people need to move to flip the election outcome
                   (result of move_min_voters or greedy_swing_states)
    states_with_pride - a list of Strings holding the names of states where residents cannot be moved from
                    (default states are AL, AZ, CA, TX)

    Return:
    A tuple that has 3 elements in the following order:
        - an int, the total number of voters moved
        - a dictionary with the following (key, value) mapping:
            - Key: a 2 element tuple of str, (from_state, to_state), the 2 letter State names
            - Value: int, number of people that are being moved
        - an int, the total number of EC votes gained by moving the voters
    None, if it is not possible to sway the election
    """
    # TODO
    winner = election_winner(election)[0]
    winning_states = winner_states(election)
    losing_states = [i for i in election if i not in winning_states]
    losing_candidate_states = [state for state in losing_states if state.get_name() not in states_with_pride]
    # how many voters we need to move
    need_to_move = 0
    for state in swing_states:
        need_to_move += (state.get_margin() + 1)
    # voters that can move
    can_move = 0
    for losing_state in losing_candidate_states:
        can_move += (losing_state.get_margin() - 1)
    if need_to_move > can_move:
        return None
    # moving voters
    num_voters_moved = 0
    state_mapping = {}
    ec_vote_gain = 0
    for win_state in swing_states:
        for lose_state in losing_candidate_states:
            if win_state.get_winner() != winner: # successfully flipped the state, move to next one
                ec_vote_gain += win_state.get_ecvotes()
                break
            if not (lose_state > win_state): # losing state has smaller or equal margin
                moving_votes = (lose_state.get_margin() - 1) # still need losing state to win
            else: # losing state has larger margin
                moving_votes = (win_state.get_margin() + 1) # flip the winning state
            # perform the move
            lose_state.subtract_winning_candidate_voters(moving_votes)
            win_state.add_losing_candidate_voters(moving_votes)
            num_voters_moved += moving_votes
            state_mapping[(lose_state.get_name(), win_state.get_name())] = moving_votes
    return (num_voters_moved, state_mapping, ec_vote_gain)





if __name__ == "__main__":
    pass
    # Uncomment the following lines to test each of the problems

    # # tests Problem 1
    # year = 2012
    # election = load_election("%s_results.txt" % year)
    # print(len(election))
    # print(election[0])

    # # tests Problem 2
    # winner, loser = election_winner(election)
    # won_states = winner_states(election)
    # names_won_states = [state.get_name() for state in won_states]
    # reqd_ec_votes = ec_votes_to_flip(election)
    # print("Winner:", winner, "\nLoser:", loser)
    # print("States won by the winner: ", names_won_states)
    # print("EC votes needed:",reqd_ec_votes, "\n")

    # # tests Problem 3
    # brute_election = load_election("60002_results.txt")
    # brute_won_states = winner_states(brute_election)
    # brute_ec_votes_to_flip = ec_votes_to_flip(brute_election, total=14)
    # brute_swing = brute_force_swing_states(brute_won_states, brute_ec_votes_to_flip)
    # names_brute_swing = [state.get_name() for state in brute_swing]
    # voters_brute = sum([state.get_margin()+1 for state in brute_swing])
    # ecvotes_brute = sum([state.get_ecvotes() for state in brute_swing])
    # print("Brute force swing states results:", names_brute_swing)
    # print("Brute force voters displaced:", voters_brute, "for a total of", ecvotes_brute, "Electoral College votes.\n")

    # # tests Problem 4: move_max_voters
    # print("move_max_voters")
    # total_lost = sum(state.get_ecvotes() for state in won_states)
    # non_swing_states = move_max_voters(won_states, total_lost-reqd_ec_votes)
    # non_swing_states_names = [state.get_name() for state in non_swing_states]
    # max_voters_displaced = sum([state.get_margin()+1 for state in non_swing_states])
    # max_ec_votes = sum([state.get_ecvotes() for state in non_swing_states])
    # print("States with the largest margins (non-swing states):", non_swing_states_names)
    # print("Max voters displaced:", max_voters_displaced, "for a total of", max_ec_votes, "Electoral College votes.", "\n")

    # # tests Problem 4: move_min_voters
    # print("move_min_voters")
    # swing_states = move_min_voters(won_states, reqd_ec_votes)
    # swing_state_names = [state.get_name() for state in swing_states]
    # min_voters_displaced = sum([state.get_margin()+1 for state in swing_states])
    # swing_ec_votes = sum([state.get_ecvotes() for state in swing_states])
    # print("Complementary knapsack swing states results:", swing_state_names)
    # print("Min voters displaced:", min_voters_displaced, "for a total of", swing_ec_votes, "Electoral College votes. \n")

    # # tests Problem 5: relocate_voters
    # print("relocate_voters")
    # flipped_election = relocate_voters(election, swing_states)
    # print("Flip election mapping:", flipped_election)