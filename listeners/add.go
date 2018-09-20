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

func execCommand(commandName string) bool {
	cmd := exec.Command(commandName)

	fmt.Println(cmd.Args)
	//StdoutPipe方法返回一个在命令Start后与命令标准输出关联的管道。Wait方法获知命令结束后会关闭这个管道，一般不需要显式的关闭该管道。
	stdout, err := cmd.StdoutPipe()

	if err != nil {
		fmt.Println(err)
		return false
	}

	cmd.Start()
	//创建一个流来读取管道内内容，这里逻辑是通过一行一行的读取的
	reader := bufio.NewReader(stdout)

	//实时循环读取输出流中的一行内容
	for {
		line, err2 := reader.ReadString('\n')
		if err2 != nil || io.EOF == err2 {
			break
		}
		fmt.Println(line)
	}

	//阻塞直到该命令执行完成，该命令必须是被Start方法开始执行的
	cmd.Wait()
	return true
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
				var response string
				//var out bytes.Buffer
				command := "ipfs get " + receiveData + " --output=repos/" + receiveData
				getResult := execCommand(command)
				if getResult == true{
					response = "success"
				} else {
					response = "error"
				}
				//cmd := exec.Command("/bin/bash", "-c", command)
				//cmd.Stdout = &out
				//err2 := cmd.Start()
				//response = handleCommandErr(err2)
				//err2 = cmd.Wait()
				//response = handleCommandErr(err2)
				fmt.Println(response)

				conn.Write([]byte(response)) // return the message through the original connection
			}

		}()
	}
}
