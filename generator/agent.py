
from schema import Exercise, TestCase
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message


import logging

VALIDATOR_JID = "validator@localhost"
logger = logging.getLogger(__name__)

example = Exercise(
    id="ex_001",
    topic="loops",
    statement="Implement sum_list(numbers) that returns the sum of a list using a for loop.",
    function_name="sum_list",
    reference_solution="def sum_list(numbers):\n    total = 0\n    for n in numbers:\n        total += n\n    return total",
    tests=[
        TestCase(args=[[1, 2, 3]], expected=6),
        TestCase(args=[[10, 20, 30]], expected=60),
        TestCase(args=[[]], expected=0),
    ],
)


class GeneratorAgent(Agent):
    class HandleRequest(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if not msg:
                return
            
            reply = Message(to=VALIDATOR_JID)
            reply.body = example.model_dump_json()
            reply.set_metadata("performative", "inform")
            print(reply.to)
            await self.send(reply)
            logger.info(f"replied to {msg.sender}")
        
    async def setup(self):
        logger.info("[generator] online")
        self.add_behaviour(self.HandleRequest())

