import discord
import threading
import asyncio
import json
import time

class DiscordClient(discord.Client):

    def __init__(self, to_slack, from_slack):
        # Call super
        super().__init__()
        # Store the queues
        self.to_slack = to_slack
        self.from_slack = from_slack
        # Create instance vars
        self.channels = dict()
        self.server = None

    @asyncio.coroutine
    def on_message(self, message):
        # Don't respond to yourself
        if message.author == self.user:
            return
        print(f"Message received from discord: {message.content}")
        # Send the message to the Slack
        self.to_slack.put({
            "type": "MSG",
            "sender": "ConnorZapfel",
            "channel": str(message.channel),
            "text": message.content
        })

    @asyncio.coroutine
    def on_ready(self):
        print('------')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print([x for x in self.servers])
        self.server = [x for x in self.servers][0]
        print('------')
        while True:
            # Wait for a message
            msg = self.from_slack.get(block=True)
            # Check the message type
            if msg["type"] == "MSG":
                print(f"Received from slack to {msg['channel']}: {msg['text']}")
                print(f"Available Chanels: {self.channels.keys()}")
                # Forward it to the discord server
                yield from self.send_message(self.channels[msg["channel"]], f"{msg['sender']}: {msg['text']}")
            elif msg["type"] == "CONF":
                # Create all the channels
                for ch_name in msg["channels"]:
                    yield from self.create_channel(self.server, ch_name)
                # Store then channel mapping
                print(f"Discovered channels: {[c for c in self.get_all_channels()]}")
                for ch in [c for c in self.get_all_channels()]:
                    self.channels[ch.name] = ch
                time.sleep(5)
