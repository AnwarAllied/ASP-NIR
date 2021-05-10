import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from core.models import Spectrum
from chartjs.colors import next_color

def datasheet4matching(file,filename):
    filetype=filename.split('.')[-1]
    try:
        # upload the data from the 1st sheet:
        sh1 = pd.read_csv(file)
        y_axis=str(list(map(float,sh1['Column 1'][21:].values.tolist())))[1:-1]
        x_axis=list(map(float,sh1['Method:'][21:].values.tolist()))
        print('y_axis:',y_axis)
        # label1=sh1[list(sh1)[0]]
        # dataset=np.array([sh1[list(sh1)[i+1]].values.tolist() for i in range(len(x_axis))]).T
        color_generator =next_color()
        xmin=min(x_axis)
        xmax=max(x_axis)

        return y_axis,xmin,xmax, 'successfully uploaded'
    except Exception as e:
        return False, 'Error while processing '+filename+ ' :'+e.__str__()