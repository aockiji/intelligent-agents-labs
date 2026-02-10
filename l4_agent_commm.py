import asyncio
import json
from datetime import datetime
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

class Performative:
    """
    FIPA-ACL message performatives for agent communication.
    """
    INFORM = "inform"           # Share information
    REQUEST = "request"         # Request action or information
    PROPOSE = "propose"         # Propose an action
    ACCEPT = "accept-proposal"  # Accept a proposal
    REFUSE = "refuse"          # Refuse a request
    AGREE = "agree"            # Agree to perform action
    CONFIRM = "confirm"        # Confirm truth of statement


# COORDINATOR AGENT

class CoordinatorAgent(Agent):
    """
    Central coordinator that manages disaster response operations.
    Sends REQUESTS to field agents and receives INFORM messages.
    """
    
    class CommunicationBehaviour(CyclicBehaviour):
        def __init__(self, log_file):
            super().__init__()
            self.log_file = log_file
            self.message_count = 0
            self.active_missions = []
        
        async def run(self):
            # Check for incoming messages
            msg = await self.receive(timeout=2)
            
            if msg:
                self.message_count += 1
                await self.handle_incoming_message(msg)
            else:
                # Periodically send requests to field agents
                if self.message_count % 3 == 0:
                    await self.send_status_request()
            
            await asyncio.sleep(2)
        
        async def handle_incoming_message(self, msg):
            """
            Parse incoming ACL messages and trigger appropriate actions.
            """
            performative = msg.metadata.get("performative", "unknown")
            sender = str(msg.sender).split("@")[0]
            
            self.log_message("RECEIVED", msg, sender)
            
            # Parse message body
            try:
                content = json.loads(msg.body)
            except:
                content = {"text": msg.body}
            
            # Handle based on performative
            if performative == Performative.INFORM:
                await self.handle_inform(sender, content)
            
            elif performative == Performative.REQUEST:
                await self.handle_request(sender, content)
            
            elif performative == Performative.AGREE:
                await self.handle_agree(sender, content)
            
            print()  # Blank line for readability
        
        async def handle_inform(self, sender, content):
            """
            Handle INFORM messages (status updates, reports).
            """
            print(f"[COORDINATOR] Received status from {sender}:")
            print(f"  Status: {content.get('status', 'unknown')}")
            
            if 'disaster_detected' in content:
                print(f"  ⚠️  Disaster Alert: {content['disaster_detected']}")
                # Trigger response action
                await self.dispatch_rescue_team(content.get('location', 'unknown'))
        
        async def handle_request(self, sender, content):
            """
            Handle REQUEST messages (assistance needed).
            """
            print(f"[COORDINATOR] Request from {sender}:")
            print(f"  Request: {content.get('request', 'unknown')}")
            
            # Send AGREE response
            response = Message(to=str(sender) + "@404.city")
            response.set_metadata("performative", Performative.AGREE)
            response.body = json.dumps({
                "agreed_action": content.get('request'),
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            await self.send(response)
            self.log_message("SENT", response, sender)
        
        async def handle_agree(self, sender, content):
            """
            Handle AGREE messages (agent agrees to perform action).
            """
            print(f"[COORDINATOR] {sender} agreed to: {content.get('agreed_action')}")
        
        async def send_status_request(self):
            """
            Send REQUEST messages to all field agents for status updates.
            """
            field_agents = ["fieldagent1", "fieldagent2"]
            
            for agent_name in field_agents:
                msg = Message(to=f"{agent_name}@404.city")
                msg.set_metadata("performative", Performative.REQUEST)
                msg.body = json.dumps({
                    "request": "status_update",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                
                await self.send(msg)
                self.log_message("SENT", msg, agent_name)
        
        async def dispatch_rescue_team(self, location):
            """
            Send rescue dispatch request to field agents.
            """
            msg = Message(to="fieldagent1@404.city")
            msg.set_metadata("performative", Performative.REQUEST)
            msg.body = json.dumps({
                "request": "deploy_rescue_team",
                "location": location,
                "priority": "high",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            await self.send(msg)
            self.log_message("SENT", msg, "fieldagent1")
        
        def log_message(self, direction, msg, other_party):
            """
            Log all messages to file and console.
            """
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            performative = msg.metadata.get("performative", "unknown")
            
            log_entry = f"\n{'='*70}\n"
            log_entry += f"[{timestamp}] {direction} - {performative.upper()}\n"
            log_entry += f"{'-'*70}\n"
            log_entry += f"From/To: {other_party}\n"
            log_entry += f"Performative: {performative}\n"
            log_entry += f"Content: {msg.body}\n"
            log_entry += f"{'='*70}\n"
            
            print(log_entry)
            
            with open(self.log_file, "a") as f:
                f.write(log_entry)
    
    def __init__(self, jid, password, log_file, verify_security=False):
        super().__init__(jid, password, verify_security=verify_security)
        self.log_file = log_file
    
    async def setup(self):
        print(f"\n[SETUP] CoordinatorAgent {self.jid} starting...")
        
        # Initialize log file
        with open(self.log_file, "w") as f:
            f.write("="*70 + "\n")
            f.write("AGENT COMMUNICATION LOG - COORDINATOR\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
        
        comm_behaviour = self.CommunicationBehaviour(log_file=self.log_file)
        self.add_behaviour(comm_behaviour)
        
        print("[SETUP] Communication behaviour active\n")


# ============================================================================
# FIELD AGENT
# ============================================================================

class FieldAgent(Agent):
    """
    Field agent that operates in disaster zones.
    Sends INFORM messages and responds to REQUESTS.
    """
    
    class CommunicationBehaviour(CyclicBehaviour):
        def __init__(self, log_file, agent_name):
            super().__init__()
            self.log_file = log_file
            self.agent_name = agent_name
            self.cycle_count = 0
        
        async def run(self):
            self.cycle_count += 1
            
            # Check for incoming messages
            msg = await self.receive(timeout=2)
            
            if msg:
                await self.handle_incoming_message(msg)
            
            # Periodically send status updates
            if self.cycle_count % 4 == 0:
                await self.send_status_inform()
            
            # Randomly detect disasters
            if self.cycle_count % 5 == 0:
                await self.report_disaster()
            
            await asyncio.sleep(2)
        
        async def handle_incoming_message(self, msg):
            """
            Parse and respond to incoming ACL messages.
            """
            performative = msg.metadata.get("performative", "unknown")
            sender = str(msg.sender).split("@")[0]
            
            self.log_message("RECEIVED", msg, sender)
            
            try:
                content = json.loads(msg.body)
            except:
                content = {"text": msg.body}
            
            # Handle REQUEST performatives
            if performative == Performative.REQUEST:
                request_type = content.get("request")
                
                if request_type == "status_update":
                    # Respond with INFORM
                    await self.send_status_inform()
                
                elif request_type == "deploy_rescue_team":
                    # Respond with AGREE
                    response = Message(to=str(msg.sender))
                    response.set_metadata("performative", Performative.AGREE)
                    response.body = json.dumps({
                        "agreed_action": "deploy_rescue_team",
                        "location": content.get("location"),
                        "eta": "5 minutes",
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    
                    await self.send(response)
                    self.log_message("SENT", response, sender)
                    
                    print(f"[{self.agent_name.upper()}] Deploying rescue team to {content.get('location')}\n")
        
        async def send_status_inform(self):
            """
            Send INFORM message with current status.
            """
            msg = Message(to="coordinator@404.city")
            msg.set_metadata("performative", Performative.INFORM)
            msg.body = json.dumps({
                "status": "operational",
                "agent": self.agent_name,
                "location": f"Zone-{self.cycle_count % 10}",
                "resources": "available",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            await self.send(msg)
            self.log_message("SENT", msg, "coordinator")
        
        async def report_disaster(self):
            """
            Send INFORM message about detected disaster.
            """
            disasters = ["Fire", "Flood", "Earthquake", "Building Collapse"]
            disaster_type = disasters[self.cycle_count % len(disasters)]
            
            msg = Message(to="coordinator@404.city")
            msg.set_metadata("performative", Performative.INFORM)
            msg.body = json.dumps({
                "status": "alert",
                "disaster_detected": disaster_type,
                "severity": "high",
                "location": f"Zone-{self.cycle_count % 10}",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            await self.send(msg)
            self.log_message("SENT", msg, "coordinator")
            
            print(f"[{self.agent_name.upper()}] ⚠️  Detected {disaster_type}!\n")
        
        def log_message(self, direction, msg, other_party):
            """
            Log messages to file.
            """
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            performative = msg.metadata.get("performative", "unknown")
            
            log_entry = f"\n{'='*70}\n"
            log_entry += f"[{timestamp}] {direction} - {performative.upper()}\n"
            log_entry += f"{'-'*70}\n"
            log_entry += f"Agent: {self.agent_name}\n"
            log_entry += f"From/To: {other_party}\n"
            log_entry += f"Performative: {performative}\n"
            log_entry += f"Content: {msg.body}\n"
            log_entry += f"{'='*70}\n"
            
            with open(self.log_file, "a") as f:
                f.write(log_entry)
    
    def __init__(self, jid, password, log_file, agent_name, verify_security=False):
        super().__init__(jid, password, verify_security=verify_security)
        self.log_file = log_file
        self.agent_name = agent_name
    
    async def setup(self):
        print(f"[SETUP] {self.agent_name} {self.jid} starting...")
        
        comm_behaviour = self.CommunicationBehaviour(
            log_file=self.log_file,
            agent_name=self.agent_name
        )
        self.add_behaviour(comm_behaviour)
        
        print(f"[SETUP] {self.agent_name} communication active\n")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """
    Main function to run multi-agent communication system.
    """
    print("\n" + "="*70)
    print("LAB 4: AGENT COMMUNICATION USING FIPA-ACL")
    print("="*70)
    print("Initializing multi-agent communication system...")
    print("="*70 + "\n")
    
    # Create log files
    coordinator_log = "coordinator_messages.log"
    field_log = "field_agent_messages.log"
    
    # Create agents
    coordinator = CoordinatorAgent(
        jid="coordinator@404.city",
        password="coord123",
        log_file=coordinator_log,
        verify_security=False
    )
    
    field_agent1 = FieldAgent(
        jid="fieldagent1@404.city",
        password="field123",
        log_file=field_log,
        agent_name="FieldAgent1",
        verify_security=False
    )
    
    field_agent2 = FieldAgent(
        jid="fieldagent2@404.city",
        password="field123",
        log_file=field_log,
        agent_name="FieldAgent2",
        verify_security=False
    )
    
    # Start all agents
    await coordinator.start()
    await field_agent1.start()
    await field_agent2.start()
    
    print("[INFO] All agents started. Communication in progress...\n")
    print("="*70)
    print("Press Ctrl+C to stop (or wait 60 seconds)")
    print("="*70 + "\n")
    
    # Run for 60 seconds
    try:
        await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping agents...")
    
    # Stop all agents
    await coordinator.stop()
    await field_agent1.stop()
    await field_agent2.stop()
    
    print("\n" + "="*70)
    print("COMMUNICATION SESSION COMPLETED")
    print("="*70)
    print(f"Coordinator logs: {coordinator_log}")
    print(f"Field agent logs: {field_log}")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] System stopped by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
