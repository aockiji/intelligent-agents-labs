"""
LAB 3: GOALS, EVENTS, AND REACTIVE BEHAVIOR
Student: [Your Name]
Date: January 28, 2026

This program implements:
1. Rescue and response goals for disaster management
2. Event-triggered behavior based on sensor reports
3. Finite State Machine (FSM) for reactive agent behavior
"""

import asyncio
import random
from datetime import datetime
from enum import Enum
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour


# ============================================================================
# FSM STATES AND GOALS
# ============================================================================

class AgentState(Enum):
    """
    Finite State Machine states for the rescue agent.
    """
    IDLE = "IDLE"
    MONITORING = "MONITORING"
    ASSESSING = "ASSESSING"
    RESPONDING = "RESPONDING"
    RESCUING = "RESCUING"
    EVACUATING = "EVACUATING"
    RECOVERY = "RECOVERY"


class Goal(Enum):
    """
    Agent goals for disaster response.
    """
    MAINTAIN_SAFETY = "Maintain Safety"
    DETECT_DISASTERS = "Detect Disasters"
    ASSESS_DAMAGE = "Assess Damage"
    RESCUE_VICTIMS = "Rescue Victims"
    EVACUATE_AREA = "Evacuate Area"
    COORDINATE_RESPONSE = "Coordinate Response"


# ============================================================================
# EVENT CLASSES
# ============================================================================

class DisasterEvent:
    """
    Represents a disaster event that triggers agent behavior.
    """
    def __init__(self, event_type, severity, location):
        self.event_type = event_type
        self.severity = severity
        self.location = location
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def __str__(self):
        return f"{self.event_type} (Severity: {self.severity}) at {self.location}"


class SensorReport:
    """
    Environmental sensor report that can trigger events.
    """
    def __init__(self):
        self.temperature = random.uniform(20, 45)
        self.wind_speed = random.uniform(0, 120)
        self.water_level = random.uniform(0, 8)
        self.structural_damage = random.uniform(0, 100)
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def detect_disaster(self):
        """
        Analyze sensor data to detect disaster events.
        Returns DisasterEvent or None.
        """
        # Check for fire (high temperature)
        if self.temperature > 40:
            return DisasterEvent("Fire", self._get_severity(self.temperature, 40, 50), "Fire Zone")
        
        # Check for flood (high water level)
        if self.water_level > 5:
            return DisasterEvent("Flood", self._get_severity(self.water_level, 5, 10), "Flood Zone")
        
        # Check for hurricane (high wind speed)
        if self.wind_speed > 80:
            return DisasterEvent("Hurricane", self._get_severity(self.wind_speed, 80, 120), "Storm Zone")
        
        # Check for structural collapse (high damage)
        if self.structural_damage > 60:
            return DisasterEvent("Building Collapse", self._get_severity(self.structural_damage, 60, 100), "Collapse Zone")
        
        return None
    
    def _get_severity(self, value, min_threshold, max_threshold):
        """
        Calculate severity level based on sensor value.
        """
        range_size = max_threshold - min_threshold
        position = (value - min_threshold) / range_size
        
        if position < 0.33:
            return "Medium"
        elif position < 0.66:
            return "High"
        else:
            return "Critical"


# ============================================================================
# REACTIVE AGENT WITH FSM
# ============================================================================

class ReactiveRescueAgent(Agent):
    """
    Rescue agent with Finite State Machine for reactive behavior.
    """
    
    class FSMBehaviour(CyclicBehaviour):
        """
        FSM-based behavior that reacts to events and pursues goals.
        """
        
        def __init__(self, trace_file):
            super().__init__()
            self.state = AgentState.IDLE
            self.current_goal = Goal.MAINTAIN_SAFETY
            self.trace_file = trace_file
            self.cycle_count = 0
            self.event_queue = []
        
        async def run(self):
            """
            Main FSM loop: sense, decide, act.
            """
            self.cycle_count += 1
            
            # Generate sensor report
            sensor_report = SensorReport()
            
            # Check for disasters
            event = sensor_report.detect_disaster()
            if event:
                self.event_queue.append(event)
            
            # Run FSM
            self.log_trace(f"\n{'='*70}")
            self.log_trace(f"CYCLE #{self.cycle_count} @ {datetime.now().strftime('%H:%M:%S')}")
            self.log_trace(f"{'='*70}")
            self.log_trace(f"Current State: {self.state.value}")
            self.log_trace(f"Current Goal: {self.current_goal.value}")
            
            # Display sensor readings
            self.log_trace(f"\n[SENSOR READINGS]")
            self.log_trace(f"  Temperature: {sensor_report.temperature:.2f}°C")
            self.log_trace(f"  Wind Speed: {sensor_report.wind_speed:.2f} km/h")
            self.log_trace(f"  Water Level: {sensor_report.water_level:.2f} m")
            self.log_trace(f"  Structural Damage: {sensor_report.structural_damage:.2f}%")
            
            # Process events and transition states
            if self.event_queue:
                event = self.event_queue.pop(0)
                self.log_trace(f"\n[EVENT DETECTED] ⚠️  {event}")
                self.handle_event(event)
            else:
                self.log_trace(f"\n[STATUS] ✓ No events detected")
            
            # Execute current state behavior
            self.execute_state_behavior()
            
            self.log_trace(f"{'='*70}\n")
            
            # Stop after 15 cycles
            if self.cycle_count >= 15:
                self.log_trace(f"\n[INFO] Simulation complete. Agent stopping...\n")
                await self.agent.stop()
            
            await asyncio.sleep(2)
        
        def handle_event(self, event):
            """
            Event-triggered state transitions (FSM logic).
            """
            self.log_trace(f"\n[FSM TRANSITION]")
            
            if self.state == AgentState.IDLE or self.state == AgentState.MONITORING:
                # Transition to assessing when disaster detected
                self.log_trace(f"  {self.state.value} → ASSESSING")
                self.state = AgentState.ASSESSING
                self.current_goal = Goal.ASSESS_DAMAGE
            
            elif self.state == AgentState.ASSESSING:
                # Transition based on severity
                if event.severity == "Critical":
                    self.log_trace(f"  ASSESSING → RESCUING (Critical severity)")
                    self.state = AgentState.RESCUING
                    self.current_goal = Goal.RESCUE_VICTIMS
                elif event.severity == "High":
                    self.log_trace(f"  ASSESSING → EVACUATING (High severity)")
                    self.state = AgentState.EVACUATING
                    self.current_goal = Goal.EVACUATE_AREA
                else:
                    self.log_trace(f"  ASSESSING → RESPONDING (Medium severity)")
                    self.state = AgentState.RESPONDING
                    self.current_goal = Goal.COORDINATE_RESPONSE
            
            elif self.state in [AgentState.RESPONDING, AgentState.RESCUING, AgentState.EVACUATING]:
                # Continue with current response or move to recovery
                if random.random() < 0.3:  # 30% chance to complete
                    self.log_trace(f"  {self.state.value} → RECOVERY (Task completed)")
                    self.state = AgentState.RECOVERY
                    self.current_goal = Goal.COORDINATE_RESPONSE
                else:
                    self.log_trace(f"  {self.state.value} → {self.state.value} (Continuing)")
            
            elif self.state == AgentState.RECOVERY:
                # Return to monitoring after recovery
                self.log_trace(f"  RECOVERY → MONITORING (Recovery complete)")
                self.state = AgentState.MONITORING
                self.current_goal = Goal.DETECT_DISASTERS
        
        def execute_state_behavior(self):
            """
            Execute actions based on current state.
            """
            self.log_trace(f"\n[ACTIONS]")
            
            if self.state == AgentState.IDLE:
                self.log_trace(f"  → Initializing systems...")
                self.state = AgentState.MONITORING
            
            elif self.state == AgentState.MONITORING:
                self.log_trace(f"  → Monitoring environment for disasters")
                self.log_trace(f"  → Running sensor scans")
            
            elif self.state == AgentState.ASSESSING:
                self.log_trace(f"  → Analyzing disaster impact")
                self.log_trace(f"  → Determining response priority")
                self.log_trace(f"  → Calculating resource requirements")
            
            elif self.state == AgentState.RESPONDING:
                self.log_trace(f"  → Deploying emergency response teams")
                self.log_trace(f"  → Establishing communication channels")
                self.log_trace(f"  → Coordinating with other agents")
            
            elif self.state == AgentState.RESCUING:
                self.log_trace(f"  → Locating victims")
                self.log_trace(f"  → Deploying rescue teams")
                self.log_trace(f"  → Providing medical assistance")
            
            elif self.state == AgentState.EVACUATING:
                self.log_trace(f"  → Issuing evacuation orders")
                self.log_trace(f"  → Opening evacuation routes")
                self.log_trace(f"  → Guiding civilians to safety")
            
            elif self.state == AgentState.RECOVERY:
                self.log_trace(f"  → Assessing residual risks")
                self.log_trace(f"  → Coordinating cleanup operations")
                self.log_trace(f"  → Preparing for next incident")
        
        def log_trace(self, message):
            """
            Log execution trace to file and console.
            """
            print(message)
            with open(self.trace_file, "a") as f:
                f.write(message + "\n")
    
    def __init__(self, jid, password, trace_file, verify_security=False):
        super().__init__(jid, password, verify_security=verify_security)
        self.trace_file = trace_file
    
    async def setup(self):
        """
        Initialize the reactive rescue agent.
        """
        print(f"\n[SETUP] ReactiveRescueAgent {self.jid} initializing...")
        print(f"[SETUP] Trace file: {self.trace_file}")
        
        # Initialize trace file
        with open(self.trace_file, "w") as f:
            f.write("="*70 + "\n")
            f.write("REACTIVE RESCUE AGENT - EXECUTION TRACE\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
        
        # Add FSM behavior
        fsm = self.FSMBehaviour(trace_file=self.trace_file)
        self.add_behaviour(fsm)
        
        print("[SETUP] FSM behavior activated")
        print("[SETUP] Starting reactive agent...\n")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """
    Main function to run the reactive agent simulation.
    """
    print("\n" + "="*70)
    print("LAB 3: GOALS, EVENTS, AND REACTIVE BEHAVIOR")
    print("="*70)
    print("Initializing Finite State Machine agent...")
    print("="*70 + "\n")
    
    trace_file = "execution_trace.log"
    
    # Create reactive rescue agent
    # IMPORTANT: Change JID to your unique username!
    JID = "rescueagent123@404.city"
    PASSWORD = "rescuepass123"
    
    agent = ReactiveRescueAgent(
        jid=JID,
        password=PASSWORD,
        trace_file=trace_file,
        verify_security=False
    )
    
    # Start the agent
    await agent.start()
    print(f"[INFO] ReactiveRescueAgent started: {JID}\n")
    
    # Keep running while agent is alive
    while agent.is_alive():
        await asyncio.sleep(1)
    
    print("\n" + "="*70)
    print("SIMULATION COMPLETED")
    print("="*70)
    print(f"Execution trace saved to: {trace_file}")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[INFO] Agent stopped by user")
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
"""
LAB 3: GOALS, EVENTS, AND REACTIVE BEHAVIOR
Student: [Your Name]
Date: January 28, 2026

This program implements:
1. Rescue and response goals for disaster management
2. Event-triggered behavior based on sensor reports
3. Finite State Machine (FSM) for reactive agent behavior
"""

import asyncio
import random
from datetime import datetime
from enum import Enum
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour


# ============================================================================
# FSM STATES AND GOALS
# ============================================================================

class AgentState(Enum):
    """
    Finite State Machine states for the rescue agent.
    """
    IDLE = "IDLE"
    MONITORING = "MONITORING"
    ASSESSING = "ASSESSING"
    RESPONDING = "RESPONDING"
    RESCUING = "RESCUING"
    EVACUATING = "EVACUATING"
    RECOVERY = "RECOVERY"


class Goal(Enum):
    """
    Agent goals for disaster response.
    """
    MAINTAIN_SAFETY = "Maintain Safety"
    DETECT_DISASTERS = "Detect Disasters"
    ASSESS_DAMAGE = "Assess Damage"
    RESCUE_VICTIMS = "Rescue Victims"
    EVACUATE_AREA = "Evacuate Area"
    COORDINATE_RESPONSE = "Coordinate Response"


# ============================================================================
# EVENT CLASSES
# ============================================================================

class DisasterEvent:
    """
    Represents a disaster event that triggers agent behavior.
    """
    def __init__(self, event_type, severity, location):
        self.event_type = event_type
        self.severity = severity
        self.location = location
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def __str__(self):
        return f"{self.event_type} (Severity: {self.severity}) at {self.location}"


class SensorReport:
    """
    Environmental sensor report that can trigger events.
    """
    def __init__(self):
        self.temperature = random.uniform(20, 45)
        self.wind_speed = random.uniform(0, 120)
        self.water_level = random.uniform(0, 8)
        self.structural_damage = random.uniform(0, 100)
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def detect_disaster(self):
        """
        Analyze sensor data to detect disaster events.
        Returns DisasterEvent or None.
        """
        # Check for fire (high temperature)
        if self.temperature > 40:
            return DisasterEvent("Fire", self._get_severity(self.temperature, 40, 50), "Fire Zone")
        
        # Check for flood (high water level)
        if self.water_level > 5:
            return DisasterEvent("Flood", self._get_severity(self.water_level, 5, 10), "Flood Zone")
        
        # Check for hurricane (high wind speed)
        if self.wind_speed > 80:
            return DisasterEvent("Hurricane", self._get_severity(self.wind_speed, 80, 120), "Storm Zone")
        
        # Check for structural collapse (high damage)
        if self.structural_damage > 60:
            return DisasterEvent("Building Collapse", self._get_severity(self.structural_damage, 60, 100), "Collapse Zone")
        
        return None
    
    def _get_severity(self, value, min_threshold, max_threshold):
        """
        Calculate severity level based on sensor value.
        """
        range_size = max_threshold - min_threshold
        position = (value - min_threshold) / range_size
        
        if position < 0.33:
            return "Medium"
        elif position < 0.66:
            return "High"
        else:
            return "Critical"


# ============================================================================
# REACTIVE AGENT WITH FSM
# ============================================================================

class ReactiveRescueAgent(Agent):
    """
    Rescue agent with Finite State Machine for reactive behavior.
    """
    
    class FSMBehaviour(CyclicBehaviour):
        """
        FSM-based behavior that reacts to events and pursues goals.
        """
        
        def __init__(self, trace_file):
            super().__init__()
            self.state = AgentState.IDLE
            self.current_goal = Goal.MAINTAIN_SAFETY
            self.trace_file = trace_file
            self.cycle_count = 0
            self.event_queue = []
        
        async def run(self):
            """
            Main FSM loop: sense, decide, act.
            """
            self.cycle_count += 1
            
            # Generate sensor report
            sensor_report = SensorReport()
            
            # Check for disasters
            event = sensor_report.detect_disaster()
            if event:
                self.event_queue.append(event)
            
            # Run FSM
            self.log_trace(f"\n{'='*70}")
            self.log_trace(f"CYCLE #{self.cycle_count} @ {datetime.now().strftime('%H:%M:%S')}")
            self.log_trace(f"{'='*70}")
            self.log_trace(f"Current State: {self.state.value}")
            self.log_trace(f"Current Goal: {self.current_goal.value}")
            
            # Display sensor readings
            self.log_trace(f"\n[SENSOR READINGS]")
            self.log_trace(f"  Temperature: {sensor_report.temperature:.2f}°C")
            self.log_trace(f"  Wind Speed: {sensor_report.wind_speed:.2f} km/h")
            self.log_trace(f"  Water Level: {sensor_report.water_level:.2f} m")
            self.log_trace(f"  Structural Damage: {sensor_report.structural_damage:.2f}%")
            
            # Process events and transition states
            if self.event_queue:
                event = self.event_queue.pop(0)
                self.log_trace(f"\n[EVENT DETECTED] ⚠️  {event}")
                self.handle_event(event)
            else:
                self.log_trace(f"\n[STATUS] ✓ No events detected")
            
            # Execute current state behavior
            self.execute_state_behavior()
            
            self.log_trace(f"{'='*70}\n")
            
            # Stop after 15 cycles
            if self.cycle_count >= 15:
                self.log_trace(f"\n[INFO] Simulation complete. Agent stopping...\n")
                await self.agent.stop()
            
            await asyncio.sleep(2)
        
        def handle_event(self, event):
            """
            Event-triggered state transitions (FSM logic).
            """
            self.log_trace(f"\n[FSM TRANSITION]")
            
            if self.state == AgentState.IDLE or self.state == AgentState.MONITORING:
                # Transition to assessing when disaster detected
                self.log_trace(f"  {self.state.value} → ASSESSING")
                self.state = AgentState.ASSESSING
                self.current_goal = Goal.ASSESS_DAMAGE
            
            elif self.state == AgentState.ASSESSING:
                # Transition based on severity
                if event.severity == "Critical":
                    self.log_trace(f"  ASSESSING → RESCUING (Critical severity)")
                    self.state = AgentState.RESCUING
                    self.current_goal = Goal.RESCUE_VICTIMS
                elif event.severity == "High":
                    self.log_trace(f"  ASSESSING → EVACUATING (High severity)")
                    self.state = AgentState.EVACUATING
                    self.current_goal = Goal.EVACUATE_AREA
                else:
                    self.log_trace(f"  ASSESSING → RESPONDING (Medium severity)")
                    self.state = AgentState.RESPONDING
                    self.current_goal = Goal.COORDINATE_RESPONSE
            
            elif self.state in [AgentState.RESPONDING, AgentState.RESCUING, AgentState.EVACUATING]:
                # Continue with current response or move to recovery
                if random.random() < 0.3:  # 30% chance to complete
                    self.log_trace(f"  {self.state.value} → RECOVERY (Task completed)")
                    self.state = AgentState.RECOVERY
                    self.current_goal = Goal.COORDINATE_RESPONSE
                else:
                    self.log_trace(f"  {self.state.value} → {self.state.value} (Continuing)")
            
            elif self.state == AgentState.RECOVERY:
                # Return to monitoring after recovery
                self.log_trace(f"  RECOVERY → MONITORING (Recovery complete)")
                self.state = AgentState.MONITORING
                self.current_goal = Goal.DETECT_DISASTERS
        
        def execute_state_behavior(self):
            """
            Execute actions based on current state.
            """
            self.log_trace(f"\n[ACTIONS]")
            
            if self.state == AgentState.IDLE:
                self.log_trace(f"  → Initializing systems...")
                self.state = AgentState.MONITORING
            
            elif self.state == AgentState.MONITORING:
                self.log_trace(f"  → Monitoring environment for disasters")
                self.log_trace(f"  → Running sensor scans")
            
            elif self.state == AgentState.ASSESSING:
                self.log_trace(f"  → Analyzing disaster impact")
                self.log_trace(f"  → Determining response priority")
                self.log_trace(f"  → Calculating resource requirements")
            
            elif self.state == AgentState.RESPONDING:
                self.log_trace(f"  → Deploying emergency response teams")
                self.log_trace(f"  → Establishing communication channels")
                self.log_trace(f"  → Coordinating with other agents")
            
            elif self.state == AgentState.RESCUING:
                self.log_trace(f"  → Locating victims")
                self.log_trace(f"  → Deploying rescue teams")
                self.log_trace(f"  → Providing medical assistance")
            
            elif self.state == AgentState.EVACUATING:
                self.log_trace(f"  → Issuing evacuation orders")
                self.log_trace(f"  → Opening evacuation routes")
                self.log_trace(f"  → Guiding civilians to safety")
            
            elif self.state == AgentState.RECOVERY:
                self.log_trace(f"  → Assessing residual risks")
                self.log_trace(f"  → Coordinating cleanup operations")
                self.log_trace(f"  → Preparing for next incident")
        
        def log_trace(self, message):
            """
            Log execution trace to file and console.
            """
            print(message)
            with open(self.trace_file, "a") as f:
                f.write(message + "\n")
    
    def __init__(self, jid, password, trace_file, verify_security=False):
        super().__init__(jid, password, verify_security=verify_security)
        self.trace_file = trace_file
    
    async def setup(self):
        print(f"\n[SETUP] ReactiveRescueAgent {self.jid} initializing...")
        print(f"[SETUP] Trace file: {self.trace_file}")
        
        # trace file
        with open(self.trace_file, "w") as f:
            f.write("="*70 + "\n")
            f.write("REACTIVE RESCUE AGENT - EXECUTION TRACE\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
        
        # FSM behavior
        fsm = self.FSMBehaviour(trace_file=self.trace_file)
        self.add_behaviour(fsm)
        
        print("[SETUP] FSM behavior activated")
        print("[SETUP] Starting reactive agent...\n")


# main 

async def main():
    """
    Main function to run the reactive agent simulation.
    """
    print("\n" + "="*70)
    print("LAB 3: GOALS, EVENTS, AND REACTIVE BEHAVIOR")
    print("="*70)
    print("Initializing Finite State Machine agent...")
    print("="*70 + "\n")
    
    trace_file = "l3_execution_trace.log"
    
    # Create reactive rescue agent
    JID = "aockiji@xmpp.jp"
    PASSWORD = "40ck1j1@2077"
    
    agent = ReactiveRescueAgent(
        jid=JID,
        password=PASSWORD,
        trace_file=trace_file,
        verify_security=False
    )
    
    # Start the agent
    await agent.start()
    print(f"[INFO] ReactiveRescueAgent started: {JID}\n")
    
    # running while agent is alive
    while agent.is_alive():
        await asyncio.sleep(1)
    
    print("\n" + "="*70)
    print("SIMULATION COMPLETED")
    print("="*70)
    print(f"Execution trace saved to: {trace_file}")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[INFO] Agent stopped by user")
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
