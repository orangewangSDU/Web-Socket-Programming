import socket
import threading
import datetime

# 服务器地址和端口
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 55774

def get_server_address():
    # 创建一个临时套接字并连接到外部的地址，然后获取本地地址
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp_socket.connect(("8.8.8.8", 80))
    local_address = temp_socket.getsockname()[0]
    temp_socket.close()
    return local_address

# 获取服务器地址
server_address = get_server_address()
print("[INFO] Server address:", server_address)

# 存储所有连接的客户端及其用户名
clients = {}

# 处理客户端消息的函数
def handle_client(client_socket, username):
    while True:
        try:
            # 接收客户端消息
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                # 如果客户端断开连接，移除该客户端并关闭连接
                del clients[username]
                client_socket.close()
                broadcast("[INFO] {} disconnected".format(username), sender_socket=client_socket)
                break
            # 格式化消息
            formatted_message = "[{}] {}: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), username, message)
            # 向所有客户端广播消息，但不发送给发送消息的客户端
            broadcast(formatted_message, sender_socket=client_socket)
        except:
            # 如果客户端出现异常，也视为断开连接
            del clients[username]
            client_socket.close()
            broadcast("[INFO] {} disconnected".format(username), sender_socket=client_socket)
            break

# 广播消息给所有客户端，包括发送消息的客户端
def broadcast(message, sender_socket=None):
    for client_username, client_socket in clients.items():
        client_socket.send(message.encode('utf-8'))
    # 服务器显示消息
    print(message)

# 启动服务器
def start_server():
    # 创建 TCP 套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定地址和端口
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    # 监听连接
    server_socket.listen(5)
    print("[INFO] Server is listening on {}:{}".format(SERVER_HOST, SERVER_PORT))

    while True:
        # 接受客户端连接
        client_socket, client_address = server_socket.accept()
        print("[INFO] New connection from {}:{}".format(client_address[0], client_address[1]))
        # 要求客户端提供用户名
        client_socket.send("Enter your username: ".encode('utf-8'))
        # 接收客户端用户名
        username = client_socket.recv(1024).decode('utf-8')
        # 检查用户名是否重复
        if username in clients:
            client_socket.send("Username already taken. Please choose another one.".encode('utf-8'))
            client_socket.close()
            continue
        # 将客户端加入列表
        clients[username] = client_socket
        # 通知其他客户端有新用户登录
        broadcast("[INFO] {} has joined the chat.".format(username))
        # 启动处理客户端消息的线程
        client_thread = threading.Thread(target=handle_client, args=(client_socket, username))
        client_thread.start()

if __name__ == "__main__":
    start_server()
