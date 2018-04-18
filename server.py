import asyncio
import threading
import time
import json
try:
    from kivy.core.clipboard import Clipboard
except:
    pass

connected_transport = dict()
usernames = dict()
keys = dict()

class ServerClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info('peername')

        connected_transport.update({self.peername: transport})
        print('Connection from {}'.format(self.peername))

    def data_received(self, data):
        message = json.loads(data.decode())
        print('Data received: {!r}'.format(message))

        if 'public_key' in message:
            usernames[message['sender']] = self.transport
            keys[message['sender']] = message['public_key']
            print(keys)
            for client in connected_transport.values():
                client.write(json.dumps({'keys': keys}).encode('utf-8', 'ignore'))
        else:
            receiver = message['receiver']
            usernames[receiver].write(data)

    def connection_lost(self, exc):
        print('Lost connection of {}'.format(self.peername))
        del connected_transport[self.peername]
        self.transport.close()

def are_you_ok():
    while True:
        for i in [i for i in connected_transport.values()]:
            i.write(b"*1*")
        time.sleep(40)

loop = asyncio.get_event_loop()
coro = loop.create_server(ServerClientProtocol, '0.0.0.0', 9000)
server = loop.run_until_complete(coro)

print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    threading.Thread(target=are_you_ok).start()
    loop.run_forever()
except KeyboardInterrupt:
    pass

server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
