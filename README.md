# computer-communication-networks
This is a repository for all the assignments of Computer Communication Networks course at SCE (Sami Shamoon College of Engineering).

# Assignments
<h3>[hw-1] udp client-server:</h3>
1. Implement server / client in UDP.
2. Support multiple client connections to the server.
3. A client sends a message to the client through the server.
4. The server maintains a data structure between customer names and their addresses.

<h3>[hw-2] TCP client-server:</h3>
A simple TCP client-server application.
1. Creating a TCP server that starts listening.
2. Connection of the TCP server to other servers.
   
<h3>[hw-3] TCP and P2P:</h3> 
1. Define an organized and planned protocol (TCP protocol) for the P2P network.
2. Implement a P2P network between the servers. 
3. The server will receive the port number from the user's input, then it starts waiting for connections on this port.
4. There is a predefined array of ports in the code that the server tries to connect to them.
   - If the server could connect successfully to one the other servers, then it collects from it all address of other servers in the network and connects to them by port cycle, adds the servers address and the socket to a global dictionary.
   - If the server could not connect to any of the other servers, then it will wait for a connection from another server.
5. For each successful connection, the server waits for service requests using 'recv' function, according to a binary protocol defined as follows:
   - Each message begins with the next fields:
   - type filed: 1 byte, defines the type of the message.
   - subtype filed: 1 byte, defines the subtype. 
   - length filed: 2 bytes, defines the length of the message (not including the size of fields).
   - sublen filed: 2 bytes, defines the length of the subtype (not including the size of fields).
   - After the four fields appears a sequence of bytes with a length of 'len' filed, which will be called data later (in homework 4).
6. Message types: 
    - type = 0 : Request to receive information about network connections:
      - The sublen field – reserved for the future (currently zero)
      - No data
      - In the subtype field we will transfer the type of connections we are interested in:
        - subtupe = 0 :  Information about servers that the server is connected to them.
        - sybtype = 1 : Information about users that are connected to the server.
    - type = 1 : Response to a request for information about network connections:
      - The sublen field – reserved for the future (currently zero)
      - The subtype field refers to the request we answer to (this field will have the same value as the subtype in the request message). 
      - If information about other servers was requested, the server will return string with the next template: port:ip (for example 50:1.0.0.196) separated by the character '\0'. 
      - If information about the users was requested, the server will return the names of the users separated by '\0' character.