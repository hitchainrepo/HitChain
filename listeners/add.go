package main

import (
	"bytes"
	"fmt"
	"net"
	"os"
	"os/exec"
	"strings"
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
		var remoteIpPort = conn.RemoteAddr().String()
		var indexSplit = strings.Index(remoteIpPort, ":")
		var remoteIp = remoteIpPort[:indexSplit]
		defer conn.Close()
		go func() {
			data := make([]byte, 1024)
			i, err := conn.Read(data)
			//fmt.Println("客户端", conn.RemoteAddr().String(), "发来数据:", string(data[0:i]))
			var receiveData = string(data[0:i])
			fmt.Println(receiveData)
			if err != nil {
				fmt.Println("读取客户端数据错误:", err.Error())
			} else {
				var response string
				var command string = "ipfs get " + receiveData
				fmt.Println(command)
				//var command string = "mkdir test"
				//cmd := exec.Command("/bin/bash", "-c", command)
				cmd := exec.Command("ipfs", "get", receiveData)
				var out bytes.Buffer
				cmd.Stdout = &out
				err2 := cmd.Start()
				if err2 != nil {
					fmt.Println("error")
					fmt.Println(err2)
					response = "error"
				} else {
					fmt.Println("success")
					resp := string(out.String())
					fmt.Println(resp)
					response = "success"
				}
				conn2, err2 := net.Dial("tcp", remoteIp + ":" + "38888")
				if err2 != nil {
					fmt.Println("回连客户端失败:", err2.Error())
					return
				}
				conn2.Write([]byte(response))
				conn2.Close()
			}

		}()
	}
}
