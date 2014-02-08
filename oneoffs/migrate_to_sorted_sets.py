import redis
import settings

db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


prev_queues = db.smembers('org-queues>Taskmaster')


new_queues = [ele for lst in zip([0] * len(prev_queues)) for ele in lst]


db.zadd('org-queues2>Taskmaster', *new_queues)
