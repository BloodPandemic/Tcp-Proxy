import sys
import threading
import socket


HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()

        results = list()
        for i in range(0, len(src), length):
            word=str(src[i:i+length])
            printable = word.translate(HEX_FILTER)

            #printing phase {beauty printing}
            hexa = "".join([f"{ord(c):02X}" for c in word])
            hex_width = length * 3
            results.append(f'{i:04x} {hexa:<{hex_width}}')
            
        if show:
            for lines in results:
                print(lines)
        else:
            return results


def recieve_from(connection):
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer


def request_handler(buffer):
    return buffer 

def response_handler(buffer):
    return buffer

#we can modify theese functions 

#proxy handler
def proxy_handler(client_socket, remote_host, remote_port, recieve_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    if recieve_first:
        remote_buffer = recieve_from(remote_socket)
        hexdump(remote_buffer)
    remote_buffer = response_handler(remote_buffer)

    if len(remote_buffer):
        print(f"<---- Sending {len(remote_buffer)} bytes to localhost")
        client_socket.send(remote_buffer)
    while True:
        local_buffer = recieve_from(client_socket)
        if len(local_buffer):
            line = f'---> recieved {len(local_buffer)} bytes from localhost'
            print(line)
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("---> Sent to remote")
        remote_buffer = recieve_from(remote_socket)
        if len(remote_buffer):
            print(f"<--- recieved {len(remote_buffer)} bytes from localhost")
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("<---- Sent to localhost")
        
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] no more data closing connection")
            break

def server_loop(local_host, local_port, remote_host, remote_port, recieve_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f"problem on bind {e}")
        print(f'Failed to listen on {local_host}:{local_port}')
        print("checking for other listening sockets or permissions")
        sys.exit(0)

    print(f"listneing on {local_host}:{local_port}")
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        #start a thread to talk to the remote host
        proxy_thread= threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, recieve_first))
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print(" usage: ./tcp_proxy.py [localhost] [localport]", end='')

        print('[remotehost] [remoteport] [recievefirst]')
        print("EXAMPLE: ./tcp_proxy.py 127.0.0.1 4444 10.12.132.1 4444 True")

        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    recieve_first = sys.argv[5]
    if "True" in recieve_first:
        recieve_first = True
    else:
        recieve_first = False

    server_loop(local_host, local_port, remote_host, remote_port, recieve_first)

if __name__=="__main__":
    main()



