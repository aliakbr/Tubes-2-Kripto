from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from datetime import datetime

import asyncio
import json
from kivy.clock import Clock
from functools import partial

PORT = 9000

Builder.load_string("""
<LoginScreen>:
    username: username_input_id
    password: password_input_id

    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'Login'
            size_hint: (1, .2)
        GridLayout:
            cols: 2
            Label:
                text: 'Username'
            TextInput:
                id: username_input_id
                multiline: False
            Label:
                text: 'Password'
            TextInput:
                id: password_input_id
                password: True
                multiline: False
            Button:
                text: 'Register'
                on_press:
                    root.manager.current = 'register'
                    root.manager.transition.direction = 'left'
            Button:
                text: 'Login'
                on_press:
                    root.handle_login()

<RegisterScreen>:
    username: username_input_id
    password: password_input_id

    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'Register'
            size_hint: (1, .2)
        GridLayout:
            cols: 2
            Label:
                text: 'Username'
            TextInput:
                id: username_input_id
                multiline: False
            Label:
                text: 'Password'
            TextInput:
                id: password_input_id
                password: True
                multiline: False
            Button:
                text: 'Back to Login'
                on_press:
                    root.manager.current = 'login'
                    root.manager.transition.direction = 'right'
            Button:
                text: 'Register'
                on_press:
                    root.handle_register()

<FriendScreen>:
    friends_list: friends_id

    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'Your Friends'
            size_hint: (1, .1)
        ScrollView:
            size_hint: (1, .8)
            GridLayout:
                cols: 1
                id: friends_id
        Button:
            text: 'Logout'
            size_hint: (1, .1)

<ChatScreen>:
    chat_list: chat_id
    chat_input: chat_input_id
    chat_friend_username: chat_friend_username_id

    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint: (1, .1)
            Button:
                text: 'Back'
                size_hint: (.1, 1)
                on_press:
                    root.manager.current = 'friend'
                    root.manager.transition.direction = 'right'
            Label:
                id: chat_friend_username_id
                size_hint: (.8, 1)
            Label:
                size_hint: (.1, 1)
        ScrollView:
            size_hint: (1, .8)
            Label:
                id: chat_id
        BoxLayout:
            size_hint: (1, .2)
            TextInput:
                id: chat_input_id
                size_hint: (.9, 1)
            Button:
                text: 'Send'
                size_hint: (.1, 1)
                on_press:
                    root.send_msg()
""")

friends = ['isak', 'sana']

class ClientProtocol(asyncio.Protocol):
    def __init__(self, manager, loop):
        self.manager = manager
        self.loop = loop

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        if data:
            message = data.decode('utf-8', 'ignore')
            message = json.loads(message)
            self.manager.chat_screen.chat_list.text += '{}: {}\n'.format(message['sender'], message['body'])

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.transport.close()

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        print(self.manager)

    def handle_login(self):
        username = self.username.text
        password = self.password.text
        if username != 'sana' and username != 'isak':
            popup = Popup(title='User Not Found', content=Label(text='Try to login again'), size_hint=(None, None), size=(300, 100))
            popup.open()
        else:
            self.manager.connect(username)

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super(RegisterScreen, self).__init__(**kwargs)

    def handle_register(self):
        print('Register')

class FriendScreen(Screen):
    def __init__(self, **kwargs):
        super(FriendScreen, self).__init__(**kwargs)

    def update(self):
        global friends
        self.friends_list.clear_widgets()
        for friend in friends:
            if friend != self.manager.username:
                button = Button(text=friend, on_press=partial(self.switch_to_friend, friend))
                self.friends_list.add_widget(button)

    def switch_to_friend(self, *args):
        self.manager.current = 'chat'
        self.manager.curr_friend = args[0]
        self.manager.transition.direction = 'left'
        self.manager.chat_screen.chat_friend_username.text = args[0]

class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super(ChatScreen, self).__init__(**kwargs)

    def send_msg(self):
        self.manager.send_msg(self.chat_input.text)
        self.chat_list.text += '{}: {}\n'.format(self.manager.username, self.chat_input.text)
        self.chat_input.text = ''

class RootWidget(ScreenManager):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.friend_screen = FriendScreen(name='friend')
        self.chat_screen = ChatScreen(name='chat')
        self.add_widget(LoginScreen(name='login'))
        self.add_widget(RegisterScreen(name='register'))
        self.add_widget(self.friend_screen)
        self.add_widget(self.chat_screen)

    def connect(self, username):
        self.username = username
        self.host = '127.0.0.1'
        self.is_stop = False
        self.loop = asyncio.get_event_loop()

        if self.reconnect():
            self.clock_receive = Clock.schedule_interval(self.receive_msg, 1)
            self.clock_detect = Clock.schedule_interval(self.detect_if_offline, 3)
            self.current = 'friend'
            self.friend_screen.update()
            print('-- connecting to ' + self.host)

    def reconnect(self):
        try:
            self.coro = self.loop.create_connection(lambda: ClientProtocol(self, self.loop),
                          self.host, PORT)
            self.transport, self.protocol = self.loop.run_until_complete(self.coro)

            self.last_connection_time = datetime.now()
            self.introduction()
            print("I just reconnected the server.")
            return True
        except Exception as e:
            self.current = 'login'
            try:
                self.clock_receive.cancel()
                self.clock_detect.cancel()
            except:
                print("No server available.")
            return False

    def detect_if_offline(self, dt): #run every 3 seconds
        if (datetime.now() - self.last_connection_time).total_seconds() > 45:
            self.transport.close()
            self.reconnect()

    def introduction(self):
        message = {
            'introduction': self.username
        }
        message = json.dumps(message)
        self.transport.write(message.encode('utf-8', 'ignore'))

    def send_msg(self, body):
        if self.transport.is_closing():
            self.transport.close()
            self.reconnect()
        message = {
            'sender': self.username,
            'receiver': self.curr_friend,
            'body': body
        }
        message = json.dumps(message)
        self.transport.write(message.encode('utf-8', 'ignore'))

    def receive_msg(self, dt):
        self.loop.run_until_complete(self.coro)

    def on_stop(self):
        exit()

class TestApp(App):
    def build(self):
        return RootWidget()

if __name__ == '__main__':
    TestApp().run()
