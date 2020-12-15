import matplotlib.pyplot as plt


def figure_1(*args):
    print(args)
    fig, ax = plt.subplots()
    ax.plot([1, 3, 4], [3, 2, 5])
    return fig

def figure_2(*args):
    print(args)
    fig, ax = plt.subplots()
    ax.plot([1, 3, 4], [3, 2, 5])
    return fig