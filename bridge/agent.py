# bridge/agent.py
import asyncio
import json
import logging

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

logger = logging.getLogger(__name__)


# shared with main.py
pending: dict[str, asyncio.Future] = {}
outbox: asyncio.Queue = asyncio.Queue()  # routes put Message here; SendOutbox consumes


class BridgeAgent(Agent):
    class CollectReplies(CyclicBehaviour):
        async def run(self):
            try:
                msg = await self.receive(timeout=5)
                if not msg:
                    return
                
                conv_id = msg.get_metadata("conversation_id")
                logger.info(f"<- got reply from {msg.sender}, conv_id={conv_id}")
                
                future = pending.get(conv_id)
                if not future:
                    logger.warning(f"no pending future for conv_id={conv_id}, dropping")
                    return
                if future.done():
                    logger.warning(f"future already done for conv_id={conv_id}")
                    return
                
                payload = json.loads(msg.body)
                future.set_result(payload)
                logger.info(f"resolved future for {conv_id}")
            except Exception as e:
                logger.exception(f"error in CollectReplies: {e}")

    class SendOutbox(CyclicBehaviour):
        async def run(self):
            try:
                msg = await outbox.get()
                logger.info(f"-> sending to {msg.to}, conv_id={msg.get_metadata('conversation_id')}")
                await self.send(msg)
            except Exception as e:
                logger.exception(f"error in SendOutbox: {e}")

    async def setup(self):
        logger.info("[bridge] online")
        self.add_behaviour(self.CollectReplies())
        self.add_behaviour(self.SendOutbox())