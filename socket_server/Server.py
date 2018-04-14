import asyncio

import sys
import threading
import User_Manager as Usr_Mg
from typing import Dict
import Vk_bot2
import queue
from utils import StringBuilder
import ConsoleLogger
LOGGER = ConsoleLogger.ConsoleLogger('Server')

class Client:
    def __init__(self,reader,writer,vk_id = 0):
        self.reader = reader
        self.writer = writer
        self.vk_id = vk_id
        self.connected_chat = 0
        self.name = 'Guest'

    def set_vk_id(self,vk_id):
        self.vk_id = vk_id
        return self

class Server:
    clients = {}
    server = None

    def __init__(self, host='127.0.0.1', port=27015, name = 'Server',loop = None, sender = None,message_queue: queue.Queue = None,database:Usr_Mg.UserManager = None,api = None):
        LOGGER.info('LOADING SERVER')
        self.loop = asyncio.get_event_loop()
        self.host = host
        self.port = port
        self.sender = sender
        self.message_queue = message_queue
        self.database = database
        self.api = api
        self.clients = {}  # type: Dict[str,Client]
        self.name = name
        self.thread = threading.Thread(target=self.run,kwargs={'loop':self.loop})
        self.thread.daemon = True
        self.thread.start()
    def run(self,loop):
        LOGGER.info('SERVER LOADED')
        asyncio.set_event_loop(loop)
        asyncio.ensure_future(self.run_server())
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            LOGGER.info('Received interrupt, closing')
            self.close()
        finally:
            self.loop.close()


    async def run_server(self):
        try:
            self.server = await asyncio.start_server(self.client_connected, self.host, self.port)
            LOGGER.info('Running server on {}:{}'.format(self.host, self.port))
        except OSError:
            LOGGER.info('Cannot bind to this port! Is the server already running?')
            self.loop.stop()

        ##########################
        #   SEND TO USERS PART   #
        ##########################

    def send_to(self, peername, msg):
        client = self.clients[peername]
        LOGGER.debug(f'Sending "{msg}" to {peername}')
        client.writer.write('{}\n'.format(msg).encode())
        return

        ##########################
        #   CONNECTION HANDLER   #
        ##########################

    async def client_connected(self, reader, writer):

        peername = writer.transport.get_extra_info('peername')[1]
        # print(peername)
        LOGGER.info('Client connected with id {}'.format(peername))
        new_client = Client(reader, writer)
        self.clients[peername] = new_client

        while not reader.at_eof():

            try:
                msg = await reader.readline()
                if msg:
                    msg = msg.decode().strip()  # type: str

                    if not msg == 'close()':
                        if msg.startswith('/'):
                            try:
                                if '/login:' in msg:
                                    token = msg.split(':')[-1]
                                    user,user_data = self.database.get_from_token(token)
                                    self.clients[peername].vk_id = user
                                    self.send_to(peername,'Welcome to remote console')
                            except Exception as Ex:
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                import traceback
                                TB = traceback.format_tb(exc_traceback)
                                LOGGER.error(TB, exc_type, exc_value)
                                del self.clients[peername]
                                continue
                            if '/chats' in msg:
                                chats = self.api.get_chats()
                                for chat_id,chat_name in chats.items():
                                    self.send_to(peername,f'{chat_id}:{chat_name}')
                            if '/connect' in msg:
                                chat = msg.split(' ')[-1]
                                self.clients[peername].connected_chat = int(chat)
                                self.send_to(peername,f'Connected to {chat} chat')
                            if msg.startswith('/s'):
                                self.sender(msg[2:], self.clients[peername].vk_id, self.clients[peername].connected_chat)
                            else:
                                pass
                        else:
                            LOGGER.info('Message from remote console:',msg)

                    else:
                        LOGGER.info('User {} disconnected'.format(peername))
                        del self.clients[peername]

            except ConnectionResetError:
                LOGGER.info('User {} disconnected'.format(peername))
                del self.clients[peername]
                return

        #################
        #   SHUT DOWN   #
        #################

    def close(self):
        self.close_clients()
        self.loop.stop()

    def close_clients(self):
        LOGGER.info('Sending EndOfFile to all clients to close them.')
        for peername, client in self.clients.items():
            client.writer.write_eof()





if __name__ == '__main__':
    mainserver = Server(name='Furry Server',host='',port=27015)