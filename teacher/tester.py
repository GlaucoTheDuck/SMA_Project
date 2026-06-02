# test_teacher.py
import asyncio
import json
import logging
import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# Simulates what the Researcher would send to the Teacher
FAKE_RESEARCH = {
    "question": "Como funciona o return em uma função Python?",
    "exercise_statement": "Implemente sum_list(numbers) que retorna a soma de uma lista usando for.",
    "sources": [
        {
            "title": "Python docs - Defining Functions",
            "url": "https://docs.python.org/pt-br/3/tutorial/controlflow.html#defining-functions",
            "excerpt": "The return statement returns with a value from a function. return without an expression argument returns None.",
        },
        {
            "title": "Python docs - The for statement",
            "url": "https://docs.python.org/pt-br/3/tutorial/controlflow.html#for-statements",
            "excerpt": "Python's for statement iterates over the items of any sequence in the order that they appear.",
        },
    ],
}


class BridgeMock(Agent):
    class TestFlow(OneShotBehaviour):
        async def run(self):
            # 1) send fake research payload to teacher (as if Researcher did it)
            request = Message(to="teacher@localhost")
            request.body = json.dumps(FAKE_RESEARCH, ensure_ascii=False)
            request.set_metadata("performative", "inform")
            request.set_metadata("ontology", "tutor-mvp")
            request.set_metadata("conversation_id", "test-001")
            await self.send(request)
            logger.info(">>> sent research to teacher")
            logger.info(f"    question: {FAKE_RESEARCH['question']}")

            # 2) wait for teacher's reply (LLM may take a while)
            logger.info("waiting for teacher's reply (60s timeout)...")
            reply = await self.receive(timeout=60)

            if not reply:
                logger.error("<<< no reply — teacher did not respond in 60s")
                return

            try:
                payload = json.loads(reply.body)
            except json.JSONDecodeError:
                logger.error(f"<<< invalid JSON: {reply.body!r}")
                return

            logger.info("<<< reply received:")
            logger.info(f"    type: {payload.get('type')}")
            logger.info(f"    text:\n\n{payload.get('text', '(empty)')}\n")

    async def setup(self):
        self.add_behaviour(self.TestFlow())


async def main():
    agent = BridgeMock("bridge@localhost", "mvp_sma")
    await agent.start()
    await spade.wait_until_finished(agent)
    await agent.stop()


if __name__ == "__main__":
    spade.run(main(), embedded_xmpp_server=False)