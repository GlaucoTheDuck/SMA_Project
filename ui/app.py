# bridge/main.py
import spade
from quart import Quart

from agent import BridgeAgent

app = Quart(__name__)
agent_ref = None  # vai ser preenchido no main()


@app.route("/")
async def home():
    return "bridge online"


async def main():
    global agent_ref
    agent_ref = BridgeAgent("bridge@localhost", "mvp_sma")
    await agent_ref.start()

    # roda o Quart dentro do mesmo loop asyncio do SPADE
    await app.run_task(host="0.0.0.0", port=8000)

    await agent_ref.stop()


if __name__ == "__main__":
    spade.run(main(), embedded_xmpp_server=False)