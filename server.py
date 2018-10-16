import socket
from Queue import myQueue
from API import api
HOST = '172.31.20.135'
PORT= 65432
def main():
    print("server is up")
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            myQue = myQueue()
            result = ''
            funtion = ''
            endData = 1
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    myQue.addtoq(data)
                    if data.decode('cp437') == "end":
                        break
                    print(data.decode('cp437'))
                    conn.sendall(data)
                function = (myQue.removefromq()).decode('cp437')
                print("function = " + function)
                print("reached")
                if(function == "CreateAccount"):
                    APICommand = api()
                    result = APICommand.CreateAccount(myQue)
                    print("result: " + result)
                else:
                    print("didn't match")
                conn.sendall(result.encode('ascii'))

        print("Connection Closed")

main()
