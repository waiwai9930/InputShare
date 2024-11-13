import asyncio

async def test_single_port(ip: str, port: int) -> int | None:
    connection = asyncio.open_connection(ip, port)
    try:
        _, writer = await asyncio.wait_for(connection, timeout=0.2)
        writer.close()
        await writer.wait_closed()
        return port
    except: return None

async def inner_port_scan(ip: str, start_port: int, end_port: int, step=1024) -> int | None:
    for i in range(start_port, end_port, step):
        port_range = range(i, min(end_port, i + step))
        tasks = [test_single_port(ip, port) for port in port_range]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result is None: continue
            return result

def scan_port(ip: str) -> int | None:
    start_port = 32000
    end_port = 47000
    target_port = asyncio.run(inner_port_scan(ip, start_port, end_port))
    return target_port
