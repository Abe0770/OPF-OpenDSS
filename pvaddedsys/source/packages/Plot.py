def plot(plt, xax, yax, xlab, ylab, title, grid):
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.plot(xax, yax)
    plt.title(title)
    plt.grid(grid)
    plt.show()