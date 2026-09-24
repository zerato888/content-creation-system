# LUTs creativos

Cuatro LUTs 3D (`.cube`, tamaño 16) para dar color final a un video: `cinematic-gold-02`, `clean`, `creamy` y `film`. El catálogo con hash e intensidad por defecto está en `LIBRARY.json`.

Uso rápido con ffmpeg (intensidad 0.5 mezclando con el original):

```
ffmpeg -protocol_whitelist file,pipe -i entrada.mp4 -filter_complex "[0:v]split[a][b];[b]lut3d=creative/film.cube[c];[a][c]blend=all_mode=normal:all_opacity=0.5" salida.mp4
```

LUTs: created by the kit author.
