package main

import (
	"fmt"
	"net"
	"os"
)
const (
	//绑定IP地址
	ip = "127.0.0.1"
	//绑定端口号
	port = 7777
)
func main() {
	listen, err := net.ListenTCP("tcp", &net.TCPAddr{net.ParseIP(ip), port, ""})
	if err != nil {
		fmt.Println("监听端口失败:", err.Error())
		os.Exit(0)
	}
	fmt.Println("已初始化连接，等待客户端连接...")
	Server(listen)
}
func Server(listen *net.TCPListener) {
	for {
		conn, err := listen.AcceptTCP()
		if err != nil {
			fmt.Println("接受客户端连接异常:", err.Error())
			continue
		}
		fmt.Println("客户端连接来自:", conn.RemoteAddr().String())
		defer conn.Close()
		go func() {
			data := make([]byte, 1024)

			i, err := conn.Read(data)
			fmt.Println("客户端", conn.RemoteAddr().String(), "发来数据:", string(data[0:i]))
			if err != nil {
				fmt.Println("读取客户端数据错误:", err.Error())
				return
			} else {
				conn2, err2 := net.Dial("tcp", "127.0.0.1:38888")
				if err2 != nil {
					fmt.Println("回连客户端失败:", err2.Error())
					return
				}
				defer conn2.Close()
				Client(conn2)
			}
			//conn.Write(data[0:i])

		}()
	}
}

func Client(conn net.Conn) {
	conn.Write([]byte("服务器返回的消息"))
}