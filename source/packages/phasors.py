import itertools
def phasor(plt, np, DSSMon_Bus_Vmag, DSSMon_Bus_Vdeg, os, store):
    magnitudes = []
    angles = []
    if not os.path.isdir(f"{store}/phasors"):
        os.mkdir(f"{store}/phasors")
    for (magnitudes, angles) in itertools.zip_longest(DSSMon_Bus_Vdeg, DSSMon_Bus_Vmag, fillvalue=-1):

        angles_rad = np.radians(angles)
        phasors_real = magnitudes * np.cos(angles_rad)
        phasors_imag = magnitudes * np.sin(angles_rad)

        plt.figure(figsize=(8, 6))

        plt.arrow(0, 0, phasors_real[0], phasors_imag[0], color='blue', headwidth=0.1, headlength=0.2)
        plt.arrow(0, 0, phasors_real[1], phasors_imag[1], color='red', headwidth=0.1, headlength=0.2)

        plt.xlabel('Real Axis')
        plt.ylabel('Imaginary Axis')
        plt.title('Phasor Diagram')

        plt.grid(True)
        plt.xlim([-magnitudes[0] - 0.5, magnitudes[0] + 0.5])
        plt.ylim([-magnitudes[1] - 0.5, magnitudes[1] + 0.5])

        for i, (mag, angle) in enumerate(zip(magnitudes, angles)):
            plt.annotate(f"{mag:.2f}∠{angle:.2f}°", (phasors_real[i], phasors_imag[i]), textcoords='offset points', xytext=(0, 10), ha='center')

        plt.savefig("{store}/phasors")