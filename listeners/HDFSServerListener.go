package main

import (
	"bufio"
	"database/sql"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"io"
	"net"
	"os"
	"os/exec"
	"strings"
	"sync"
)

const (
	Ip = "127.0.0.1"
	Port = "30004"
	MaxNum = 500


	DBuserName = "root"
	DBpassword = "111111"
	DBip = "127.0.0.1"
	DBport = "3306"
	DBName = "HDFS"
	TableName = "clients"

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
	listen, err := net.Listen("tcp", Ip+":"+Port)
	if err != nil {
		fmt.Println("fail to monitor the port:", err.Error())
		os.Exit(0)
	}
	defer listen.Close()
	listen = LimitListener(listen, MaxNum)
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
			var response string = "error"
			data := make([]byte, 1024)
			i, err := conn.Read(data)
			if err != nil {
				conn.Write([]byte(response))
				fmt.Println("error receiving data from client:", err.Error())
			}
			fmt.Println("client", conn.RemoteAddr().String(), "send data:", string(data[0:i]))
			var receiveData = string(data[0:i])
			// judge the operation
			colonIndex := strings.Index(receiveData, ":")
			if colonIndex < 0 {
				fmt.Println("the client send a wrong data from: " + conn.RemoteAddr().String())
				return
			}
			tmp := strings.Split(receiveData, ":")
			oper := tmp[0]
			value := tmp[1]

			switch oper {
			case "PeerId":
				// add by Nigel start: judge whether received a correct hash id

				// add by Nigel end
				path := strings.Join([]string{DBuserName, ":", DBpassword, "@tcp(", DBip, ":", DBport, ")/", DBName, "?charset=utf8"}, "")
				db, err := sql.Open("mysql", path)
				defer db.Close()
				if err != nil {
					conn.Write([]byte(response))
					panic(err.Error())
				}
				_, err = db.Query("select id from " + TableName + " limit 1")
				if err != nil {
					sql := "CREATE TABLE " + TableName +
						" (" +
						"`id` int(11) NOT NULL AUTO_INCREMENT, " +
						"`hash_id` varchar(255) DEFAULT NULL, " +
						"`address` varchar(255) DEFAULT NULL, " +
						"PRIMARY KEY (`id`)" +
						") ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;"
					_, err := db.Exec(sql)
					if err != nil {
						conn.Write([]byte(response))
						panic(err.Error())
					}
				}
				rows, err := db.Query("SELECT id FROM clients WHERE hash_id = ?", value)
				if err != nil {
					conn.Write([]byte(response))
					fmt.Println(err)
				}
				var existId int
				defer rows.Close()
				for rows.Next() {
					if err := rows.Scan(&existId); err != nil {
						conn.Write([]byte(response))
						panic(err)
					}
				}
				if existId > 0 {
					conn.Write([]byte(response))
					return
				} else {
					_, err = db.Exec("insert into clients (hash_id, address) values (?,?)", value, conn.RemoteAddr().String())
					if err != nil{
						conn.Write([]byte(response))
						panic(err)
					}
				}

				response = "success"
				conn.Write([]byte(response))
			case "Add":
				// add by Nigel start: judge whether received a correct hash id
				
				// add by Nigel end
				command := "ipfs get " + value + " --output=repos/" + value
				cmd := exec.Command("/bin/bash", "-c", command)
				stdout, err := cmd.StdoutPipe()
				if err != nil {
					conn.Write([]byte(response))
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
					if err2 != nil {
						conn.Write([]byte(response))
						break
					}
					if io.EOF == err2 {
						break
					}
				}
				fmt.Println(response)
				cmd.Wait()
				conn.Write([]byte(response))
				
			default:
				fmt.Print("The server is under attack from " + conn.RemoteAddr().String())
				return
			}
		}()
	}
}
