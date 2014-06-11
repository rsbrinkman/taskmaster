import redis
from taskmaster import settings

db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

keys = db.keys('queue-tasks>*') + ['org-tasks>Taskmaster', 'org-queues>Taskmaster']
for k in keys:
    prev = db.smembers(k)
    new = [ele for lst in zip([0] * len(prev), prev) for ele in lst]
    v_index = k.index('>')
    new_k = k[:v_index] + '2' + k[v_index:]
    db.zadd(new_k, *new)
