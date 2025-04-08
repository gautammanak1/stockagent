
import os
from typing import Any, Literal, Dict
from datetime import datetime
from pydantic.v1 import UUID4
from uagents import Model, Protocol, Context
from uuid import uuid4
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)

from stock_info_agent.stockinfoagent import (
    get_stock_info,
    get_historical_stock_data,
    StockInfoRequest,
    HistoricalDataRequest
)


AI_AGENT_ADDRESS = 'agent1q0h70caed8ax769shpemapzkyk65uscw4xwk6dc4t3emvp5jdcvqs9xs32y'

if not AI_AGENT_ADDRESS:
    raise ValueError("AI_AGENT_ADDRESS not set")


class StartSessionContent(Model):
    type: Literal["start-session"]

class EndSessionContent(Model):
    type: Literal["end-session"]

# Helper functions to create chat messages
def create_text_chat(text: str) -> ChatMessage:
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)],
    )

def create_end_session_chat() -> ChatMessage:
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[EndSessionContent(type="end-session")],
    )


chat_proto = Protocol(spec=chat_protocol_spec)


struct_output_client_proto = Protocol(
    name="StructuredOutputClientProtocol",
    version="0.1.0"
)


class StructuredOutputPrompt(Model):
    prompt: str
    output_schema: dict[str, Any]

class StructuredOutputResponse(Model):
    output: dict[str, Any]


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    if msg.content and isinstance(msg.content[0], TextContent):
        ctx.logger.info(f"Got a message from {sender}: {msg.content[0].text}")
    else:
        ctx.logger.info(f"Got a message from {sender} with content type: {type(msg.content[0]).__name__ if msg.content else 'empty'}")
    
    ctx.storage.set(str(ctx.session), sender)
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.utcnow(),
            acknowledged_msg_id=msg.msg_id,
            metadata={
                "device": "mobile",
                "status": "delivered"
            }
        )
    )
    
    # Process each content item in the message
    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Got a start session message from {sender}")
            continue
        elif isinstance(item, TextContent):
            prompt = item.text.lower()
            ctx.logger.info(f"Sending structured output prompt to {AI_AGENT_ADDRESS}")
            
            
            if "historical" in prompt or "past" in prompt or "history" in prompt:
                await ctx.send(
                    AI_AGENT_ADDRESS,
                    StructuredOutputPrompt(
                        prompt=prompt,
                        output_schema=HistoricalDataRequest.schema()
                    )
                )
            else:
                await ctx.send(
                    AI_AGENT_ADDRESS,
                    StructuredOutputPrompt(
                        prompt=prompt,
                        output_schema=StockInfoRequest.schema()
                    )
                )
            ctx.logger.info(f"Sent structured output prompt to {AI_AGENT_ADDRESS}")
        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"Got an end session message from {sender}")
            continue
        else:
            ctx.logger.info(f"Got unexpected content from {sender}")


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Got an acknowledgement from {sender} for {msg.acknowledged_msg_id}")


@struct_output_client_proto.on_message(StructuredOutputResponse)
async def handle_structured_output_response(
    ctx: Context, sender: str, msg: StructuredOutputResponse
):
    ctx.logger.info(f"Received structured output response from {sender}")
    session_sender = ctx.storage.get(str(ctx.session))
    
    if session_sender is None:
        ctx.logger.error("Discarding message because no session sender found in storage")
        return

    ctx.logger.info(f"Parsed output: {str(msg.output)}")
    
    try:

        if "ticker" in msg.output and all(k in StockInfoRequest.schema()["properties"] for k in msg.output.keys()):
            request = StockInfoRequest.parse_obj(msg.output)
            
            if "<UNKNOWN>" in str(msg.output):
                await ctx.send(
                    session_sender,
                    create_text_chat(
                        "Sorry, I couldn't understand your stock query. Please try again with a clearer request (e.g., 'Info for IBM')."
                    ),
                )
                return

            ctx.logger.info(f"Fetching stock info for: {request.ticker}")
            stock_details = get_stock_info(request.ticker)
            
            if "error" in stock_details:
                await ctx.send(session_sender, create_text_chat(str(stock_details["error"])))
                return

            # Format the stock info into a readable message
            message = f"**Stock Info for: '{request.ticker.upper()}'**\n\n"
            message += f"**Name**: {stock_details['name']}\n"
            message += f"**Market Cap**: ${stock_details['market_cap']:,.2f}\n"
            message += f"**Exchange**: {stock_details['exchange']}\n"
            message += f"**Share Class Shares Outstanding**: {stock_details['share_class_shares_outstanding']:,.0f}\n"
            message += f"**Weighted Shares Outstanding**: {stock_details['weighted_shares_outstanding']:,.0f}\n"
            if stock_details["description"]:
                message += f"**Description**: {stock_details['description'][:800]}...\n"  

            await ctx.send(session_sender, create_text_chat(message))
            await ctx.send(session_sender, create_end_session_chat())


        elif "ticker" in msg.output and all(k in HistoricalDataRequest.schema()["properties"] for k in msg.output.keys()):
            request = HistoricalDataRequest.parse_obj(msg.output)
            
            if "<UNKNOWN>" in str(msg.output):
                await ctx.send(
                    session_sender,
                    create_text_chat(
                        "Sorry, I couldn't understand your historical stock query. Please try again with a clearer request (e.g., 'Historical data for IBM')."
                    ),
                )
                return

            ctx.logger.info(f"Fetching historical data for: {request.ticker}")
            historical_data = get_historical_stock_data(request.ticker)
            
            if "error" in historical_data:
                await ctx.send(session_sender, create_text_chat(str(historical_data["error"])))
                return


            message = f"**Historical Stock Data for: '{request.ticker.upper()}' (Last 60 Days)**\n\n"
            message += "Showing closing prices for the past 60 days:\n\n"
            for date, price in list(historical_data.items())[:7]: 
                message += f"**{date}**: ${price:.2f}\n"
            if len(historical_data) > 5:
                message += f"...and {len(historical_data) - 5} more days available.\n"

            await ctx.send(session_sender, create_text_chat(message))
            await ctx.send(session_sender, create_end_session_chat())

        else:
            await ctx.send(
                session_sender,
                create_text_chat(
                    "Sorry, I couldn't process your request. Please specify a stock ticker and whether you want info or historical data."
                ),
            )

    except Exception as e:
        ctx.logger.error(f"Error processing response: {e}")
        if session_sender:
            await ctx.send(
                session_sender,
                create_text_chat(
                    "Sorry, I encountered an error while processing your stock request. Please try again later."
                ),
            )