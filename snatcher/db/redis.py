from redis import Redis

from snatcher.conf import settings


class PortWeightManager:
    def __init__(self):
        self.weights_cache = None

    def get_optimal_port(self):
        rank = 0

        def inner() -> list:
            nonlocal rank

            port_list = self.weights_cache.zrevrange('weights', rank, rank)
            rank += 1
            return port_list
        return inner

    def decrease_weight(self, port: str, decrease_size: int | float = 20):
        weight = self.weights_cache.zscore('weights', port)
        self.weights_cache.zadd('weights', {port: weight - decrease_size})

    def increase_weight(self, port: str, increase_size: int | float = 10):
        weight = self.weights_cache.zscore('weights', port)
        self.weights_cache.zadd('weights', {port: weight + increase_size})

    def __enter__(self):
        self.weights_cache = Redis(**settings.DATABASES['redis']['weights'], decode_responses=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.weights_cache.close()


def optimal_port_generator():
    with PortWeightManager() as manager:
        optimal_port = manager.get_optimal_port()
        while port_list := optimal_port():
            yield port_list[0]


def decreasing_weight(port: str, decrease_size: int | float = 20):
    with PortWeightManager() as manager:
        manager.decrease_weight(port, decrease_size)


def increasing_weight(port: str, increase_size: int | float = 10):
    with PortWeightManager() as manager:
        manager.increase_weight(port, increase_size)
