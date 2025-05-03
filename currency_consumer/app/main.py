from dependency_injector.wiring import inject, Provide

from app.containers.currency_container import Container


async def main() -> None:
    container = Container()
    service = container.currency_service()
    await service.process_ticker_stream()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
