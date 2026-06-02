
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import subprocess
import json
import textwrap

import logging


logger = logging.getLogger(__name__)


class ValidatorAgent(Agent):
    class HandleRequest(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if not msg:
                return
            print(msg.body)
            generate = json.loads(msg.body)

            solution = generate['reference_solution']
            function_name = generate['function_name']
            tests = generate['tests']

            script = textwrap.dedent(f"""
{solution}

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
                body = {"type": "exercise", "exercise": generate}
                reply = Message(to="bridge@localhost")
                reply.body = json.dumps(body)
                reply.set_metadata("performative", "inform")
                reply.set_metadata("ontology", "tutor-mvp")
                reply.set_metadata("conversation_id", msg.get_metadata("conversation_id"))
                await self.send(reply)
            else:
                body = {
                    'msg': f"An error occurred while trying to run the validation code. Refactor the code by pointing out the problem.",
                    'erro_code': f'{result.returncode}',
                    'error': f'{result.stdout}'
                }
                reply = msg.make_reply()
                reply.body = json.dumps(body)
                reply.set_metadata("performative", "inform")
                reply.set_metadata("conversation_id", msg.get_metadata("conversation_id"))
                
                await self.send(reply)
            logger.info(f"replied to {reply.to}")
        
    async def setup(self):
        logger.info("[validator] online")
        self.add_behaviour(self.HandleRequest())

