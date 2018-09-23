package main

import (
	"bufio"
	"fmt"
	"io"
	"net"
	"os"
	"os/exec"
	"strings"
	"sync"
)

// LimitListener returns a Listener that accepts at most n simultaneous connections from the provided listener
func LimitListener(l net.Listener, n int) net.Listener {
	return &limitListener{l, make(chan struct{}, n)}
}

type limitListener struct {
	net.Listener
	sem chan struct{}
}

func (l *limitListener) acquire() { l.sem <- struct{}{} }
func (l *limitListener) release() { <-l.sem }

func (l *limitListener) Accept() (net.Conn, error) {
	l.acquire()
	c, err := l.Listener.Accept()
	if err != nil {
		l.release()
		return nil, err
	}
	return &limitListenerConn{Conn: c, release: l.release}, nil
}

type limitListenerConn struct {
	net.Conn
	releaseOnce sync.Once
	release     func()
}

func (l *limitListenerConn) Close() error {
	err := l.Conn.Close()
	l.releaseOnce.Do(l.release)
	return err
}

func main() {
	listen, err := net.Listen("tcp", "127.0.0.1:30004")
	if err != nil {
		fmt.Println("fail to monitor the port:", err.Error())
		os.Exit(0)
	}
	defer listen.Close()
	listen = LimitListener(listen, 1000)
	fmt.Println("finish initialization, waiting for clients...")
	Server(listen)
}

func handleOutput(line string) string {
	var response string
	line = strings.TrimSpace(line)
	fmt.Println(line)
	if line == "get:success"{
		response = "success"
	}else{
		response = "error"
	}
	return response
}


func Server(listen net.Listener) {
	for {
		conn, err := listen.Accept()
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
				fmt.Println(response)
				cmd.Wait()
				conn.Write([]byte(response)) // return the message through the original connection
			}

		}()
	}
}
