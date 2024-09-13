import autogen

config_list = [
    {"api_type": "groq", "model": "llama3-70b-8192", "api_key": "A P I K E Y ", "cache_seed": None,"use_docker": False}
]

# Create the agent for tool calling
chatbot = autogen.AssistantAgent(
    name="chatbot",
    system_message="""For NETWORK STATUS and NETWORK TROUBLESHOOTING tasks,
        only use the functions you have been provided with.
        Output 'TERMINATE' when an answer has been provided.""",
    llm_config={"config_list": config_list},
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
    code_execution_config={"use_docker": False}  # Disable Docker for code execution
)
