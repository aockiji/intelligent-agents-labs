import asyncio
import random
from datetime import datetime
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour

from disaster_env import DisasterEnvironment

class SensorAgent(Agent):
    """
    Agent that periodically monitors environmental conditions
    and detects disaster events.
    """
    
    class PerceptionBehaviour(PeriodicBehaviour):
        """
        Periodic behavior that senses the environment every few seconds.
        """
        
        def __init__(self, period, environment, log_file):
            super().__init__(period=period)
            self.environment = environment
            self.log_file = log_file
            self.perception_count = 0
        
        async def run(self):
            """
            Main perception loop:
            1. Sense environment
            2. Check for disasters
            3. Log events
            """
            self.perception_count += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Update environment conditions
            self.environment.update_conditions()
            
            # Get curr percepts
            state = self.environment.get_current_state()
            
            # Print
            print("=" * 70)
            print(f"[PERCEPTION #{self.perception_count}] @ {timestamp}")
            print("=" * 70)
            print(f"Temperature:        {state['temperature']}°C")
            print(f"Humidity:           {state['humidity']}%")
            print(f"Wind Speed:         {state['wind_speed']} km/h")
            print(f"Water Level:        {state['water_level']} m")
            print(f"Structural Damage:  {state['structural_damage']}%")
            
            # Log 
            self.log_event(timestamp, "ENVIRONMENT_STATE", state)
            
            # Random chance of disaster 
            if random.random() < 0.4:  # 40% chance each cycle
                disaster = self.environment.generate_disaster_event()
                print(f"\n⚠️  DISASTER DETECTED!")
                print(f"Type:      {disaster['type']}")
                print(f"Severity:  {disaster['severity']}")
                print(f"Location:  {disaster['location']}")
                print(f"Time:      {disaster['timestamp']}")
                
                # Log disaster
                self.log_event(timestamp, "DISASTER_EVENT", disaster)
            else:
                print("\n✓ No disasters detected")
            
            print("=" * 70 + "\n")
            
            # Stop after 10 perceptions
            if self.perception_count >= 10:
                print("[INFO] Sensor monitoring complete. Stopping agent...")
                await self.agent.stop()
        
        def log_event(self, timestamp, event_type, data):
            """
            Write events to log file.
            """
            with open(self.log_file, "a") as f:
                f.write(f"\n{'='*70}\n")
                f.write(f"[{timestamp}] {event_type}\n")
                f.write(f"{'-'*70}\n")
                for key, value in data.items():
                    f.write(f"{key}: {value}\n")
    
    def __init__(self, jid, password, environment, log_file, verify_security=False):
        super().__init__(jid, password, verify_security=verify_security)
        self.environment = environment
        self.log_file = log_file
    
    async def setup(self):
        """
        Initialize the sensor agent and start perception behavior.
        """
        print(f"\n[SETUP] SensorAgent {self.jid} initializing...")
        print(f"[SETUP] Log file: {self.log_file}")
        
        # create log file
        with open(self.log_file, "w") as f:
            f.write("="*70 + "\n")
            f.write("DISASTER MONITORING SYSTEM - EVENT LOG\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n")
        
        # perception behavior that runs every 3 seconds
        perception = self.PerceptionBehaviour(
            period=3.0,
            environment=self.environment,
            log_file=self.log_file
        )
        self.add_behaviour(perception)
        
        print("[SETUP] Perception behavior activated")
        print("[SETUP] Starting environmental monitoring...\n")


async def main():
    """
    Main function to run the disaster monitoring simulation.
    """
    print("\n" + "="*70)
    print("LAB 2: PERCEPTION AND ENVIRONMENT MODELING")
    print("="*70)
    print("Initializing disaster monitoring system...")
    print("="*70 + "\n")
    
    # new disaster environment
    environment = DisasterEnvironment()
    
    # Log
    log_file = "disaster_events.log"
    
    # sensor agent
    JID = "aockiji@xmpp.jp"
    PASSWORD = "40ck1j1@2077"
    
    agent = SensorAgent(
        jid=JID,
        password=PASSWORD,
        environment=environment,
        log_file=log_file,
        verify_security=False
    )
    
    # Start 
    await agent.start()
    print(f"[INFO] SensorAgent started: {JID}\n")
    
    # while agent is alive
    while agent.is_alive():
        await asyncio.sleep(1)
    
    print("\n" + "="*70)
    print("MONITORING SESSION COMPLETED")
    print("="*70)
    print(f"Events logged to: {log_file}")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[INFO] Monitoring stopped by user")
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")