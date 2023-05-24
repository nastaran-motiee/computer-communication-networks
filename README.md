# computer-communication-networks

This repository includes all the assignments of Computer Communication Networks course at SCE (Sami Shamoon College of
Engineering).

## Assignments

### [hw-1] udp client-server:

1. Implement server / client in UDP.
2. Support multiple client connections to the server.
3. A client sends a message to the client through the server.
4. The server maintains a data structure between customer names and their addresses.

### [hw-2] TCP client-server:

A simple TCP client-server application.

1. Creating a TCP server that starts listening.
2. Connection of the TCP server to other servers.

### [hw-3] TCP and P2P:

#### The server:

1. Define an organized and planned protocol (TCP protocol) for the P2P network.
2. Implement a P2P network between the servers.
3. The server will receive the port index (0-4) from the user's input, then it starts waiting for connections on this
   port.
4. There is a predefined array of addresses in the code that the server tries to connect to them. (Notice that all the
   ip addresses are '127.0.0.1' in this case, because all the servers in our case are on the same machine)
    - If the server could connect successfully to one the other servers, then it collects from it all address of other
      servers in the network and connects to them by port cycle, adds the servers address and the socket to a global
      dictionary.
    - If the server could not connect to any of the other servers, then it will wait for a connection from another
      server.
5. For each successful connection, the server waits for service requests using 'recv' function, according to a binary
   protocol defined as follows:

#### The Protocole:

1. Each message begins with the next fields:
    - **type filed**: 1 byte, defines the type of the message.
    - **subtype filed**: 1 byte, defines the subtype.
    - **length filed**: 2 bytes, defines the length of the message (not including the size of fields).
    - **sublen filed**: 2 bytes, defines the length of the subtype (not including the size of fields).
2. After the four fields appears a sequence of bytes with a length of 'len' filed, which will be called data later (
   in homework 4).
    - #### Message types:
        - [X] ``` type = 0 ```: Request to receive information about network connections:
            - The sublen field – reserved for the future (currently zero).
            - No data.
            - In the subtype field we will transfer the type of connections we are interested in:
                - subtupe = 0 :  Information about servers that the server is connected to them.
                - sybtype = 1 : Information about users that are connected to the server.
        - [X] ```type = 1``` : Response to a request for information about network connections:
            - The sublen field – reserved for the future (currently zero)
            - The subtype field refers to the request we answer to (this field will have the same value as the
              subtype in
              the request message).
            - If information about other servers was requested, the server will return string with the next
              template: port:
              ip (for example 50:1.0.0.196) separated by the character '\0'.
            - If information about the users was requested, the server will return the names of the users
              separated by '\0'
              character.
        - [X] ```type = 2``` : Setting the username for the connection.
            - for server the subtype will be 0 and for users the subtype will be 1.
            - The sublen field – reserved for the future (currently zero)
            - In data, we will transfer the username if subtype = 1, otherwise data will be empty.
        - [X] ```type = 3``` : Sending a message.
            - The subtype field – reserved for the future (currently zero)
            - The sublen field – the length of the username (in bytes after encoding)
            - The data field - In data we will transfer the username of the user we want to send the message to,
              followed immediately by the content of the message. Note that: len = sublen + |message|.
            - When the server forwards the message to the recipient or another server, it adds the username of the
              sender to the beginning of the message (sender + 0'\b + reciever), and accordingly updates the sublen.

#### implementation notes:

- In this exercise the reading and writing of the protocol was implemented.
- There are two dictionaries: a server dictionary and a user dictionary.
- Basic client program communicating with TCP protocol.
    - The client sends messages of only type = 2 and type = 3.
    - The client program get an input from the user for the address of the server.
    - For this assignment only, each time the server gets a message of type = 2, only if the username is not in the
      user dictionary, the server will send the the message to all the other servers in the network.

