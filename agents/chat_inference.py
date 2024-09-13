# start the conversation

from network_chat import user_proxy, chatbot


res = user_proxy.initiate_chat(
    chatbot,
    message="Is the system connected to the internet?Can you check it by using your tool?",
    summary_method="reflection_with_llm",
)

print(f"LLM SUMMARY: {res.summary['content']}")