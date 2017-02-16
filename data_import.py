import sqlite3 
import datetime 
import dateutil.parser
import xml.etree.ElementTree as ET
import numpy as np
from sklearn.preprocessing import StandardScaler

conn = sqlite3.connect('C:\\Users\ChristopherHaack\Downloads\soccer\database.sqlite')
c = conn.cursor()

def getPlayerStats(player_ids, home, date ):
    s = []
    
    margin = datetime.timedelta(days = 365)
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
            print(player, date, pDate[3])
            
    return s


def getShotInfo(sInfo, team_id):
    '''
    helper function to count how many shots each team has
    '''
    cnt1 = 0
    cnt2 = 0
    shotTree = ET.fromstring(sInfo)
    for elem in shotTree:
        for item in elem:
            if item.text == str(team_id):
                cnt1 += 1
            elif (item.text != str(team_id)) and (item.tag == 'team'):
                cnt2 += 1
    return cnt1, cnt2

def getPosInfo(pInfo, home):
    '''
    helper function to see posession break down of the game
    '''
    posTree = ET.fromstring(pInfo)
    vals = [0, 0 ,0 ,0]
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
    return vals


    
def gamesMapping(team_id, games, normalize=False):
    performance = []
    for game in games:
        p = []
        #adds 
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


class season:
    def __init__(self, season = '2015/2016'):
        season = '2015/2016'
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
class leagueSeason:
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
    
