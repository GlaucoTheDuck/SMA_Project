# bridge/main.py
import asyncio
import json
import logging
import uuid

import spade
from quart import Quart, request, jsonify, send_from_directory
from spade.message import Message

from agent import BridgeAgent, pending

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


app = Quart(__name__)
agent: BridgeAgent | None = None  # set in main()


# main.py
from agent import BridgeAgent, pending, outbox

async def send_and_wait(to: str, performative: str, payload: dict, timeout: int = 60) -> dict:
    conv_id = str(uuid.uuid4())
    future = asyncio.get_event_loop().create_future()
    pending[conv_id] = future

    msg = Message(to=to)
    msg.body = json.dumps(payload, ensure_ascii=False)
    msg.set_metadata("performative", performative)
    msg.set_metadata("ontology", "tutor-mvp")
    msg.set_metadata("conversation_id", conv_id)
    
    outbox.put_nowait(msg)   # <-- mudou aqui
    logger.info(f"-> {to} ({conv_id})")

    try:
        return await asyncio.wait_for(future, timeout=timeout)
    finally:
        pending.pop(conv_id, None)

# ===== Routes =====

@app.route("/")
async def index():
    return await send_from_directory("static", "index.html")


@app.route("/request-exercise", methods=["POST"])
async def request_exercise():
    body = await request.get_json()
    try:
        result = await send_and_wait(
            to="generator@localhost",
            performative="request",
            payload={"topic": body.get("topic", "loops")},
        )
        return jsonify({"ok": True, "result": result})
    except asyncio.TimeoutError:
        return jsonify({"ok": False, "error": "timeout"}), 504


@app.route("/submit-code", methods=["POST"])
async def submit_code():
    body = await request.get_json()
    try:
        result = await send_and_wait(
            to="verifier@localhost",
            performative="submit",
            payload={"exercise": body.get("exercise"), "code": body.get("code")},
            timeout=30,
        )
        return jsonify({"ok": True, "result": result})
    except asyncio.TimeoutError:
        return jsonify({"ok": False, "error": "timeout"}), 504


@app.route("/ask-question", methods=["POST"])
async def ask_question():
    body = await request.get_json()
    try:
        result = await send_and_wait(
            to="researcher@localhost",
            performative="query",
            payload={
                "search": body.get("question"),
                "exercise_statement": body.get("exercise_statement", ""),
            },
        )
        return jsonify({"ok": True, "result": result})
    except asyncio.TimeoutError:
        return jsonify({"ok": False, "error": "timeout"}), 504


# ===== Startup =====

async def main():
    global agent
    agent = BridgeAgent("bridge@localhost", "mvp_sma")
    await agent.start()
    await app.run_task(host="0.0.0.0", port=8000)
    await agent.stop()


if __name__ == "__main__":
    spade.run(main(), embedded_xmpp_server=False)