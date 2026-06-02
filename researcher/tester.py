import asyncio
import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
import json

class TesterAgent(Agent):
    class SendAndReceive(OneShotBehaviour):
        async def run(self):
            msg = Message(to="research@localhost")
            msg.body = json.dumps({"search": "how to read a file in python"})
            msg.set_metadata("performative", "request")
            await self.send(msg)
            print("Mensagem enviada, aguardando resposta...")
            reply = await self.receive(timeout=15)
            if reply:
                data = json.loads(reply.body)
                for item in data:
                    print(f"\nTítulo: {item['title']}")
                    print(f"Link: {item['link']}")
                    print(f"Resposta: {item['answer'].strip()}...")
            else:
                print("Sem resposta (timeout)")

    async def setup(self):
        self.add_behaviour(self.SendAndReceive())

async def main():
    agent = TesterAgent("tester@localhost", "mvp_sma")
    await agent.start(auto_register=True)
    await asyncio.sleep(20)
    await agent.stop()

spade.run(main())