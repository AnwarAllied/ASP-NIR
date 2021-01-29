# import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from .models import Spectrum, NirProfile
from chartjs.colors import next_color

def datasheet2spec(file,pk,filename):
    profile=NirProfile.objects.get(pk=pk)
    filetype=filename.split('.')[-1]
    if filetype in ['xlsx','xls']:
        try:
            exf=pd.ExcelFile(file)
            # upload the data from the 1st sheet: 
            sh1 = pd.read_excel(exf, exf.sheet_names[0],index_col=False)
            x_axis=list(map(float,list(sh1)[1:]))
            label1=sh1[list(sh1)[0]]
            dataset=np.array([sh1[list(sh1)[i+1]].values.tolist() for i in range(len(x_axis))]).T
            color_generator =next_color()
            xmin=min(x_axis)
            xmax=max(x_axis)
            for i in range(len(dataset)):
                S = Spectrum(
                    origin = '%s %s %s %s' % (filename.split('-')[0],label1[i],list(sh1)[0],filename.split('-')[-1].split('.')[0]),
                    code = 'WM%dV%dX%dN%d' % (np.mean(dataset[i]),np.var(dataset[i]),np.max(dataset[i]),np.min(dataset[i])),
                    color = '#%02X%02X%02X' % tuple(next(color_generator)),
                    y_axis = str(dataset[i].tolist())[1:-1],
                    x_range_max = xmax,
                    x_range_min = xmin,
                    nir_profile = profile
                )
                S.save()
                print("spectrum",i, 'saved')
        except Exception as e:
            return False , 'Error while processing '+filename+ ' :'+e.__str__()
    return True, 'successfuly uploads'

def detect_xls_profile(xls):
    """
    To detect the format of the spectral content in the xls file:

    The file name format: "ORIGIN ORIGINSUB1 ORIGINSUB2 ... - LABLE1 LABLE2 ... - REFFERANCE Note... .xls"
    ORIGIN: Wheat, Soybean
    ORIGINSUB1: Granded, Flour
    LABLE1: Protein, Brix
    LABLE2: Moisture, ...
    REFFERANCE: ASP, Alan Ames
    Note: 1_20201126_120750
    A: NIRvaScan format: single sheet & single spectrum in colB after row22.
    B: One sheet & one index format: 1st row for x-axis data and 1st col for label (e.g. protein level).
    C: One sheet & multi index formats (for labels): as B and 2nd, 3rd col for lables (e.g. protein and moisture).
    D: Multi-sheet format

    """
    pass



def figure_2(*args):
    print(args)
    fig, ax = plt.subplots()
    ax.plot([1, 3, 4], [3, 2, 5])
    return fig