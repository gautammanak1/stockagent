from datetime import datetime
from uagents import Agent, Context
from protocol import chat_proto, ChatMessage, create_text_chat, ChatAcknowledgement

agent = Agent(
    name="bob",
    seed="bob recovery phrase 12345678fgjfjfgh8",
    port=8002,
    # endpoint="http://localhost:8002/submit",
    mailbox=True
)

AGENT_ADDRESS = "agent1q0s2005sz2z357rv72kl0nruf4z9h7trxd7qccndj7re4zkf2z3zsf996sl"

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Got acknowledgement from {sender}. Timestamp: {msg.timestamp}, "
                    f"Acknowledged Message ID: {msg.acknowledged_msg_id}")

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    for content in msg.content:
        if content.type == "text":
            ctx.logger.info(f"Received response from {sender}: {content.text}")
        elif content.type == "end-session":
            ctx.logger.info(f"Session ended by {sender}")

    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.utcnow(),
            acknowledged_msg_id=msg.msg_id
        )
    )

@agent.on_event("startup")
async def introduce_agent(ctx: Context):
    ctx.logger.info(f"Hello, I'm agent {agent.name} and my address is {agent.address}.")
    ctx.logger.debug(f"Chat protocol digest: {chat_proto.digest}")
    
    await ctx.send(
        AGENT_ADDRESS,
        # create_text_chat("Generate an invoice for My Business, located at 123 Main St. The invoice is for customer John Doe, with billing contact Jane Doe. The payment is due by 2025-04-10, and payment should be made to Bank XYZ, Account: 123456. The invoice includes the following items: Product A with a quantity of 2 at $10.00 each, and Product B with a quantity of 1 at $25.00. Send the invoice to the email address gautam.kumar@fetch.ai")
        create_text_chat("Give me the details of the AAPL stock ticker. Include the name, market cap, description, exchange, share class shares outstanding, and weighted shares outstanding.")
        # create_text_chat("Analyzes this https://github.com/InsaneNaman/astro-paper-portfolio  GitHub repository.")
        # # create_text_chat("search flight from JFK to LAX on 2025-05-15 for 2 adults") 

    )

agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
# from uagents import Agent, Context, Model

# # Create an agent instance
# agent = Agent(
#     name="Example Agent",
#     port=8002,
#     seed="Example Agent",
#     # endpoint=["http://localhost:8002/submit"]
# )

# # Stock Info Agent address
# stock_info_agent_address = "agent1q0lyz97cyf8xxrd6j380vzrn5tpr0cgc3u7pn2uyfl9w27lxzg8xx009f28"

# # Define request/response models
# class Request(Model):
#     ticker: str

# class Response(Model):
#     name: str
#     market_cap: float
#     description: str
#     exchange: str
#     share_class_shares_outstanding: float
#     weighted_shares_outstanding: float

# # Send request on startup
# @agent.on_event("startup")
# async def startup(ctx: Context):
#     await ctx.send(stock_info_agent_address, Request(ticker="AAPL"))

# # Handle the response
# @agent.on_message(Response)
# async def handle_response(ctx: Context, sender: str, msg: Response):
#     ctx.logger.info(f"Company: {msg.name}")
#     ctx.logger.info(f"Market Cap: ${msg.market_cap:,.2f}")
#     ctx.logger.info(f"Exchange: {msg.exchange}")
#     ctx.logger.info(f"Description: {msg.description}")
#     ctx.logger.info(f"Share Class Shares Outstanding: {msg.share_class_shares_outstanding}")
#     ctx.logger.info(f"Weighted Shares Outstanding: {msg.weighted_shares_outstanding}")

# if __name__ == "__main__":
#     agent.run()