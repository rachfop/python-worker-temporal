from dataclasses import dataclass

from temporalio import activity


@dataclass
class YourParams:
    name: str


@activity.defn
async def greet(input: YourParams) -> str:
    return f"Hello, {input.name}!"
