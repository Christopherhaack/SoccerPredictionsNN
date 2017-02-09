import sqlite3 
import datetime 
import dateutil.parser
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
        statement += p_statement + o_statement
        c.execute(statement) 
        temp = c.fetchall()
        for pDate in temp:
            if  dateutil.parser.parse(pDate[3]) - margin <  dateutil.parser.parse(date) <  dateutil.parser.parse(pDate[3]):
                pS = pDate
                break;
        s.append(pS)
    
    return s
    
    
def gamesMapping(team_id, games):
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
        #need to make json parse function here to get some better info
        p += game[77:85]
        performance.append(p)
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
        self.teams = teams
        self.league_id = league_id
        self.season = season
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
    
