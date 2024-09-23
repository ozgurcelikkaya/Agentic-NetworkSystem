import json
import os
from typing import Literal,Annotated
import random
import autogen


config_list = [
    {"api_type": "groq", "model": "llama3-70b-8192", "api_key": "A P I K E Y", "cache_seed": None,"use_docker": False}
]

task = """Why I can not connect to the internet with device4221?Also what is memory usage of device Ozgur-123"""

writer = autogen.AssistantAgent(
    name="Writer",
    llm_config={"config_list": config_list},
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    system_message="""
    You are a planner responsible for creating a detailed plan to solve tasks.

    Available Functions:
        check_internet_connectivity(device_name: str) -> str
        get_memory_usage(system_name: str) -> str
        is_cable_connected(system_name: str) -> str
        is_port_authorized(system_name: str, port_number: int) -> str
        is_firewall_pass_allowed(system_name: str) -> str
        get_most_cpu(system_name: str) -> str
        check_interface_status(system_name: str) ->str
    Before executing any function, outline your reasoning and specify which functions to use.
    YOU DO NOT HAVE TO USE ALL FUNCTIONS GIVEN TO YOU FOR A PROBLEM.
    USE ONLY FUNCTIONS THAT ARE NECESSARY FOR THE PROBLEMS. For example if user asked for memory usage of "device-123" just use get_memory_usage. Procedure is same for troubleshooting.
    Ensure all arguments, especially device names like "Ozgur-123", are correctly referenced and not altered.
    Only use the functions provided above.
    Output the plan as a list of function calls in the following example format:
        check_internet_connectivity("Ozgur-123")
        is_port_authorized("Ozgur-123", 8080)
    Output once the plan is ready.
    OUTPUT 'TERMINATE' when you receive output from critic.
    """,
)

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    system_message="""For NETWORK STATUS and NETWORK TROUBLESHOOTING tasks:
    - Before executing any function, explain your reasoning and specify which function you will use.
    - Only use the functions you have been provided with:
    check_internet_connectivity(device_name: str) -> str
    get_memory_usage(system_name: str) -> str
    is_cable_connected(system_name: str) -> str
    is_port_authorized(system_name: str, port_number: int) -> str
    is_firewall_pass_allowed(system_name: str) -> str
    get_most_cpu(system_name: str) -> str
    check_interface_status(system_name: str) ->str
    - Observe Planner Agent's plan and Summarize it as a plan.
    OUTPUT 'TERMINATE' when you are done.""",
    code_execution_config={
        "last_n_messages": 1,
        "work_dir": "tasks",
        "use_docker": False,
    },  
)

critic = autogen.AssistantAgent(
    name="Critic",
    llm_config={"config_list": config_list},
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    system_message="""
    You are a controller, known for your thoroughness and commitment to standards.
    You are a controller responsible for controlling the plan and its execution.
    BE AWARE OF planner agent system prompt:
    'Available Functions:
        check_internet_connectivity(device_name: str) -> str
        get_memory_usage(system_name: str) -> str
        is_cable_connected(system_name: str) -> str
        is_port_authorized(system_name: str, port_number: int) -> str
        is_firewall_pass_allowed(system_name: str) -> str
        get_most_cpu(system_name: str) -> str
        check_interface_status(system_name: str) ->str
    Before executing any function, outline your reasoning and specify which functions to use.
    YOU DO NOT HAVE TO USE ALL FUNCTIONS GIVEN TO YOU FOR A PROBLEM.
    USE ONLY FUNCTIONS THAT ARE NECESSARY FOR THE PROBLEMS. For example if user asked for memory usage of "device-123" just use get_memory_usage. Procedure is same for troubleshooting.
    Ensure all arguments, especially device names like "Ozgur-123", are correctly referenced and not altered.
    Only use the functions provided above.
    Output the plan as a list of function calls in the following example format:
        check_internet_connectivity("Ozgur-123")
        is_port_authorized("Ozgur-123", 8080)
    Output once the plan is ready.'
    OUTPUT 'TERMINATE' when you got function outputs from Critic Executor.
    """,
)

critic_executor = autogen.UserProxyAgent(
    name="Critic_Executor",
    human_input_mode="NEVER",
    # is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    code_execution_config={
        "last_n_messages": 1,
        "work_dir": "tasks",
        "use_docker": False,
    },  
)


def reflection_message(recipient, messages, sender, config):
    print("Reflecting...", "controller")
    return f"Reflect and provide critique on the following plan. \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"


user_proxy.register_nested_chats(
    [{"recipient": critic, "message": reflection_message, "summary_method": "last_msg", "max_turns": 1}],
    trigger=writer,  # condition=my_condition,
)


@critic_executor.register_for_execution()
@critic.register_for_llm(name="get_memory_usage", description="Retrieves the current memory usage of the system as a percentage.")
def get_memory_usage(system_name: Annotated[str, "Name of the system to check"]) -> str:
    # Simulated memory usage percentage
    memory_usage = random.uniform(0, 100)
    return f"{system_name} memory usage: {memory_usage:.2f}%"

@critic_executor.register_for_execution()
@critic.register_for_llm(name="check_internet_connectivity",description="Verifies that the device can connect to the internet.")
def check_internet_connectivity(device_name: Annotated[str, "Name of the device to check"]) -> str:
    # Default simulated result: device is connected
    connected_devices = ["Device-123", "Device-456", "Device-789"]
    
    if device_name in connected_devices:
        return f"{device_name} is connected to the internet."
    else:
        return f"{device_name} is not connected to the internet."

@critic_executor.register_for_execution()
@critic.register_for_llm(name="is_cable_connected",description="Checks if the cable is connected to the system.")
def is_cable_connected(system_name: Annotated[str, "Name of the system to check"]) -> str:
    # Simulated cable connection check
    cable_connected = random.choice([True, False])
    return f"Cable connected to {system_name}: {cable_connected}"

@critic_executor.register_for_execution()
@critic.register_for_llm(name="is_port_authorized",description="Checks if the specified port is authorized for use.")
def is_port_authorized(system_name: Annotated[str, "Name of the system to check"],
                       port_number: Annotated[int, "Port number to check"]) -> str:
    # Simulated port authorization check
    port_authorized = random.choice([True, False])
    return f"Port {port_number} on {system_name} authorized: {port_authorized}"

@critic_executor.register_for_execution()
@critic.register_for_llm(name="is_firewall_pass_allowed",description="Checks if there is permission to pass through the firewall.")
def is_firewall_pass_allowed(system_name: Annotated[str, "Name of the system to check"]) -> str:
    # Simulated firewall permission check
    firewall_pass_allowed = random.choice([True, False])
    return f"Firewall pass permission for {system_name}: {firewall_pass_allowed}"


def reflection_message_no_harm(recipient, messages, sender, config):
    print("Reflecting...", "controller executor")
    return f"Reflect and provide critique on the following plan. Ensure it does not use unnecessary function. You can use tools to check it. \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"


user_proxy.register_nested_chats(
    [
        {
            "sender": critic_executor,
            "recipient": critic,
            "message": reflection_message_no_harm,
            "max_turns": 4,
            "summary_method": "last_msg",
        }
    ],
    trigger=writer,  
)

res = user_proxy.initiate_chat(recipient=writer, message=task, max_turns=4, summary_method="last_msg")