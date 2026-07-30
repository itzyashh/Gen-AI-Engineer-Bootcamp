from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from rich.pretty import pprint


load_dotenv()

@tool
def get_weather(city: str):
    """Get Weather for a given City"""
    return "sunny"



model = ChatOpenAI(model="gpt-4o-mini")

agent = create_agent(
    model,
    tools=[get_weather],
    debug=False
)

response1 = agent.invoke({
    "messages":[
        {
            'role': 'user',
            'content': 'How is the weather in Mumbai ?'
        }
    ]
})

pprint(response1)


