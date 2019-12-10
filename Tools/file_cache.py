#coding=utf-8
import hashlib
import os
import pandas as pd
import pcikle
from collection import OrderedDict

def get_cache_path():
	__cache__path = '/tmp/{}/'.format(pd.datetime.now().strftime(format="%Y-%m-%d"))
	if os.path.exist(__cache__path):
		pass
	else:
		os.mkdir(__cache__path)
	return __cache__path
	
	
def _cache(func,arg,kwargs,time_format_dimension='%Y-%m-%d'):
	kwargs = OrderedDict(sorted(kwargs.items(),key=lambda t :t[0]))
	key = pickle.dumps([func.__code__._co_name,arg,kwargs])
	name = func.__code__._co_name+"_" + hashlib.sha1(key).hexdigest()+"_{}".format(pd.datetime.now().strftime(time_format_dimension))
	file_path = get_cache_path()
	if os.path.exist(file_path+name):
		with open(file_path+name,'rb') as f:
			res = pickle.load(f)
	else:
		res = func(*arg,**kwargs)
		with open(file_path+name,'wb') as f:
			pickle.sump(res,f)
	return res
		
		


def file_cache(deco_arg_dict):
	if callable(deco_arg_dict):
		@wraps(deco_arg_dict)
		def wrapped(*args,**kwargs):
			return _cache(deco_arg_dict,args,kwargs)
		return wrapped
	else:
		def _deco(func):
			@wraps(func)
			def __deco(*args,**kwargs):
				return _cache(func,args,kwargs)
			return __deco
		return _deco
if __name__=='__main__':
	pass