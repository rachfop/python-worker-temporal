import argparse
import asyncio
from typing import Optional

from temporalio.client import Client, TLSConfig

async def main(SignalInput: str):
    # Hardcoded values
    TEMPORAL_MTLS_TLS_CERT = "./etc/temporal/ca.pem"
    TEMPORAL_MTLS_TLS_KEY = "./etc/temporal/ca.key"
    TEMPORAL_HOST_URL = "patrick.a2dd6.tmprl.cloud:7233"
    TEMPORAL_NAMESPACE = "patrick.a2dd6"

    # Read client certificate and key
    with open(TEMPORAL_MTLS_TLS_CERT, "rb") as f:
        client_cert = f.read()

    with open(TEMPORAL_MTLS_TLS_KEY, "rb") as f:
        client_key = f.read()

    # Start client
    client = await Client.connect(
        TEMPORAL_HOST_URL,
        namespace=TEMPORAL_NAMESPACE,
        tls=TLSConfig(
            client_cert=client_cert,
            client_private_key=client_key,
        ),
    )


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
