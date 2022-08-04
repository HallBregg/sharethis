#!python
import asyncio
import datetime
import logging
import logging.config
import signal
from typing import Callable, NoReturn

from sharethis.infrastructure.main import db, config_logger, bucket_storage_client
from sharethis.services.uow import MainUnitOfWork


tasks = {}
logger = config_logger()


async def periodic_wrapper(
    func: Callable,
    interval: datetime.timedelta,
    **func_kwargs,
) -> NoReturn:
    """
    Args:
        func:
        interval:
        **func_kwargs:

    Returns:

    """
    try:
        while True:
            await asyncio.sleep(interval.total_seconds())
            try:
                func(**func_kwargs)
            except Exception as e:
                logger.critical(e)
    except asyncio.CancelledError:
        logger.warning('Task cancelled')


def create_periodic_task(
    name: str,
    func: Callable,
    interval: datetime.timedelta,
    **func_kwargs
) -> asyncio.Task:
    """

    Args:
        name:
        func:
        interval:
        **func_kwargs:

    Returns:

    """
    return asyncio.create_task(periodic_wrapper(func, interval, **func_kwargs), name=name)


async def shutdown(sig: signal, loop):
    logging.info(f'Received signal: {sig.name}')
    tasks_to_cancel = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
    [task.cancel() for task in tasks_to_cancel]
    logging.info(f'Cancelling: {len(tasks)} tasks')
    await asyncio.gather(*tasks)


def register_signals(signals, loop):
    for sig in signals:
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(sig, loop)))


def cleaner():
    with MainUnitOfWork(db, bucket_storage_client) as uow:
        to_delete = uow.content_meta.delete_expired()
        uow.content.bulk_delete(to_delete)
        uow.commit()
    if deleted := len(to_delete):
        logger.info(f'Cleaner deleted: {deleted} records and associated files.')
    logger.debug(f'Files deleted: {to_delete}')


async def main():
    register_signals(
        signals=(signal.SIGHUP, signal.SIGTERM, signal.SIGINT),
        loop=asyncio.get_event_loop(),
    )
    cleaner_task = create_periodic_task(
        name='cleaner',
        func=cleaner,
        interval=datetime.timedelta(seconds=5),
    )
    try:
        await asyncio.gather(cleaner_task)
    except asyncio.CancelledError:
        logger.info('Gather cancelled')
        logger.info('Cleaning')


if __name__ == '__main__':
    asyncio.run(main())
