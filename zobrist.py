import random as rand

indices={
    'P':1,
    'R':2,
    'N':3,
    'B':4,
    'Q':5,
    'K':6,
    'p':7,
    'r':8,
    'n':9,
    'b':10,
    'q':11,
    'k':12}
table=[] #12x64

def random_bitstring():
    return rand.randint(0,2**32-1)

black_to_move=random_bitstring()

def init_zobrist():
    # fill a table of random numbers/bitstrings
    for i in range(64):
        table.append([])  # loop over the board, represented as a linear array
        for j in indices:      # loop over the pieces
            table[i].append(random_bitstring())

def hash(board_state):
    h = 0
    board=board_state.split()[0].replace("/", "")
    if board_state.split()[1]=="b":
        h = h^black_to_move
    
    i=0
    v=0
    limit=64
    while v<limit:      # loop over the board positions
        if board[v].isdigit():
            limit-=int(board[v])
            i+=int(board[v])
        else:
            j = indices[board[v]]
            h = h^table[i][j-1]
        v+=1
        i+=1
    return h


init_zobrist()