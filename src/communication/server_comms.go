package conn

import (
	"bufio"
	"fmt"
	"net"
	"strconv"
	"strings"
)

func connect(protocol string, address_with_port string) {

	// Connect to the Lua socket server running in the emulator
	conn, err := net.Dial(protocol, address_with_port)
	if err != nil {
		panic(err)
	}
	defer conn.Close()

	reader := bufio.NewReader(conn)
	writer := bufio.NewWriter(conn)
	fmt.Println("Connected to ", address_with_port)

	for {
		// Read data from the Lua server
		data, err := reader.ReadString('\n')
		if err != nil {
			panic(err)
		}

		fmt.Println("Data: ", data)

		// Clean and parse Mario's X coordinate
		marioXStr := strings.TrimSpace(data)
		marioX, err := strconv.Atoi(marioXStr)
		if err != nil {
			fmt.Println("Invalid number received: ", marioXStr)
			continue
		}

		// Decide on input based on X-position
		var command string
		if marioX < 100 {
			command = "right\n"
		} else {
			command = "left\n"
		}

		// Send command to Lua
		_, err = writer.WriteString(command)
		if err != nil {
			panic(err)
		}
		writer.Flush()
	}
}
