"""
Example: Deploying a simple Todo schema
"""

import asyncio
import httpx


TODO_SCHEMA = {
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "version": "1.0.0",
    "tenant_mode": "row_isolation",
    "entities": {
        "Todo": {
            "name": "Todo",
            "fields": [
                {"name": "id", "type": "uuid", "required": True},
                {"name": "title", "type": "string", "required": True},
                {"name": "description", "type": "text", "required": False, "nullable": True},
                {"name": "completed", "type": "boolean", "required": False},
                {"name": "priority", "type": "integer", "required": False},
            ],
            "ownership": {"mode": "user"},
            "indexes": ["title", "completed"],
        }
    },
    "permissions": {
        "Todo": {"read": "owner", "write": "owner", "delete": "owner"}
    },
}


async def deploy_schema():
    """Deploy Todo schema"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/schema/deploy",
            json=TODO_SCHEMA,
            headers={"Content-Type": "application/json"},
        )

        result = response.json()
        print("Deployment Result:")
        print(f"  Success: {result['success']}")
        print(f"  Version: {result['data']['version']}")
        print(f"  Migration ID: {result['data']['migration_id']}")
        print(f"  Changes: {result['data']['changes']}")


async def validate_schema():
    """Validate Todo schema"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/schema/validate",
            json=TODO_SCHEMA,
        )

        result = response.json()
        print("Validation Result:")
        print(f"  Valid: {result['data']['valid']}")
        print(f"  Warnings: {result['data'].get('warnings', [])}")


async def parse_intent():
    """Parse natural language intent"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/intent/parse",
            json={
                "input": "Create a new entity called Comment with content field",
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )

        result = response.json()
        print("Intent Parsing Result:")
        print(f"  Intent Type: {result['data']['intent']['type']}")
        print(f"  Confidence: {result['data']['intent']['confidence']}")


async def health_check():
    """Check API health"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v1/health")
        result = response.json()
        print("Health Check:")
        print(f"  Status: {result['status']}")
        print(f"  Service: {result['service']}")
        print(f"  Timestamp: {result['timestamp']}")


async def main():
    """Run all examples"""
    print("=== Vibe Coding Platform - Python Examples ===\n")

    print("1. Health Check")
    await health_check()
    print()

    print("2. Validate Schema")
    await validate_schema()
    print()

    print("3. Deploy Schema")
    await deploy_schema()
    print()

    print("4. Parse Intent")
    await parse_intent()
    print()


if __name__ == "__main__":
    asyncio.run(main())
