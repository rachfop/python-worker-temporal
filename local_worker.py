import asyncio
import os
from typing import Optional

from temporalio.client import Client, TLSConfig
from temporalio.worker import Worker

# Import the activity and workflow from our other files
from activities import greet
from workflows import VersioningExample


async def main():

    client = await Client.connect("localhost:7233")
    versioning_build_id = os.getenv("VERSIONING_BUILD_ID")
    # Run the worker
    worker = Worker(
        client,
        task_queue="versioned-queue",
        workflows=[VersioningExample],
        activities=[greet],
        build_id=f"{versioning_build_id}",
        use_worker_versioning=True,
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
