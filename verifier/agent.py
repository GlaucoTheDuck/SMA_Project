
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
            conv_id = msg.get_metadata('conversation_id')
            code = generate['code']
            exercise = generate['exercise']
            
            print(conv_id)
            
            script = textwrap.dedent(f"""
{code}

# --- ÁREA DE TESTE INJETADA AUTOMATICAMENTE ---
resultado = {exercise['function_name']}({repr(exercise['tests'][0]['args'][0])})
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
                reply = msg.make_reply()
                reply.body = json.dumps({"exercise": exercise, "result": result.stdout})
                reply.set_metadata("performative", "inform")
                reply.set_metadata("success", 'True')
                reply.set_metadata("conversation_id", conv_id)
                await self.send(reply)
            else:
                body = {
                    'search': f"Code: {result.returncode} Error: {result.stderr}"
                }
                reply = Message(to="researcher@localhost")
                reply.body = json.dumps(body)
                reply.set_metadata("performative", "inform")
                reply.set_metadata("conversation_id", conv_id)
                await self.send(reply)
            logger.info(f"replied to {msg.sender}")
        
    async def setup(self):
        logger.info("[verifier] online")
        self.add_behaviour(self.HandleRequest())

