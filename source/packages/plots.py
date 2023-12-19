def plot(data, x_axis, y_axis, name, file_path, plt):
    fig, ax = plt.subplots()
    ax.plot(data)

    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.set_title(name)

    plt.savefig(file_path)
    plt.close()