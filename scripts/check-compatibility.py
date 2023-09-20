import asyncio
import os
import sys
from typing import Optional

from env import (get_connection_options, get_workflow_options, namespace,
                 task_queue)
from temporalio.client import Client, TLSConfig
from temporalio.worker import Worker


async def main():
    if (
        os.getenv("TEMPORAL_MTLS_TLS_CERT")
        and os.getenv("TEMPORAL_MTLS_TLS_KEY") is not None
    ):
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

    if len(sys.argv) < 2:
        raise Exception(f"usage: {sys.argv[0]} <prTitle>")

    pr_title = sys.argv[1]
    matches = pr_title.match(r"^\[compatible-([^\]]+)\]")

    if matches is None:
        raise Exception(f"invalid PR title {pr_title}")

    build_id = matches.group(1)

    connection = await Connection.connect(get_connection_options())
    client = Client(connection=connection, namespace=namespace)

    compatibility = await client.task_queue.get_build_id_compatibility(task_queue)
    set_ = next(
        (s for s in compatibility.version_sets if build_id in s.build_ids), None
    )

    if set_ is None:
        raise Exception(f"Could not find set that contains build ID: {build_id}")

    joined_build_ids = ", ".join([f'"versioned-{b}"' for b in set_.build_ids])

    histories = await client.workflow.list(
        query=f'TaskQueue="{task_queue}" AND BuildIds IN ({joined_build_ids})'
    ).into_histories()

    replay_results = await Worker.run_replay_histories(
        get_workflow_options(), histories
    )

    i = 0
    for result in replay_results:
        if result.error:
            raise result.error
        i += 1
        if i > 10_000:
            break
        if i % 1000 == 0:
            print(f"{i} compatible")

    print("✅ all compatible")
    await connection.close()


try:
    asyncio.run(run())
except Exception as err:
    print(err)
    sys.exit(1)
