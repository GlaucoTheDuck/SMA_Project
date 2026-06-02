from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json
import urllib.request
import urllib.parse
import logging

logger = logging.getLogger(__name__)

EXA_API_KEY = "4935752b-bc4e-4a40-a57f-6a472efaeb44"

def search_exa(query):
    url = "https://api.exa.ai/search"
    payload = json.dumps({
        "query": query,
        "numResults": 1,
        "contents": {"text": True}
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "x-api-key": EXA_API_KEY
    })
    with urllib.request.urlopen(req) as r:
        results = json.loads(r.read())["results"]
    return [
        {
            "title": item.get("title", ""),
            "link": item.get("url", ""),
            "answer": (item.get("text") or "")
        }
        for item in results
    ]

class ResearchAgent(Agent):
    class HandleRequest(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if not msg:
                return
            print(msg.body)
            content = json.loads(msg.body)
            answer = search_exa(content['search'])
            print(answer)
            reply = Message(to="teacher@localhost")
            reply.body = json.dumps({"question": msg.body, "sources": answer})
            reply.set_metadata("performative", "inform")
            await self.send(reply)

    async def setup(self):
        logger.info("[researcher] online")
        self.add_behaviour(self.HandleRequest())