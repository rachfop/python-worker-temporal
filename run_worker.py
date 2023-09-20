import asyncio
import os
from typing import Optional

from temporalio.client import Client, TLSConfig
from temporalio.worker import Worker

# Import the activity and workflow from our other files
from activities import greet
from workflows import VersioningExample


async def main():

    if os.getenv("TEMPORAL_MTLS_TLS_CERT") and os.getenv("TEMPORAL_MTLS_TLS_KEY"):
        server_root_ca_cert: Optional[bytes] = None
        with open(os.getenv("TEMPORAL_MTLS_TLS_CERT"), "rb") as f:
            client_cert = f.read()

        with open(os.getenv("TEMPORAL_MTLS_TLS_KEY"), "rb") as f:
            client_key = f.read()

        # Start client
        client = await Client.connect(
            os.getenv("TEMPORAL_HOST_URL"),
            namespace=os.getenv("TEMPORAL_NAMESPACE"),
            tls=TLSConfig(
                server_root_ca_cert=server_root_ca_cert,
                client_cert=client_cert,
                client_private_key=client_key,
            ),
        )
    else:
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
