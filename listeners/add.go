package main

import (
	"bufio"
	"fmt"
	"io"
	"net"
	"os"
	"os/exec"
)
const (
	//绑定IP地址
	ip = "127.0.0.1"
	//绑定端口号
	port = 30004
)
func main() {
	listen, err := net.ListenTCP("tcp", &net.TCPAddr{net.ParseIP(ip), port, ""})
	if err != nil {
		fmt.Println("fail to monitor the port:", err.Error())
		os.Exit(0)
	}
	fmt.Println("finish initialization, waiting for clients...")
	Server(listen)
}

func handleCommandErr(err error) string {
	var response string
	if err != nil {
		fmt.Println("Something went wrong while handling commands!!!")
		response = "error"
	} else {
		response = "success"
	}
	return response
}

func handleOutput(line string) string {
	var response string
	if line == "get:success"{
		response = "success"
	}else{
		response = "error"
	}
	return response
}


func Server(listen *net.TCPListener) {
	for {
		conn, err := listen.AcceptTCP()
		if err != nil {
			fmt.Println("client connection error:", err.Error())
			continue
		}
		fmt.Println("connection from:", conn.RemoteAddr().String())
		defer conn.Close()
		go func() {
			data := make([]byte, 1024)
			i, err := conn.Read(data)
			fmt.Println("客户端", conn.RemoteAddr().String(), "发来数据:", string(data[0:i]))
			var receiveData = string(data[0:i])
			fmt.Println(receiveData)
			if err != nil {
				fmt.Println("error receiving data from client:", err.Error())
			} else {
				var response string = "error"
				command := "ipfs get " + receiveData + " --output=repos/" + receiveData
				cmd := exec.Command("/bin/bash", "-c", command)
				fmt.Println(cmd.Args)
				stdout, err := cmd.StdoutPipe()
				if err != nil {
					fmt.Println(err)
				}
				cmd.Start()
				reader := bufio.NewReader(stdout)

				for {
					line, err2 := reader.ReadString('\n')
					response = handleOutput(line)
					if response == "success" {
						break
					}
					if err2 != nil || io.EOF == err2 {
						break
					}
				}

				cmd.Wait()
				conn.Write([]byte(response)) // return the message through the original connection
			}

		}()
	}
}
