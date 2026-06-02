
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import subprocess
import json
import textwrap

import logging


logger = logging.getLogger(__name__)


class VerifierAgent(Agent):
    class HandleRequest(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if not msg:
                return
            print(msg.body)
            generate = json.loads(msg.body)

            code = generate['code']
            #function_name = generate['function_name']
            exercise = generate['exercise']
            print(exercise)
            script = textwrap.dedent(f"""
{code}

# --- ÁREA DE TESTE INJETADA AUTOMATICAMENTE ---
resultado = {function_name}({repr(tests[0]['args'][0])})
print(resultado)
""").strip()
            print(script)
            result = subprocess.run(
                ["python3", "-c", script],
                capture_output=True,
                text=True,
                timeout=5 # Mata o processo se demorar mais que 5 segundos (evita loop infinito)
            )

            print(result)
            if result.returncode == 0:
                print("Exit:", result.stdout) # Lógica de Conclusão
            else:
                body = {
                    'search': f"Code: {result.returncode} Error: {result.stderr}"
                }
                reply = Message(to="research@localhost")
                reply.body = json.dumps(body)
                reply.set_metadata("performative", "inform")
                
                await self.send(reply)
            logger.info(f"replied to {msg.sender}")
        
    async def setup(self):
        logger.info("[verifier] online")
        self.add_behaviour(self.HandleRequest())

