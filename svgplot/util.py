from scipy import stats
import numpy as np
import pandas as pd

def zscore(d, clip=None, min=None, max=None, axis=1):
	# StandardScaler().fit_transform(d.T)
	sd = stats.zscore(d, axis=axis)

	#sd = sd.T

	if isinstance(clip, float) or isinstance(clip, int):
		max = abs(clip)
		min = -max

	if isinstance(min, float) or isinstance(min, int):
		print('scale min', min)
		sd[np.where(sd < min)] = min

	if isinstance(max, float) or isinstance(max, int):
		print('scale max', max)
		sd[np.where(sd > max)] = max

	return pd.DataFrame(sd, index=d.index, columns=d.columns)
