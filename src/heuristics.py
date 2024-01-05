from game import Game

#Value functions for preferred board positions of certain pieces.
#Retrieved from https://www.chessprogramming.org/Simplified_Evaluation_Function
#


boardPriority = {
"p":[  0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5,  5, 10, 25, 25, 10,  5,  5,
            0,  0,  0, 20, 20,  0,  0,  0,
            5, -5,-10,  0,  0,-10, -5,  5,
            5, 10, 10,-20,-20, 10, 10,  5,
            0,  0,  0,  0,  0,  0,  0,  0],

'n':[-50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50,],

'b':[-20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
              0, 10, 10, 10, 10, 10, 10,  0,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20,],

'r':[ 0,  0,  0,  0,  0,  0,  0,  0,
             5, 10, 10, 10, 10, 10, 10,  5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
             0,  0,  0,  5,  5,  0,  0,  0],

'q':[-20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5,  5,  5,  5,  0,-10,
             -5,  0,  5,  5,  5,  5,  0, -5,
              0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20],

#Early game values
'k1':[-30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -10,-20,-20,-20,-20,-20,-20,-10,
             20, 20,  0,  0,  0,  0, 20, 20,
             20, 30, 10,  0,  0, 10, 30, 20],

#Late game values
'k2':[-50,-40,-30,-20,-20,-30,-40,-50,
            -30,-20,-10,  0,  0,-10,-20,-30,
            -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30,
            -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-30,  0,  0,  0,  0,-30,-30,
            -50,-30,-30,-30,-30,-30,-30,-50]}


def material(board_state, weight):
    piece_values = {'p': 1, 'b': 3, 'n': 3, 'r': 5, 'q': 9, 'k': 0}
    black_points = 0
    board_state = board_state.split()[0]
    for piece in board_state:
        if piece.islower():
            black_points += piece_values[piece]
        elif piece.isupper():
            black_points -= piece_values[piece.lower()]
    return black_points * weight

def piece_moves(game, weight):
    black_points = 0
    turn = str(game).split()[1]
    square_values = {"e4": 1, "e5": 1, "d4": 1, "d5": 1, "c6": 0.5, "d6": 0.5, "e6": 0.5, "f6": 0.5,
                    "c3": 0.5, "d3": 0.5, "e3": 0.5, "f3": 0.5, "c4": 0.5, "c5": 0.5, "f4": 0.5, "f5": 0.5}
    possible_moves = game.get_moves()
    for move in possible_moves:
        if turn == "b":
            if move[2:4] in square_values:
                black_points += square_values[move[2:4]]
        else:
            if move[2:4] in square_values:
                black_points -= square_values[move[2:4]]
    return black_points

def structure(board_state,weight):
    piece_values = {'p': 3, 'b': 4, 'n': 4, 'r': 3, 'q': 4, 'k': 1}
    normalPieces=['p','b','n','r','q']
    blackKingdex=0
    whiteKingdex=0
    score=0
    blackPieces=0
    whitePieces=0
    tempKingValue=15
    board=board_state.split()[0].replace("/","")
    
    #Iterates over the board to find piece positions
    boardIndex=0
    priorityIndex=0
    limit=64
    while boardIndex < limit:
        piece=board[boardIndex]
        lowPiece = piece.lower()
        if piece.isdigit():
            limit-=int(piece)
            priorityIndex+=int(piece)
        if piece=='k':
            blackKingdex=priorityIndex
        elif piece=='K':
            whiteKingdex=priorityIndex
        elif lowPiece in normalPieces:
            if piece.islower():
                blackPieces+=1
                score+=boardPriority[lowPiece][63-priorityIndex]*piece_values[lowPiece]   
            else:
                whitePieces+=1
                score-=boardPriority[lowPiece][priorityIndex]*piece_values[lowPiece]
        boardIndex+=1
        priorityIndex+=1
                
    if blackPieces>8:
        score+=boardPriority['k1'][63-blackKingdex]*tempKingValue
    else:
        score+=boardPriority['k2'][63-blackKingdex]*tempKingValue
    if whitePieces>8:
        score-=boardPriority['k1'][whiteKingdex]*tempKingValue
    else:
        score-=boardPriority['k2'][whiteKingdex]*tempKingValue
    return score*weight

        

def in_check(game, weight):
    black_points = 0
    current_status = game.status
    # Turn should be 'w' or 'b'
    turn = str(game).split(" ")[1]
    # Check or Checkmate situations
    if turn == "w":
        if current_status == 1:
            black_points += 1 * weight
        elif current_status == 2:
            black_points += float("inf")
    else:
        if current_status == 1:
            black_points -= 1 * weight
        elif current_status == 2:
            black_points += float("-inf")
    return black_points