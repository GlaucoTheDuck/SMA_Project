import asyncio
import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message


class Tester(Agent):
    class Probe(OneShotBehaviour):
        async def run(self):
            msg = Message(to="generator@localhost")
            msg.body = "hello generator"
            msg.set_metadata("performative", "request")
            await self.send(msg)
            print("sent:", msg.body)

            reply = await self.receive(timeout=5)
            print(reply)
            if reply:
                print("got:", reply.body)
            else:
                print("no reply")
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.Probe())


async def main():
    t = Tester("tester@localhost", "senha")
    await t.start(auto_register=True)
    await spade.wait_until_finished(t)
    await t.stop()


spade.run(main(), embedded_xmpp_server=False)