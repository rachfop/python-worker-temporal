import argparse
import asyncio
import os
from typing import Optional

from temporalio.client import Client, TLSConfig


async def main(SignalInput: str):

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
    async for workflow in client.list_workflows(
        'WorkflowType="VersioningExample" AND ExecutionStatus="Running"'
    ):
        print(f"Signalling {workflow.id} with signal input: {SignalInput}")
        handle = client.get_workflow_handle(workflow.id)
        await handle.signal("Proceed", SignalInput)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start and signal workflows.")
    parser.add_argument("SignalInput", type=str, help="Input for the signal")

    args = parser.parse_args()
    asyncio.run(main(args.SignalInput))
