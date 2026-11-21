"""Demonstracion reproducible de modulacion en amplitud convencional."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def generate_message(t, fm=200.0, amplitude=1.0):
    return amplitude * np.cos(2.0 * np.pi * fm * t)


def generate_carrier(t, fc=4000.0, amplitude=1.0):
    return amplitude * np.cos(2.0 * np.pi * fc * t)


def modulate_am(message, carrier, modulation_index):
    if not 0.0 <= modulation_index <= 1.0:
        raise ValueError("El indice de modulacion debe estar entre 0 y 1")
    return carrier * (1.0 + modulation_index * message)


def add_attenuation(signal, gain=0.35):
    if gain < 0:
        raise ValueError("La ganancia no puede ser negativa")
    return gain * signal


def add_noise(signal, noise_std=0.08, rng=None):
    if noise_std < 0:
        raise ValueError("La desviacion estandar no puede ser negativa")
    if rng is None:
        rng = np.random.default_rng(0)
    return signal + rng.normal(0.0, noise_std, signal.shape)


def clip_distortion(signal, threshold=0.75):
    if threshold <= 0:
        raise ValueError("El umbral debe ser positivo")
    return np.clip(signal, -threshold, threshold)


def spectrum(signal, fs):
    n = signal.size
    frequencies = np.fft.rfftfreq(n, d=1.0 / fs)
    values = np.abs(np.fft.rfft(signal)) * (2.0 / n)
    values[0] /= 2.0
    if n % 2 == 0:
        values[-1] /= 2.0
    return frequencies, values


def spectrum_db(values, floor_db=-100.0):
    reference = max(np.max(values), np.finfo(float).eps)
    minimum = 10.0 ** (floor_db / 20.0)
    return 20.0 * np.log10(np.maximum(values / reference, minimum))


def plot_scenario(t, message, signal, fs, title, output_path, fm, fc, mi, envelope=False):
    frequencies, amplitudes = spectrum(signal, fs)
    db = spectrum_db(amplitudes)
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), constrained_layout=True)
    view = slice(0, int(0.012 * fs))
    axes[0].plot(t[view] * 1000.0, message[view], "--", linewidth=1.2,
                 label="Mensaje", color="tab:orange")
    axes[0].plot(t[view] * 1000.0, signal[view], linewidth=0.9,
                 label="Senal recibida", color="tab:blue")
    if envelope:
        upper = 1.0 + mi * message
        axes[0].plot(t[view] * 1000.0, upper[view], ":", linewidth=1.8,
                     label="Envolvente teorica", color="tab:red")
        axes[0].plot(t[view] * 1000.0, -upper[view], ":", linewidth=1.8,
                     color="tab:red")
    axes[0].set_title(f"{title}: dominio del tiempo")
    axes[0].set_xlabel("Tiempo (ms)")
    axes[0].set_ylabel("Amplitud")
    axes[0].grid(alpha=0.25)
    axes[0].legend(loc="upper right")

    limit = fc + 7.0 * max(fm, fc * 0.05)
    band = frequencies <= limit
    axes[1].plot(frequencies[band] / 1000.0, db[band], linewidth=1.2,
                 color="tab:green")
    axes[1].axvline(fc / 1000.0, linestyle="--", linewidth=0.9,
                    color="tab:red", label=f"Portadora {fc:.0f} Hz")
    for offset in (-fm, fm):
        axes[1].axvline((fc + offset) / 1000.0, linestyle=":",
                        linewidth=0.9, color="tab:purple")
    axes[1].set_title(f"{title}: dominio de la frecuencia")
    axes[1].set_xlabel("Frecuencia (kHz)")
    axes[1].set_ylabel("Amplitud relativa (dB)")
    axes[1].set_ylim(-100, 5)
    axes[1].grid(alpha=0.25)
    axes[1].legend(loc="upper right")
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def analyze_scenarios(output_dir=None, seed=2026):
    output_dir = Path(output_dir) if output_dir else Path(__file__).resolve().parent / "graficas"
    output_dir.mkdir(parents=True, exist_ok=True)
    fs, duration, fm, fc, mi = 48000.0, 0.05, 200.0, 4000.0, 0.70
    t = np.arange(0.0, duration, 1.0 / fs)
    message = generate_message(t, fm=fm)
    carrier = generate_carrier(t, fc=fc)
    am_signal = modulate_am(message, carrier, mi)
    rng = np.random.default_rng(seed)
    scenarios = {
        "original": am_signal,
        "atenuacion": add_attenuation(am_signal, gain=0.35),
        "ruido": add_noise(am_signal, noise_std=0.08, rng=rng),
        "saturacion": clip_distortion(am_signal, threshold=0.75),
    }
    for name, signal in scenarios.items():
        plot_scenario(t, message, signal, fs, name.replace("_", " ").capitalize(),
                      output_dir / f"{name}.png", fm, fc, mi, envelope=(name == "original"))

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    limit = fc + 7.0 * max(fm, fc * 0.05)
    for axis, (name, signal) in zip(axes.flat, scenarios.items()):
        frequencies, amplitudes = spectrum(signal, fs)
        db = spectrum_db(amplitudes)
        band = frequencies <= limit
        axis.plot(frequencies[band] / 1000.0, db[band], linewidth=1.0)
        axis.axvline(fc / 1000.0, color="tab:red", linestyle="--", linewidth=0.8)
        axis.axvline((fc - fm) / 1000.0, color="tab:purple", linestyle=":", linewidth=0.8)
        axis.axvline((fc + fm) / 1000.0, color="tab:purple", linestyle=":", linewidth=0.8)
        axis.set_title(name.replace("_", " ").capitalize())
        axis.set_xlim(0.0, limit / 1000.0)
        axis.set_ylim(-100, 5)
        axis.set_xlabel("Frecuencia (kHz)")
        axis.set_ylabel("Amplitud relativa (dB)")
        axis.grid(alpha=0.25)
    fig.suptitle("Comparacion espectral: AM convencional", fontsize=14)
    fig.savefig(output_dir / "comparacion_espectral.png", dpi=160)
    plt.close(fig)
    return t, message, carrier, am_signal, scenarios


if __name__ == "__main__":
    _, _, _, am, cases = analyze_scenarios()
    print("Simulacion completa.")
    print(f"Muestras AM: {am.size}")
    print(f"Escenarios generados: {', '.join(cases)}")
