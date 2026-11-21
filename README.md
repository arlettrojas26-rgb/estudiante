# Modulacion en amplitud (AM)

Proyecto reproducible en Python para estudiar una senal AM convencional:

- mensaje sinusoidal de 200 Hz;
- portadora sinusoidal de 4 kHz;
- indice de modulacion m = 0.70, por debajo de 1;
- muestreo a 48 kHz y duracion de 50 ms;
- atenuacion, ruido aditivo gaussiano y recorte por saturacion.

Solo usa `numpy` y `matplotlib`.

## Ejecucion

```powershell
python am_modulation.py
python -m unittest -v
```

Las figuras se guardan automaticamente en `graficas/`:

- `original.png`: mensaje, senal AM y envolvente teorica;
- `atenuacion.png`: perdida de amplitud;
- `ruido.png`: piso espectral elevado;
- `saturacion.png`: distorsion por recorte;
- `comparacion_espectral.png`: comparacion de los cuatro casos.

## Hallazgos esperados

En la senal original, la envolvente sigue a `1 + m cos(2*pi*fm*t)`. Su espectro presenta una componente portadora en 4 kHz y dos bandas laterales a 3.8 kHz y 4.2 kHz.

La atenuacion reduce toda la amplitud sin cambiar las posiciones espectrales ni introducir nuevas componentes. El ruido aditivo eleva el piso del espectro y puede ocultar componentes pequenas.

El recorte elimina los picos de la senal modulada. Al ser una transformacion no lineal, crea armonicos y laterales adicionales alrededor de la portadora. La saturacion tambien modifica la envolvente y puede producir componentes fuera de las bandas originales.

El indice se limita a `[0, 1]`. Con m = 0.70, la envolvente permanece positiva y no hay inversion de fase ni sobremodulacion.