from functools import wraps
import pickle
from hashlib import md5

from django.conf import settings

from celery import task, Task, current_task
from celery.utils.log import get_task_logger
from redis import Redis

REDIS_CLIENT = None

def redis():
    global REDIS_CLIENT
    if REDIS_CLIENT is None:
        REDIS_CLIENT = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_LOCKS_DB)
    return REDIS_CLIENT


logger = get_task_logger(__name__)

class SingleTask(Task):
    abstract = True
    collapse_queue = False

    def __init__(self, *args, **kwargs):
        super(SingleTask, self).__init__(*args, **kwargs)
        self._collapse_key = self.name + ':collapse:'

    def apply_async(self, args=None, kwargs={}, **options):
        res = super(SingleTask, self).apply_async(args=args, kwargs=kwargs, **options)
        if getattr(settings, 'CELERY_ALWAYS_EAGER', False) is False and \
           self.collapse_queue == 'last':
            redis().set(self.collapse_key(args, kwargs), res.id)
        return res
        
    def collapse_key(self, args, kwargs):
        params_str = pickle.dumps((tuple(args or []), kwargs))
        return self._collapse_key + md5(params_str).hexdigest()

    #def after_return(self, *args, **kwargs):
        #logger.debug('Task returned: %r' % (self.request, ))
        #if self.have_lock:
            #logger.debug('release_lock: %r' % (self.request, ))
            #self.lock.release()

            
class single_task():
    '''
    Decorator factory, creates a task decorator with 
    SingleTask base and desired task parameters
    '''
    def __init__(self, **taskparams):
        self.taskparams = taskparams
    
    def __call__(self, f):
        ''' Decorate the function '''
        @task(base=SingleTask, **self.taskparams)
        @wraps(f)
        def wrapped(*args, **kwargs):
            if getattr(settings, 'CELERY_ALWAYS_EAGER', False):
                return f(*args, **kwargs)

            if current_task.collapse_queue == 'last':
                last_id = redis().get(current_task.collapse_key(args, kwargs))
                if last_id != current_task.request.id:
                    logger.info("i'm not the last: %s, i'm %s, quit", last_id, current_task.request.id)
                    return
            
            return f(*args, **kwargs)
        return wrapped 


class lock_retry():
    """
    Decorator factory for tasks. Makes task retry if this task is currently executing in other process.
    Note that this decorator should be applied before @task decorator (placed below)
    """
    def __init__(self, timeout=None, countdown=None):
        self.timeout = timeout
        self.countdown = countdown

    def __call__(self, func):
        """ Apply decorator to the function """

        @wraps(func)
        def wrapped(*args, **kwargs):
            if getattr(settings, 'CELERY_ALWAYS_EAGER', False):
                return func(*args, **kwargs)

            lock = redis().lock(current_task.name + ':lock', timeout=self.timeout)
            have_lock = lock.acquire(blocking=False)
            if have_lock:
                try:
                    return func(*args, **kwargs)
                finally:
                    lock.release()
            else:
                raise current_task.retry(countdown=self.countdown)

            #logger.info('lock failed: %r', (current_task.request, ))
        return wrapped
