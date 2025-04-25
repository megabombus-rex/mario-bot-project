-- bot_server.lua

function connect(address, port, laddress, lport)
    local sock, err = socket.tcp()
    if not sock then return nil, err end
    if laddress then
        local res, err = sock:bind(laddress, lport, -1)
        if not res then return nil, err end
    end
    local res, err = sock:connect(address, port)
    if not res then return nil, err end
    return sock
end

function bind(host, port, backlog)
    local sock, err = socket.tcp()
    if not sock then return nil, err end
    sock:setoption("reuseaddr", true)
    local res, err = sock:bind(host, port)
    if not res then return nil, err end
    res, err = sock:listen(backlog)
    if not res then return nil, err end
    return sock
end

function server_loop()
    --local socket = require("socket.core")
    local socket = require("socket.core")

    emu.print(socket)

    if socket then
        emu.print("Socket is ok. :)")
    else
        emu.print("Problem with socket....")
    end
    
    local server, err = bind("127.0.0.1", 12345)
    if not server then
        print("Server error: " .. err)
        return
    end
    server:settimeout(0.1)

    emu.print("Connected", server, err)

    -- this is for the newest version
    --local server = sock.bind("127.0.0.1", 12345, -1)
    -- create a TCP socket and bind it to the local host, at any port
    --local server = assert(socket.bind("*", 0))
    -- find out which port the OS chose for us
    --local ip, port = server:getsockname()
    -- ^ do not use ^

    local client
    while not client do
        client = server:accept()

        if client then
            client:settimeout(10)
            local line, err = client:receive()
            if line then
                break
            end

            if err then
                emu.print("Error: ".. err)
            end
        end
        --emu.print("Waiting for client to connect")
    end

    while true do
        emu.print("Second loop.")
        -- Read Mario X position (Hi + Lo bytes)
        local marioX = memory.readbyte(0x006D) * 0x100 + memory.readbyte(0x0086)
    
        -- Send Mario's position to bot
        client:send(tostring(marioX) .. "\n")
    
        -- Receive input command from bot (like "right" or "left")
        local input = client:receive()
    
        if input then
            emu.print("Data from client: " .. input)
        end

        -- Apply input
        local joy = {}
        if input == "right" then
            joy.right = true
        elseif input == "left" then
            joy.left = true
        elseif input == "jump" then
            joy.A = true
        end
    
        joypad.set(1, joy)
    
        emu.frameadvance()  -- Go to next frame
    end
end

function main()
    server_loop()
end

main()