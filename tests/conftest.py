import asyncio
import os
from datetime import timedelta
from typing import Optional

import pytest
import pytest_asyncio

from momento import SimpleCacheClient, SimpleCacheClientAsync
from momento.auth import EnvMomentoTokenProvider
from momento.config import Laptop

#######################
# Integration test data
#######################

TEST_CONFIGURATION = Laptop.latest()

TEST_AUTH_PROVIDER = EnvMomentoTokenProvider("TEST_AUTH_TOKEN")

TEST_CACHE_NAME: Optional[str] = os.getenv("TEST_CACHE_NAME")
if not TEST_CACHE_NAME:
    raise RuntimeError("Integration tests require TEST_CACHE_NAME env var; see README for more details.")

DEFAULT_TTL_SECONDS: timedelta = timedelta(seconds=60)


#############################################
# Integration test fixtures: data and clients
#############################################


@pytest.fixture(scope="session")  # type: ignore
def event_loop() -> asyncio.AbstractEventLoop:
    """cf https://github.com/pytest-dev/pytest-asyncio#-_loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client() -> SimpleCacheClient:
    configuration = TEST_CONFIGURATION
    credential_provider = TEST_AUTH_PROVIDER
    with SimpleCacheClient(configuration, credential_provider, DEFAULT_TTL_SECONDS) as _client:
        # Ensure test cache exists
        _client.create_cache(TEST_CACHE_NAME)
        try:
            yield _client
        finally:
            _client.delete_cache(TEST_CACHE_NAME)


@pytest_asyncio.fixture(scope="session")
async def client_async() -> SimpleCacheClientAsync:
    configuration = TEST_CONFIGURATION
    credential_provider = TEST_AUTH_PROVIDER
    async with SimpleCacheClientAsync(configuration, credential_provider, DEFAULT_TTL_SECONDS) as _client:
        # Ensure test cache exists
        # TODO consider deleting cache on when test runner shuts down
        await _client.create_cache(TEST_CACHE_NAME)
        try:
            yield _client
        finally:
            await _client.delete_cache(TEST_CACHE_NAME)
