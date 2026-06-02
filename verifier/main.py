from agent import VerifierAgent
import spade
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)

async def main():
    agent = VerifierAgent("verifier@localhost", "mvp_sma")
    await agent.start(auto_register=True)
    await spade.wait_until_finished(agent)

if __name__ == "__main__":
    spade.run(main())