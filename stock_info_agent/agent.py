from enum import Enum
from uagents import Agent, Context, Model
from uagents.experimental.quota import QuotaProtocol, RateLimit
from protocol import chat_proto, struct_output_client_proto


AGENT_NAME = "Stock Info Agent"
agent = Agent(
    name=AGENT_NAME,
    port=8005,
    seed="StockInfoAgent",
    mailbox=True
)

stock_proto = QuotaProtocol(
    storage_reference=agent.storage,
    name="Stock-Agent-Protocol",
    version="0.1.0",
    default_rate_limit=RateLimit(window_size_minutes=60, max_requests=60),
)
class HealthCheck(Model):
    pass

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

class AgentHealth(Model):
    agent_name: str
    status: HealthStatus

def agent_is_healthy() -> bool:
    """
    Implement health check logic.
    In production, this might check:
    - Connection to Polygon API
    - System resources
    """
    return True

health_protocol = QuotaProtocol(
    storage_reference=agent.storage,
    name="HealthProtocol",
    version="0.1.0"
)

@health_protocol.on_message(HealthCheck, replies={AgentHealth})
async def handle_health_check(ctx: Context, sender: str, msg: HealthCheck):
    status = HealthStatus.UNHEALTHY
    try:
        if agent_is_healthy():
            status = HealthStatus.HEALTHY
    except Exception as err:
        ctx.logger.error(f"Health check error: {err}")
    finally:
        await ctx.send(sender, AgentHealth(agent_name=AGENT_NAME, status=status))
# Include protocols
agent.include(stock_proto, publish_manifest=True)
agent.include(chat_proto, publish_manifest=True)
agent.include(struct_output_client_proto, publish_manifest=True)
agent.include(health_protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()

