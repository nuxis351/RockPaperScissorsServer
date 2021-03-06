import mysql.connector
import socket
from mysql.connector import errorcode
import array
import json

class DBManager:
    cnx = None
    def __init__(self):
        try:
            # Production Credentials
            #self.cnx = mysql.connector.connect(user='rpsdb1', password='tekashi69',
            #                     host='rpsdb1.cs0eeakwgvyu.us-east-2.rds.amazonaws.com',
            #                      database='rpsdb1')

            #Nick's Test Credentials
            self.cnx = mysql.connector.connect(user='rpsNick', password='Connection',
                                  host='rpsdb1.cs0eeakwgvyu.us-east-2.rds.amazonaws.com',
                                  database='rpsdbTest')

            print(self.cnx)

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print("error: ")
                print(err)
        
    # Prepares and excutes the SQL statement for Create account.
    # Accepts a list of userInfo as its paramater which holds all the relavent information
    # that was sent over by the client.
    # This will insert a new row into the rps_user table with all the listed columns filled out:
    #   rps_user_username
    #   rps_user_email
    #   rps_user_password
    #   rps_user_fname
    #   rps_user_lname
    def CreateAccount(self, userInfo):
        add_user = ("INSERT INTO rps_user "
                "(rps_user_username, rps_user_email, rps_user_password, rps_user_fname, rps_user_lname) "
                "VALUES (%s, %s, %s, %s, %s)")
        try:
            cursor = self.cnx.cursor()
            cursor.execute(add_user, userInfo)
            self.cnx.commit()
            cursor.close()
            self.cnx.close()
            return("1")
        except mysql.connector.Error as err:
            cursor.close()
            self.cnx.close()
            return err

    # Prepares and executes the select statement for the login function and returns all data
    # associated with the user account with whos password and username was matched.
    # Accepts a list of params as variable userInfo which contains a username and password
    # sent over from the client
    # Returned information is:
    #   rps_user_id
    #   rps_user_username
    #   rps_user_email
    #   rps_user_fname
    #   rps_user_lname
    #   rps_user_wins
    #   rps_user_losses
    #   rps_user_currency
    #   rps_user_score
    def Login(self, userInfo):
        login = ("SELECT rps_user_id, rps_user_username, rps_user_email, rps_user_fname, rps_user_lname, rps_user_wins, rps_user_losses, rps_user_currency, rps_user_score FROM rps_user WHERE rps_user_username = %s AND rps_user_password = %s")
        cursor = self.cnx.cursor(buffered=True)
        try:
            cursor.execute(login, userInfo)
            rows = cursor.rowcount
            #Obtains the row information in form of tuple
            result = cursor.fetchone()
            #Parses out the tuple into more understandable variables
            user_id = str(result[0])
            user_username = str(result[1])
            user_email = str(result[2])
            user_fname = str(result[3])
            user_lname = str(result[4])
            user_wins = str(result[5])
            user_losses = str(result[6])
            user_currency = str(result[7])
            user_score = str(result[8])
            #Packages the inforamtion into json format to be sent to client
            accountInfo_json = {
                "user_id" : user_id, 
                "firstname" : user_fname, 
                "lastname" : user_lname, 
                "email" : user_email, 
                "username" : user_username,
                "wins" : user_wins, 
                "losses" : user_losses, 
                "currency" : user_currency, 
                "score" : user_score
                }
            #Turns the json object into a string object
            accountInfo_string = json.dumps(accountInfo_json)

            cursor.close()
            self.cnx.close()
            # Will check to see if the login returned any information and then returns
            # said information as a string in json format
            if rows == 1:
                return (accountInfo_string)
            else:
                return ("Login Failure")
        except mysql.connector.Error as err:
            print(err)
            cursor.close()
            self.cnx.close()
            return err
    
    def updateAccountInfo(self, param):
        #print("param = " + param)
        get_account = ("UPDATE rps_user SET rps_user_username = %s WHERE rps_user_id = %s")
        cursor = self.cnx.cursor(buffered=True)
        try:
            cursor.execute(get_account, param)
            #result = str(cursor.fetchone()[0])
            self.cnx.commit()
            cursor.close()
            self.cnx.close()
            #print("Returned value from db = ")
            #print(result)
            return "1"
        except mysql.connector.Error as err:
            cursor.close()
            self.cnx.close()
            #print(err)
            return err
    
    def AI_fetch(self, move_Info):
        print(move_Info)
        query1 = ("SELECT COUNT(*) FROM move_history WHERE rps_user_id = %s AND move_history_pMove = %s AND move_history_pResult = %s AND move_history_move = 1")
        query2 = ("SELECT COUNT(*) FROM move_history WHERE rps_user_id = %s AND move_history_pMove = %s AND move_history_pResult = %s AND move_history_move = 2")
        query3 = ("SELECT COUNT(*) FROM move_history WHERE rps_user_id = %s AND move_history_pMove = %s AND move_history_pResult = %s AND move_history_move = 3")
        cursor = self.cnx.cursor(buffered=True)
        try:
            cursor.execute(query1, move_Info)
            result1 = cursor.fetchone()
            cursor.execute(query2, move_Info)
            result2 = cursor.fetchone()
            cursor.execute(query3, move_Info)
            result3 = cursor.fetchone()
            self.cnx.commit()
            cursor.close()
            self.cnx.close()
            if result1[0] > result2[0] and result1[0] > result3[0]:
                return 2
            elif result2[0] > result3[0] and result2[0] > result1[0]:
                return 3
            else:
                return 1
        except mysql.connector.Error as err:
            cursor.close()
            self.cnx.close()
            return err
    
    def move_Insert(self, move_Info):
        query = ("INSERT into move_history (rps_user_id, move_history_pMove, move_history_pResult, move_history_move, move_history_result, move_history_round) VALUES (%s, %s, %s, %s, %s, %s)")
        cursor = self.cnx.cursor(buffered=True)
        try:
            cursor.execute(query, move_Info)
            self.cnx.commit()
            cursor.close()
            self.cnx.close()
            return 1
        except mysql.connector.Error as err:
            cursor.close()
            self.cnx.close()
            return err

    def updateWinLoss(self, param):
        query = ("UPDATE rps_user SET rps_user_wins = %s, rps_user_losses = %s WHERE rps_user_id = %s")
        cursor = self.cnx.cursor(buffered=True)
        try:
            cursor.execute(query, param)
            self.cnx.commit()
            cursor.close()
            self.cnx.close()
            return "Updated Win and Loss!"
        except mysql.connector.Error as err:
            cursor.close()
            self.cnx.close()
            return err
    
    def updateScore(self, param):
        winnerId = param[0] 
        winnerScore = param[1] 
        loserId = param[2]
        loserScore = param[3]
        scoreCalc = 10 #The score to be added/subtracted due to win/loss, before underdog bonus
        #Checks if there is an 'underdog' and applies score bonus accordingly
        if(loserScore - winnerScore >= 100): 
            scoreCalc = scoreCalc + (winnerScore - loserScore)/10
        query = ("UPDATE rps_user SET rps_user_score = %s WHERE rps_user_id = %s")
        queryInfoWinner = [winnerScore + scoreCalc, winnerId]
        queryInfoLoser = [loserScore - scoreCalc, loserId]
        cursor = self.cnx.cursor(buffered=True)
        try:
            cursor.execute(query, queryInfoWinner)
            cursor.execute(query, queryInfoLoser)
            self.cnx.commit()
            cursor.close()
            self.cnx.close()
            return "Updated Score!"
        except mysql.connector.Error as err:
            cursor.close()
            self.cnx.close()
            return err
        finally:
            cursor.close()

    def leaderboard(self):
        query = ("SELECT rps_user_username, rps_user_score FROM rps_user ORDER BY rps_user_score")
        cursor = self.cnx.cursor(buffered=True)
        try:
            cursor.execute(query)
            #Places all rows of query into 'result'
            result = cursor.fetchall()
            return result
            #  Old code
            #self.cnx.commit()
            #cursor.close()
            #self.cnx.close()
        except mysql.connector.Error as err:
            cursor.close()
            self.cnx.close()
            return err
        finally:
            cursor.close()
    
    def addFriend(self, twofriends):
        query = ("INSERT INTO friends (player_username, player2_username) VALUES (%s, %s)")
        cursor = self.cnx.cursor(buffered = True)
        try:
            cursor.execute(query, twofriends)
            self.cnx.commit()
            cursor.close()
            self.cnx.close()
            return "1"
        except mysql.connector.Error as err:
            cursor.close()
            self.cnx.close()
            return err
    
    def findFriends(self, username):
        query = ("SELECT player_username FROM friends WHERE player2_username = %s UNION SELECT player2_username FROM friends WHERE player_username = %s")
        inHouse = []
        inHouse.append(username)
        inHouse.append(username)
        cursor = self.cnx.cursor()
        print("Entering try")
        try:
            cursor.execute(query, inHouse)
            sqlretval = cursor.fetchall()
            cursor.close()
            self.cnx.close()
            print(sqlretval)
            holdretval = ()
            for x in sqlretval:
                print(x)
                holdretval = holdretval + x
            retval = ""
            for x in holdretval:
                print(x)
                retval = retval + x
                retval = retval + ","
            print(len(retval))
            return retval
        except mysql.connector.Error as err:
            cursor.close()
            self.cnx.close()
            print(err)
            return err