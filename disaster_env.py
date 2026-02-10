import asyncio
import random
from datetime import datetime
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour


class DisasterEnvironment:
    """
    Simulates a disaster environment with various conditions.
    Generates random disaster events with different severity levels.
    """
    
    def __init__(self):
        self.disaster_types = [
            "Earthquake",
            "Flood",
            "Fire",
            "Hurricane",
            "Tornado",
            "Landslide"
        ]
        
        self.severity_levels = ["Low", "Medium", "High", "Critical"]
        
        # Environmental parameters
        self.temperature = 25.0  # Celsius
        self.humidity = 50.0     # Percentage
        self.wind_speed = 10.0   # km/h
        self.water_level = 0.0   # meters
        self.structural_damage = 0.0  # Percentage
    
    def update_conditions(self):
        """
        Randomly update environmental conditions.
        Simulates changing environment over time.
        """
        self.temperature += random.uniform(-2, 2)
        self.humidity += random.uniform(-5, 5)
        self.wind_speed += random.uniform(-3, 3)
        self.water_level += random.uniform(-0.5, 0.5)
        self.structural_damage += random.uniform(0, 2)
        
        # reasonable ranges
        self.temperature = max(0, min(50, self.temperature))
        self.humidity = max(0, min(100, self.humidity))
        self.wind_speed = max(0, min(150, self.wind_speed))
        self.water_level = max(0, min(10, self.water_level))
        self.structural_damage = max(0, min(100, self.structural_damage))
    
    def generate_disaster_event(self):
        """
        Generate a random disaster event.
        Returns a dictionary with disaster details.
        """
        disaster_type = random.choice(self.disaster_types)
        severity = random.choice(self.severity_levels)
        
        # adjust based on disaster
        if disaster_type == "Fire":
            self.temperature += random.uniform(5, 15)
        elif disaster_type == "Flood":
            self.water_level += random.uniform(1, 3)
        elif disaster_type in ["Hurricane", "Tornado"]:
            self.wind_speed += random.uniform(20, 50)
        elif disaster_type == "Earthquake":
            self.structural_damage += random.uniform(5, 20)
        
        return {
            "type": disaster_type,
            "severity": severity,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "location": f"Zone-{random.randint(1, 10)}"
        }
    
    def get_current_state(self):
        """
        Returns current environmental state.
        """
        return {
            "temperature": round(self.temperature, 2),
            "humidity": round(self.humidity, 2),
            "wind_speed": round(self.wind_speed, 2),
            "water_level": round(self.water_level, 2),
            "structural_damage": round(self.structural_damage, 2)
        }

