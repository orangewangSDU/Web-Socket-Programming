import tkinter as tk
import socket
import threading
import datetime

# 服务器地址和端口
SERVER_HOST = '192.168.59.236'
SERVER_PORT = 55774

# 创建Tkinter应用程序
app = tk.Tk()
app.title("Chat Client")

# 创建框架来放置聊天历史记录和消息输入框
frame = tk.Frame(app)
frame.pack(padx=10, pady=10)

# 创建滚动条和文本框用于显示消息
scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

messages_text = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
messages_text.pack(expand=True, fill=tk.BOTH)
scrollbar.config(command=messages_text.yview)

# 创建消息输入框
input_box = tk.Entry(app)
input_box.pack(padx=10, pady=(0, 10), fill=tk.X)

# 连接服务器
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

# 接收服务器消息的函数
def receive_messages():
    while True:
        try:
            # 接收消息并在文本框中显示
            message = client_socket.recv(1024).decode('utf-8')
            messages_text.insert(tk.END, message + '\n')
            messages_text.see(tk.END)  # 滚动到最新消息
        except:
            # 如果接收失败，关闭客户端套接字
            client_socket.close()
            break

# 启动接收消息的线程
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# 发送消息到服务器
def send_message(event=None):
    message = input_box.get()
    if message.lower() == 'exit' or message.lower() == 'quit':
        # 如果用户输入退出命令，关闭连接并退出程序
        client_socket.close()
        app.quit()
    else:
        # 添加时间戳
        timestamped_message = message
        client_socket.send(timestamped_message.encode('utf-8'))
        input_box.delete(0, tk.END)  # 清空输入框

# 创建发送按钮
send_button = tk.Button(app, text="Send", command=send_message)
send_button.pack(padx=10, pady=5, fill=tk.X)

# 绑定回车键发送消息
app.bind('<Return>', send_message)

# 运行Tkinter应用程序的主事件循环
app.mainloop()
