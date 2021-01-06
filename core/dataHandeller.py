# import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from .models import Spectrum, NirProfile
from chartjs.colors import next_color

def datasheet2spec(file,pk,filename):
    print("kwargs")
    profile=NirProfile.objects.get(pk=pk)
    filetype=filename.split('.')[-1]
    if filetype in ['xlsx','xls']:
        exf=pd.ExcelFile(file)
        # upload the data from the 1st sheet: 
        sh1 = pd.read_excel(exf, exf.sheet_names[0],index_col=False)
        # upload lables from the 2nd sheet:
        # sh2 = pd.read_excel(exf, exf.sheet_names[1],index_col=False, error_bad_lines=False, encoding='utf-8')
        # dt=pd.read_excel(co, index_col=False, error_bad_lines=False, encoding='utf-8')
        x_axis=list(map(float,list(sh1)[1:]))
        label1=sh1[list(sh1)[0]].values
        dataset=np.array([sh1[list(sh1)[i+1]].values.tolist() for i in range(len(x_axis))]).T
        color_generator =next_color()
        xmin=min(x_axis)
        xmax=max(x_axis)
        for i in range(len(dataset)):
            S = Spectrum(
                origin = 'Wheat %d %s %s' % (label1[i],list(sh1)[0], 'C'),
                code = 'WM%dV%dX%dN%d' % (np.mean(dataset[i]),np.var(dataset[i]),np.max(dataset[i]),np.min(dataset[i])),
                color = '#%02X%02X%02X' % tuple(next(color_generator)),
                y_axis = str(dataset[i].tolist())[1:-1],
                x_range_max = xmax,
                x_range_min = xmin,
                nir_profile = profile
            )
            S.save()
            print("spectrum",i, 'saved')
    return 'successfuly uploads'   

def figure_2(*args):
    print(args)
    fig, ax = plt.subplots()
    ax.plot([1, 3, 4], [3, 2, 5])
    return fig