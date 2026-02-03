import asyncio

from agoraiot import config
from computation_example import ComputationExample

if __name__ == '__main__':
    print(config)

    loop = asyncio.get_event_loop()

    compute = ComputationExample()
    loop.create_task(compute.run())
    loop.run_forever()
