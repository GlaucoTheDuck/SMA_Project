import asyncio
from pyjabber.server import Server
from pyjabber.server_parameters import Parameters

async def main():
    params = Parameters()
    print(">> XMPP server up on localhost:5222")
    server = Server(params)
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())