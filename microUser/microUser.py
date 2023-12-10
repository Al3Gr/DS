from concurrent import futures
from userDB import UserDB

import user_pb2
import user_pb2_grpc
import grpc



class UserService(user_pb2_grpc.UserServiceServicer):

    def __init__(self):
        self.db = UserDB()

    def UserSignup(self, request, context):
        print(f"Signup => Data received: {request.username}:{request.password}")
        query = {"username": request.username, "password": request.password}
        self.db.signup(query)
        return user_pb2.ReplySuccess(success="OK")

    def UserLogin(self, request, context):
        print(f"Login => Data received: {request.username}:{request.password}")
        query = {"username": request.username, "password": request.password}
        result = self.db.login(query)
        if result:
            return user_pb2.ReplyToken(token="TOKEN")
        else:
            return user_pb2.ReplyToken(token="ERROR")


def main():
    port = '20000'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print(f'Micro User Service start at port {port}')
    server.wait_for_termination()


if __name__ == "__main__":
    main()
