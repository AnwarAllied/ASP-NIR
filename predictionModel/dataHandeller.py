import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from core.models import Spectrum
from chartjs.colors import next_color

def datasheet4matching(file,filename):
    # profile=NirProfile.objects.get(pk=pk)
    filetype=filename.split('.')[-1]
    try:
        # upload the data from the 1st sheet:
        sh1 = pd.read_csv(file)
        y_axis=list(map(float,sh1['Column 1'][21:].values.tolist()))
        x_axis=list(map(float,sh1['Method:'][21:].values.tolist()))
        # label1=sh1[list(sh1)[0]]
        # dataset=np.array([sh1[list(sh1)[i+1]].values.tolist() for i in range(len(x_axis))]).T
        color_generator =next_color()
        xmin=min(x_axis)
        xmax=max(x_axis)
        spec=Spectrum()
        spec.origin='Latest uploaded spectrum'
        spec.color=color_generator
        spec.y_axis=y_axis
        spec.x_range_min=xmin
        spec.x_range_max=xmax
        spec.spec_pic=''
        spec.nir_profile=''
        spec.pic_path=''
        return spec, 'successfuly uploaded'
    except Exception as e:
        return False, 'Error while processing '+filename+ ' :'+e.__str__()