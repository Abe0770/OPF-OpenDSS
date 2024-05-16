def plot(data, x_axis, y_axis, name, file_path, plt):
    fig, ax = plt.subplots()
    ax.plot(data)

    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.set_title(name)

    plt.savefig(file_path)
    plt.close()

def subplot(data, x_axis, y_axis, name, file_path, plt, label):
    fig, ax = plt.subplots()

    colors = plt.cm.tab10(range(len(data))) 

    for i, data in enumerate(data):
        ax.plot(data, label=f"{label[i]}", color=colors[i])

    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.set_title(name)
    ax.legend() 

    plt.savefig(file_path)
    plt.close()

def subplots(data, x_axis, y_axis, name, file_path, plt, label, n, np):
    fig, axs = plt.subplots(nrows=int(np.ceil(n / 2)), ncols=2, figsize=(60, 48))
    axs = axs.flatten()  

    for i in range(n):
        axs[i].plot(data[i])
        axs[i].set_title(f"{name} - {label[i]}")
        axs[i].set_xlabel(x_axis)  
        axs[i].set_ylabel(y_axis)  

    for i in range(n, len(axs)):
        axs[i].axis("off")

    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()