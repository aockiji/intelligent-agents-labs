import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour


class AgentOne(Agent):
    """A basic SPADE agent that prints a message periodically"""
    
    class HelloBehaviour(CyclicBehaviour):
        def __init__(self):
            super().__init__()
            self.counter = 0
        
        async def run(self):
            self.counter += 1
            print(f"[{self.agent.name}] Agent running and saying hello! (Count: {self.counter})")
            
            # so it doesn't run forever
            if self.counter >= 5:
                print(f"[{self.agent.name}] Stopping agent after {self.counter} iterations")
                await self.agent.stop()
            
            await asyncio.sleep(2)
    
    async def setup(self):
        print(f"[{self.name}] Agent setup started")
        self.add_behaviour(self.HelloBehaviour())
        print(f"[{self.name}] Agent setup completed")


async def main():
    print("="*60)
    print("Starting SPADE Agent with xmpp.jp")
    print("="*60)
    
    agent = AgentOne("aockiji@xmpp.jp", "40ck1j1@2077", verify_security=False)
    
    await agent.start()
    print("[INFO] Agent started successfully!\n")
    
    while agent.is_alive():
        await asyncio.sleep(1)
    
    print("\n[INFO] Agent has stopped")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())