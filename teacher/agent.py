# teacher/agent.py
import json
import logging
import uuid
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

from llm import chat

logger = logging.getLogger(__name__)

BRIDGE_JID = "bridge@localhost"  # constante local mesmo

SYSTEM_PROMPT = """You are a Python programming tutor helping a beginner student.

Rules you MUST follow:
- Answer ONLY the specific question asked. Don't dump everything you know about the topic.
- Base your explanation on the reference material provided. Don't invent facts.
- Always include the source links at the end of your answer for further reading.
- Do NOT write the full solution to the exercise. Explain the concept, not the answer.
- Keep it short: 4 to 6 sentences max.
- Reply in Portuguese."""


class TeacherAgent(Agent):
    class Explain(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if not msg:
                return
            print(f'msg: {msg.body}')
            # parse payload inline
            try:
                payload = json.loads(msg.body) if msg.body else {}
            except json.JSONDecodeError:
                payload = {}

            question = payload.get("question", "")
            sources = payload.get("sources", [])
            exercise_statement = payload.get("exercise_statement", "")
            conv_id = msg.get_metadata("conversation_id")
            print(f'sources: {sources}')

            logger.info(f"explaining: {question[:60]}")

            sources_block = "\n".join(
                f"- {s.get('title', 'source')}: {s.get('link')}\n"
                f"  excerpt: {s.get('excerpt') or s.get('answer', '')}"
                for s in sources
            )

            print(f"DEBUG: type(sources) = {type(sources)}")
            print(f"DEBUG: sources len = {len(sources) if isinstance(sources, list) else 'N/A'}")
            if isinstance(sources, list) and len(sources) > 0:
                print(f"DEBUG: first element type = {type(sources[0])}, value = {sources[0]}")

            print(f'source block: {sources_block}')

            user_prompt = f"""Reference material:
{sources_block}

Exercise the student is working on:
{exercise_statement}

Student's question:
{question}

Answer focused on the question. End with the links from the reference material."""

            try:
                answer = chat(user_prompt, system=SYSTEM_PROMPT, temperature=0.4)
            except Exception as e:
                logger.error(f"LLM failed: {e}")
                links = ", ".join(s.get("url", "") for s in sources)
                answer = f"Não consegui formular a resposta agora. Consulte os links: {links}"

            # build reply inline
            reply = Message(to=BRIDGE_JID)
            reply.body = json.dumps({"type": "explanation", "text": answer}, ensure_ascii=False)
            reply.set_metadata("performative", "inform")
            reply.set_metadata("ontology", "tutor-mvp")
            
            if conv_id:
                reply.set_metadata("conversation_id", conv_id)
            
            print(reply)

            await self.send(reply)
            logger.info("explanation sent")

    async def setup(self):
        logger.info("[teacher] online")
        self.add_behaviour(self.Explain())