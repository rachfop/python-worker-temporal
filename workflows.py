import asyncio
from datetime import timedelta
from typing import List

from temporalio import workflow

# Import our activity, passing it through the sandbox
with workflow.unsafe.imports_passed_through():
    from activities import greet


@workflow.defn
class VersioningExample:
    def __init__(self) -> None:
        self._pending_inputs: List[str] = []

    @workflow.run
    async def run(self) -> str:
        workflow.logger.info("Workflow V1 started, waiting for signal.")
        while True:
            await workflow.wait_condition(lambda: self._pending_inputs)

            input_value = self._pending_inputs.pop(0)
            workflow.logger.info(f"Workflow V1 got signal: {input_value}")
            await workflow.execute_activity(
                f"from V2.1 workflow!",
                greet,
                start_to_close_timeout=timedelta(minutes=1),
            )

            if input_value == "finish":
                return "Concluded workflow on V1"

    @workflow.signal
    def proceeder(self, input: str):
        self._pending_inputs.append(input)
