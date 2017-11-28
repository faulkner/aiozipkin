import asyncio
import aiohttp
import aiozipkin as az

from aiohttp import web


service_c_api = 'http://127.0.0.1:9003/api/v1/data'
service_d_api = 'http://127.0.0.1:9004/api/v1/data'


async def handler(request):
    await asyncio.sleep(0.01)
    session = request.app['session']

    resp = await session.get(service_c_api)
    data_c = await resp.text()

    resp = await session.get(service_d_api)
    data_d = await resp.text()

    body = 'service_b ' + data_c + ' ' + data_d
    return web.Response(text=body)


def make_app():
    app = web.Application()
    app.router.add_get('/api/v1/data', handler)

    zipkin_address = 'http://127.0.0.1:9411'
    endpoint = az.create_endpoint('service_b')
    tracer = az.create(zipkin_address, endpoint, sample_rate=1.0)
    az.setup(app, tracer)

    trace_config = az.make_trace_config(tracer)
    session = aiohttp.ClientSession(trace_configs=[trace_config])
    app['session'] = session
    return app


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 9001
    app = make_app()
    web.run_app(app, host=host, port=port)
