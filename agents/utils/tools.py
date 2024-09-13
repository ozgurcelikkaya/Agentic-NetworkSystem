import json
import os
from typing import Literal,Annotated
import random
import autogen
from network_chat import user_proxy, chatbot


# Simulated function to check interface status
@user_proxy.register_for_execution()
@chatbot.register_for_llm(description="Checks whether the interface is up (active) or down (inactive).")
def check_interface_status(interface: Annotated[str, "Name of the interface to check"]) -> str:
    # Simulated check: randomly returns "down" or "active"
    status = random.choice(["down", "active"])
    return f"Interface {interface} is {status}"

# Simulated function to get the system that used the most CPU today
@user_proxy.register_for_execution()
@chatbot.register_for_llm(description="Returns the system that used the most CPU today.")
def get_most_cpu() -> str:
    # Default simulated CPU usage data
    cpu_usage_data = {
        "System-A": 45.3,
        "System-B": 78.9,
        "System-C": 65.4,
        "System-D": 22.1
    }
    
    # Find the system with the highest CPU usage
    most_cpu_system = max(cpu_usage_data, key=cpu_usage_data.get)
    most_cpu_value = cpu_usage_data[most_cpu_system]
    
    return f"The system that used the most CPU today is {most_cpu_system} with {most_cpu_value:.2f}% usage."

# Simulated function to get memory usage
@user_proxy.register_for_execution()
@chatbot.register_for_llm(description="Retrieves the current memory usage of the system as a percentage.")
def get_memory_usage(system_name: Annotated[str, "Name of the system to check"]) -> str:
    # Simulated memory usage percentage
    memory_usage = random.uniform(0, 100)
    return f"{system_name} memory usage: {memory_usage:.2f}%"

# Simulated function to check internet connectivity
@user_proxy.register_for_execution()
@chatbot.register_for_llm(description="Verifies that the device can connect to the internet.")
def check_internet_connectivity(device_name: Annotated[str, "Name of the device to check"]) -> str:
    # Default simulated result: device is connected
    connected_devices = ["Device-123", "Device-456", "Device-789"]
    
    if device_name in connected_devices:
        return f"{device_name} is connected to the internet."
    else:
        return f"{device_name} is not connected to the internet."