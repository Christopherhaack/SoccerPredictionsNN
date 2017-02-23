import sqlite3 
import datetime 
import dateutil.parser
import xml.etree.ElementTree as ET
import numpy as np
from sklearn.preprocessing import StandardScaler

conn = sqlite3.connect('C:\\Users\ChristopherHaack\Downloads\soccer\database.sqlite')
c = conn.cursor()

def getPlayerStats(player_ids, home, date ):
    ''' this is a helper function that allows one to get satistical information loaded in the fifa
    video game for a given player on a given date. This allows us to know how good a player is in fifa
    @param player_ids a list of player id's that correspond to the fifa_api_ids of certain players
    @param home, is the team were looking at the home team
    @param date, date of the game
    @ return a list of player stats.
    '''
    s = []
    
    margin = datetime.timedelta(days = 365)
    #always returns the teams players first for the data structure.
    if home == False:
        temp = player_ids[11:] + player_ids[:11]
        player_ids = temp
    
    for player in player_ids:
        
        pS = []
        statement = '''select * from player_attributes where '''
        p_statement = ''' player_api_id = ''' + str(player)
        o_statement = ''' order by date'''
        #not an elegant solution at all deals with case where a player is loaded at none. Happens in very few matches so far as i can tell.
        try:
            statement += p_statement + o_statement
            c.execute(statement) 
            temp = c.fetchall()
            for pDate in temp:
                #checks to get the stat for the player in the current season
                if  dateutil.parser.parse(pDate[3]) <  dateutil.parser.parse(date):
                    pS = pDate[4:]
                    playerStat = []
                    for item in pS:
                        #only worry's about numeric fields. This throws out percieved work rates and dominant feet as these
                        #are not seen as important factors right now
                        if type(item) == type(1):
                            playerStat.append(item)
                if dateutil.parser.parse(pDate[3]) <  dateutil.parser.parse(date):
                    break;
        except:
            pass
        try:
            for item in playerStat:
                s.append(item)
        except:
            pass
            
    return s


def getShotInfo(sInfo, team_id):
    '''
    helper function to count how many shots each team has from an xml format
    '''
    cnt1 = 0
    cnt2 = 0
    #some matches dont have this info.
    try:
        shotTree = ET.fromstring(sInfo)
        for elem in shotTree:
            #each shot is loaded as a set of elements and right now we only care about quantity
            for item in elem:
                if item.text == str(team_id):
                    cnt1 += 1
                elif (item.text != str(team_id)) and (item.tag == 'team'):
                    cnt2 += 1
    except:
        pass
    return cnt1, cnt2

def getPosInfo(pInfo, home):
    '''
    helper function to see posession break down of the game at halftime and at full time
    '''
    vals = [0, 0 ,0 ,0]
    #some matches dont have this info.
    try:
        posTree = ET.fromstring(pInfo)

        for elem in posTree:
            for item in elem:
                if item.tag == 'elapsed' and item.text == '90':
                    for i2 in elem:
                        if i2.tag == 'homepos' and home:
                            vals[2] = int(i2.text)
                        elif i2.tag == 'homepos':
                            vals[3] = int(i2.text)
                        elif i2.tag == 'awaypos' and home == False:
                            vals[2] = int(i2.text)
                        elif i2.tag == 'awaypos' and home:
                            vals[3] = int(i2.text)
                elif item.tag == 'elapsed' and item.text == '45':
                    for i2 in elem:
                        if i2.tag == 'homepos' and home:
                            vals[0] = int(i2.text)
                        elif i2.tag == 'homepos':
                            vals[1] = int(i2.text)
                        elif i2.tag == 'awaypos' and home == False:
                            vals[0] = int(i2.text)
                        elif i2.tag == 'awaypos' and home:
                            vals[1] = int(i2.text)
    except:
        pass
    return vals


    
def gamesMapping(team_id, games, normalize=False):
    ''' this is a helperfunction that returns performance information for different games
    @param team_id is the id of the team
    @param games is the matches it played in
    @normalize attempts to normalize data set
    @return a performance which is a set of lists with stats about each game.
    '''
    performance = []
    for game in games:
        p = []
        #adds the stage of the season the game is in 
        p.append(game[4])
        #checks to see if the team is home team and adds result, which is given by [points, goals scored, goals against]
        if game[7] == team_id:
            home = True
            p.append(game[8])
            if game[9] > game[10]:
                p.append(3)
            elif game[9] == game[10]:
                p.append(1)
            else:
                p.append(0)
            p.append(game[9])
            p.append(game[10])
        else:
            home = False
            p.append(game[7])
            if game[9] > game[10]:
                p.append(3)
            elif game[9] == game[10]:
                p.append(1)
            else:
                p.append(0)
            p.append(game[10])
            p.append(game[9])
        #these will give positions of players
        p += game[12:55]
        #these will give stats of players
        p += getPlayerStats(game[55:77], home, game[5])
        #parses info about shots on target and gives (shots on target, shots against)
        p += getShotInfo(game[78], team_id)
        p += getShotInfo(game[79], team_id)
        p += getPosInfo(game[84], home)
         
        performance.append(p)
    if normalize:
        performance = np.asarray(performance)    
        performance = StandardScaler().fit_transform(performance)
    return performance
''' this is the class that will hold all the data'''
class soccerInfo:
    def __init__(self):
        self.seasonData = self.generateSeason()
    def generateSeason(self):
        sVals = []
        for i in range(2008, 2010):
            s = str(i) + "/" + str(i + 1)
            sTemp = season(season = s)
            sVals.append(sTemp)
        return sVals
class season:
    ''' this is a class which will hold performances over a set of seasons'''
    def __init__(self, season = '2015/2016'):
        selectS = ''' select league_id from match '''
        whereS = ''' where season = ''' +  "\"" + season + "\"" 
        grouping = '''
         group by league_id
        having count(*) > 100'''
        statement = selectS + whereS + grouping
        c.execute(statement)
        leagues = c.fetchall()
        self.leagues = leagues
        self.season = season
        self.pVals = self.genInfo()
    def genInfo(self):
        pVals = []
        print(self.season)
        '''for lTemp in self.leagues:
            league = lTemp[0]
            print(league)
            l = leagueSeason(league_id = league, season = self.season)
            pVals.append(l)''' 
        ''' normally i would do above, but this is being annoying today so only doing prem'''
        l = leagueSeason(league_id = 1729, season = self.season)
        pVals.append(l)
        return pVals
class leagueSeason:
    ''' this class will hold the information of a given leagues season'''
    def __init__(self, league_id = 1729, season = '2015/2016'):
        statement = '''select home_team_api_id
    from match where'''
        conn = sqlite3.connect('C:\\Users\ChristopherHaack\Downloads\soccer\database.sqlite')
        c = conn.cursor()
        league_clause = " league_id = " + str(league_id)
        s_clause = " season = " +  "\"" + season + "\"" 
        o_clause = " group by home_team_api_id"
        statement += league_clause + " and " + s_clause + o_clause
        c.execute(statement)
        teams = c.fetchall()
        teams1 = []
        for team in teams:
            teams1.append(team[0])
        self.teams = teams1
        self.league_id = league_id
        self.season = season
        self.info =self.getSeasonInfo()
        self.performances = self.generateSeasonPerformance()
        
    #this is a helper function used to get all of the team performance information
    def generateSeasonPerformance(self):
        performances = []
        for team in self.teams:
            p = teamPerformance(team, self.season)
            performances.append(p)
        return performances
    def getSeasonInfo(self):
        ''' class that is used to determine y values, basically just gives
        the two teams playing the game and the result and the stage of the season'''
        statement = '''select stage,
        home_team_api_id,
        away_team_api_id, 
        home_team_goal, 
        away_team_goal
        from match where'''
        league_clause = " league_id = " + str(self.league_id)
        s_clause = " season = " +  "\"" + self.season + "\"" 
        o_clause = " order by stage"

        statement += league_clause + " and " + s_clause + o_clause
        c.execute(statement)
        gameInfo = c.fetchall()
        gameInfo1 = []
        for game in gameInfo:
            g = []
            for i in game:
                g.append(i)
            if game[4] < game[3]:
                g.append(3)
            elif game[4] > game[3]:
                g.append(0)
            else:
                g.append(1)
            gameInfo1.append(g)
        return gameInfo1
    
''' this is the class that will store all the information about a given teams
performance in a season'''
class teamPerformance:
    
    def __init__(self, team_id = 10260, season = '2015/2016'):
        self.team_id = team_id
        conn = sqlite3.connect('C:\\Users\ChristopherHaack\Downloads\soccer\database.sqlite')
        c = conn.cursor()
        statement =    '''select *
        from match where'''
        h_clause = "home_team_api_id = " +str(team_id)
        a_clause = "away_team_api_id = " +str(team_id)
        o_clause = " order by stage"
        s_clause = " season = " +  "\"" + season + "\"" 
        statement +=  s_clause + 'and ( ' + h_clause + ' or ' + a_clause +' ) ' + o_clause
        c.execute(statement)
        games = c.fetchall()
        self.team_id = team_id
        performance = gamesMapping(self.team_id, games)
        self.performance = performance
    
