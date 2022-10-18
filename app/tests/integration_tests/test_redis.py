from redis import Redis


def test_redis_connection():
    redis_host = 'redis'
    connection = Redis(redis_host)
    assert connection.ping()
