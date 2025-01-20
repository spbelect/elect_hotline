from __future__ import absolute_import
from collections import OrderedDict, defaultdict

class DequeDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        self.maxlen = kwargs.pop('maxlen', None)
        return super(DequeDict, self).__init__(*args, **kwargs)
    
    def __setitem__(self, key, value):
        res = super(DequeDict, self).__setitem__(key, value)
        if self.maxlen and len(self) > self.maxlen:
            self.popitem(last = False)
        return res
    
    
class BubbleDict(DequeDict):
    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        return super(BubbleDict, self).__setitem__(key, value)




def autovivify(levels = 1, final = dict):
    return (defaultdict(final) if levels < 2 else
            defaultdict(lambda: autovivify(levels - 1, final)))