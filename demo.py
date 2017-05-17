import os
import pickle
import random
import matplotlib.pyplot as plt
def convertPreds(yVals):
    y_pred = []

    for i in range(len(yVals)):
        y = yVals[i]
        y = list(y)
        idx = y.index(max(y))
        if idx == 0:
            y_pred.append(3)
        elif idx == 1:
            y_pred.append(1)
        else:
            y_pred.append(0)
    return y_pred

def Kbet(cash, bookiePred, ourRes, ourPred, res, betLimit):
   
    ourPred = ourPred.tolist()
    loc = ourPred.index(max(ourPred))
    bPred = bookiePred[:3]
    newCash = cash
    payout = 1/(bPred[loc]) - 1
    scale = 1/10
    if bookiePred[0] != -1:
        if max(ourPred) - bPred[loc] > 0:
            bAmount =   newCash * ((max(ourPred) * payout - (1 - max(ourPred)) )/ payout) * scale
            ourBet = ourRes
        else:
            bAmount = 0
        ourBet = ourRes
        newCash = newCash - bAmount
        if ourBet == res:
            newCash = newCash + (bAmount * 1/(bPred[loc]))
    return newCash
def bet2(cash, bookiePred, ourRes, ourPred, res, betLimit, k, b):
    
    ourPred = ourPred.tolist()
    loc = ourPred.index(max(ourPred))
    kVal = k[loc]
    bPred = bookiePred[:3]
    newCash = cash
    if bookiePred[0] != -1:
        if max(ourPred) - bPred[loc] > 0:
            bAmount = betLimit * (max(ourPred) - bPred[loc]) * b * kVal
            ourBet = ourRes
        else:
            bAmount = 0
        ourBet = ourRes
        newCash = newCash - bAmount
        if ourBet == res:
            newCash = newCash + (bAmount * 1/(bPred[loc]))
    return newCash

def homeOps(game):
    h = []
    for i in range(5):
        loc = i * 42 + 1
        h.append(game[loc])
    return h
def awayOps(game):
    h = []
    for i in range(5):
        loc = i * 42 + 42 * 5 + 1
        h.append(game[loc])
    return h
def homeScores(game):
    scores = []
    for i in range(5):
        loc = i * 42 + 3
        scores.append((game[loc] * 10, game[loc + 1] * 10 ))
    return scores
def awayScores(game):
    scores = []
    for i in range(5):
        loc = i * 42 + 42 * 5 + 3
        scores.append((game[loc] * 10, game[loc + 1] * 10 ))
    return scores
def averageOppRatingsh(game):
    r = []
    for i in range(5):
        loc = i * 42 + 28
        r.append(sum(game[loc:loc + 11])/11 * 100)
    return r
def averageOppRatingsa(game):
    r = []
    for i in range(5):
        loc = i * 42 + 28 + 42 * 5
        r.append(sum(game[loc:loc + 11])/11 * 100)
    return r
def hRating(game):
    
    loc =   42 * 4 + 17
    r = sum(game[loc:loc + 11])/11 * 100
    return r
def aRating(game):
    loc =  42 * 9 + 17
    r = sum(game[loc:loc + 11])/11 * 100
    return r
def transformX(x):
    
    #home and away locations
    h = x[0]
    a = x[210]
    hopp = homeOps(x)
    aopp = awayOps(x)
    hscores = homeScores(x)
    ascores = awayScores(x)
    hoppR = averageOppRatingsh(x)
    aoppR = averageOppRatingsa(x)
    hR = hRating(x)
    aR = aRating(x)
    ginfo = [h, a, hopp, aopp, hscores, ascores, hoppR, aoppR, hR, aR]
    
    return ginfo


def getBOdd(b, bookie):
    if b == 3:
        return bookie[0]
    if b == 1:
        return bookie[1]
    else:
        return bookie[2]

def placeBet(cash, b, amount, bookie, actual):
    bookieOdd = getBOdd(b, bookie)
    nCash = cash
    nCash -= amount
    if b == actual:
        nCash += 1/(bookieOdd) * amount
    return nCash    


def demoSimText(bookie, preds, results, x):
    k = [32.133890891260116, 1, 7.4192276004841595]
    b = 1
    startCash = 10000
    kCash = 10000
    hCash = startCash
    cashAmounts = []
    kAmounts = []
    hAmounts = []
    n = len(bookie)
    ourResults = convertPreds(preds)
    cash = startCash
    hAmounts.append(startCash)
    cashAmounts.append(cash)
    kAmounts.append(kCash)
    fname = 'demoTeams.csv'
    f = open(fname, 'r')
    teamID = dict()

    for line in f:
        line = line.strip().split(',')
        teamID[int(line[0])] = line[1]
    for i in range(n):
        os.system('cls' if os.name == 'nt' else 'clear')
        game = x[i]
        bookiePred = bookie[i]
        info(game, teamID, bookiePred)
        b = -1
        bAmount = -1
        while b != 0 and b != 1 and b !=3:
            try:
                if b != -1:
                    print('enter a valid argument')
                b = int(input('Enter your predicted outcome: 3 for home win, 1 for tie, 0 for home loss: '))
            except:
                print('please use a valid input argument')
        print()
        while bAmount < 0 or bAmount > hCash:
            try:
                if bAmount > hCash:
                    print('you need more money to place that bet')
                    print()
                amountStr = 'put amount to wager max ' + str(hCash) +'$:'
                bAmount = float(input(amountStr))
            except:
                 print('please use a valid input argument')  
        
        ourPred = preds[i]
        ourRes = ourResults[i]
        
        res = results[i]
        hCash = placeBet(hCash, b, bAmount, bookiePred, res)
        cash= bet2(cash, bookiePred, ourRes, ourPred, res, betLimit, k , b)
        kCash = Kbet(kCash, bookiePred, ourRes, ourPred, res, betLimit)
        cashAmounts.append(cash)
        kAmounts.append(kCash)
        hAmounts.append(hCash)
    time = list(range(n + 1))
    plt.plot(time, kAmounts, '-', label='scaled kelly cash')
    plt.plot(time, cashAmounts, '-', label='learned model cash')
    plt.plot(time, hAmounts, '-', label='your bets')
    plt.xlabel('number of games')
    plt.ylabel('amount of cash')
    plt.legend(loc = 2)
    plt.savefig('demoSim.jpg')
    plt.show()

def info(game, teamID, bookie):
    homeTeam = teamID[game[0]]
    awayTeam = teamID[game[1]]
    print(homeTeam + ' Vs. ' + awayTeam)
    print('-' * 100)
    print('The home team is ' + homeTeam + ' and has average player rating ' + str(game[8]))
    for i in range(5):
        opp = teamID[game[2][i]]
        print()
        print(str(i + 1) + ' games ago they played against ' + opp + ' who has an average player rating of ' + str(game[6][i])) 
        print(homeTeam + ': ' + str(game[4][i][0]) + ' ' + opp + ': ' + str(game[4][i][1]))
    print('-' * 100)
    print('The away team is ' + awayTeam +  ' and has average player rating ' + str(game[9]))
    for i in range(5):
        opp = teamID[game[3][i]]
        print()
  
        print(str(i + 1) + ' games ago they played against ' + opp + ' who has an average player rating of ' + str(game[7][i])) 
        print(awayTeam + ': ' + str(game[5][i][0]) + ' ' + opp + ': ' + str(game[5][i][1]))
    print('-' * 100)
    print('decimal pay outs of bookies are:') 
    print('home win: ' + str(1/bookie[0]) + ' tie: ' + str(1/bookie[1]) + ' home loss ' + str(1/bookie[2]))
    print('-' * 100)



if __name__ == '__main__':
    betLimit = 100
    maxEaring = 5 * 100
    with open('demoX.pickle', 'rb') as handle:
        demoX = pickle.load(handle)
    with open('demoX1.pickle', 'rb') as handle:
        demoX1 = pickle.load(handle)

    with open('demoYVals.pickle', 'rb') as handle:
        yVals = pickle.load(handle)

    with open('demoBookies.pickle', 'rb') as handle:
        bookies = pickle.load(handle)

    with open('demoActual.pickle', 'rb') as handle:
        actual = pickle.load(handle)
    b =''
   
    while(b != 'no'):
        os.system('cls' if os.name == 'nt' else 'clear')
        print('welcome to the demo for using artificial intellignece to predict soccer games!')
        print()
        print('In this demo you will bet on 5 soccer games from the 2014/2015 and 2015/2016 seasons')
        print()
        print('You will then see how your bets performed compared to my model')
        print()
        c = 'hello world'
        while(c == 'hello world'):
             c = input('press enter to begin')
             
        a = list(range(len(demoX)))
        random.shuffle(a)
        gIndices = a[:5]
        dXVals = []
        dYVals = []
        dBookies = []
        dActual = []
        
        for idx in gIndices:
            dXVals.append(transformX(demoX[idx])) 
            dYVals.append(yVals[idx])
            dBookies.append(bookies[idx])
            dActual.append(actual[idx])
        demoSimText(dBookies, dYVals, dActual, dXVals)
        b = input('hit enter to play again: ')




