import json
import os
from typing import Literal, Annotated
import random
import autogen
import re
import logging


config_list = [
    {
        "api_type": "groq",
        "model": "llama3-70b-8192",
        "api_key": "A P I K E Y",
        "cache_seed": None,
        "use_docker": False
    }
]


planner = autogen.ConversableAgent(
    name="Planner",
    system_message="""
    You are a planner responsible for creating a detailed plan to solve tasks.
    - Available Functions:
        1. check_internet_connectivity(device_name: str) -> str
        2. get_memory_usage(system_name: str) -> str
    - Before executing any function, outline your reasoning and specify which functions to use.
    - Ensure all arguments, especially device names like "Ozgur-123", are correctly referenced and not altered.
    - Only use the functions provided above.
    - Output the plan as a list of function calls in the following format:
        1. `check_internet_connectivity("Ozgur-123")`
        2. `get_memory_usage("Ozgur-123")`
    - Output 'PLAN_COMPLETE' once the plan is ready.
    """,
    llm_config={"config_list": config_list},
)


controller = autogen.ConversableAgent(
    name="Controller",
    system_message="""
    You are a controller responsible for executing the plan created by the Planner.
    - Available Functions:
        1. execute_plan(plan: str) -> str
    - execute_plan is a function that takes a plan consisting of a list of function calls and executes them sequentially.
    - Each function call in the plan should be executed using the available tools.
    - Validate all arguments before execution, ensuring that specific identifiers like "Ozgur-123" are correctly used.
    - Provide updates after each function execution.
    - Output 'EXECUTION_COMPLETE' once all functions have been executed.
    """,
    llm_config={"config_list": config_list},
)

chatbot = autogen.ConversableAgent(
    name="Chatbot",
    system_message="""
    For NETWORK STATUS and NETWORK TROUBLESHOOTING tasks:
    - Available Functions:
        1. check_internet_connectivity(device_name: str) -> str
        2. get_memory_usage(system_name: str) -> str
    - Execute the functions as specified by the Controller.
    - Ensure all arguments, especially specific identifiers like "Ozgur-123", are correctly referenced and not altered.
    - Provide results of each function execution.
    - Output 'TERMINATE' when all functions have been executed.
    """,
    llm_config={"config_list": config_list},
)


user_proxy = autogen.ConversableAgent(
    name="User",
    system_message="""
    You are the user interacting with the system.
    - Ensure that all interactions are clear and precise.
    - When specifying devices or interfaces (e.g., "Ozgur-123"), maintain their exact naming to avoid confusion.
    """,
    llm_config={"config_list": config_list},
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False}
)

@user_proxy.register_for_llm(description="The plan to execute tool.")
@controller.register_for_execution()
def execute_plan(plan: Annotated[str, "The plan to execute"]) -> str:
    # Initialize a new user proxy and executor for nested chat
    inner_user_proxy = autogen.ConversableAgent(
        name="Inner_User_Proxy",
        human_input_mode="ALWAYS",
    )
    executor = autogen.ConversableAgent(
        name="Executor",
        system_message="""
        You are an executor responsible for executing the plan.
        - Available Functions:
            1. check_internet_connectivity(device_name: str) -> str
            2. get_memory_usage(system_name: str) -> str
        - Execute each function as specified in the plan.
        - Ensure all arguments, especially "Ozgur-123", are correctly referenced and not altered.
        - Provide results of each function execution.
        - Output 'EXECUTION_COMPLETE' once all functions have been executed.
        """,
        llm_config={"config_list": config_list},
    )    

    
    chat_result = inner_user_proxy.initiate_chat(
        executor,
        message=plan,
        summary_method="reflection_with_llm",
        max_turns=5,
    )

    return chat_result.summary


initial_message="""Why I can not connect internet with device Device-123?"""

groupchat = autogen.GroupChat(agents=[user_proxy, planner, controller,chatbot], messages=[], max_round=4)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})

chat_result = user_proxy.initiate_chat(
    manager,
    message=initial_message,
    summary_method="reflection_with_llm",
    max_turns=5,
)



