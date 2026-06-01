
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import subprocess
import json
import textwrap
from howdoi import howdoi
import logging


logger = logging.getLogger(__name__)


class ResearchAgent(Agent):
    class HandleRequest(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if not msg:
                return
            
            print(msg.body)
            content = json.loads(msg.body)

            query = {
                'query': content['search'],
                'num_answers': 3,
                'link': True
            }
            answer = howdoi.howdoi(query)
            
            reply = msg.make_reply()
            reply.body = json.dumps(answer)
            reply.set_metadata("performative", "inform")

            await self.send(reply)
        
    async def setup(self):
        logger.info("[researcher] online")
        self.add_behaviour(self.HandleRequest())

