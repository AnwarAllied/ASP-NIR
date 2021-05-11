# import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from .models import PcaModel
# from core.models import Spectrum
# from chartjs.colors import next_color


def datasheet4testing(file,filename):
    # profile=NirProfile.objects.get(pk=pk)
    filetype=filename.split('.')[-1]
    try:
        print('filetype :',filetype)
        # upload the data from the 1st sheet: 
        sh1 = pd.read_csv(file)
        print('Abs. :',sh1['Column 1'][20])
        y_axis=list(map(float,sh1['Column 1'][21:].values.tolist()))
        x_axis=list(map(float,sh1['Method:'][21:].values.tolist()))
        # color_generator =next_color()
        xmin=min(x_axis)
        xmax=max(x_axis)
        
        # print('match :',match.y_axis[:5],match.y_axis[-5:])
        # match.obtain()  # match.save()
        # print("Match",match.id, 'saved')
        return y_axis, 'successfuly uploaded'
    except Exception as e:
        return False, 'Error while processing '+filename+ ' :'+e.__str__()
    

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