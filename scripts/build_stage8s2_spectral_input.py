#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

RW3_DENSITY = 1.045
RW3_H = 0.0759
RW3_C = 0.9041
RW3_O = 0.0080
RW3_TI = 0.0120


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', required=True)
    ap.add_argument('--beam', required=True, choices=('Q120','Q140','Q150','Q200'))
    ap.add_argument('--medium', required=True, choices=('water','rw3'))
    ap.add_argument('--depth-cm', required=True, type=float)
    ap.add_argument('--ssd-cm', type=float, default=50.0)
    ap.add_argument('--field-x-cm', type=float, default=8.0)
    ap.add_argument('--field-y-cm', type=float, default=10.0)
    ap.add_argument('--radius-cm', type=float, default=0.5)
    ap.add_argument('--ncase', required=True)
    ap.add_argument('--seed1', required=True)
    ap.add_argument('--seed2', required=True)
    args = ap.parse_args()

    if not (0.0 < args.depth_cm <= 2.0):
        raise SystemExit('Stage 8S2 depth must be in (0, 2] cm; use 0.001 cm for surface 0+')
    if args.radius_cm <= 0:
        raise SystemExit('Scoring radius must be positive')

    medium_name = 'WATER_1KEV' if args.medium == 'water' else 'RW3_NOMINAL'
    source_z = -args.ssd_cm
    hx = args.field_x_cm / 2.0
    hy = args.field_y_cm / 2.0

    rw3_block = f'''\n    :start RW3_NOMINAL:\n        elements = H, C, O, Ti\n        mass fractions = {RW3_H:.4f}, {RW3_C:.4f}, {RW3_O:.4f}, {RW3_TI:.4f}\n        bulk density = {RW3_DENSITY:.6f}\n        bremsstrahlung correction = NRC\n    :stop RW3_NOMINAL:\n'''

    text = f'''###############################################################################
# Stage 8S2: planar photon fluence spectrum, F50 TERAD geometry.
# Medium={args.medium}; depth={args.depth_cm:.4f} cm; beam={args.beam}.
# Surface is z=0, source is z={source_z:.4f} cm, field is specified at surface.
###############################################################################

:start geometry definition:
    :start geometry:
        library = egs_ndgeometry
        type = EGS_XYZGeometry
        name = spectral_phantom
        x-planes = -15 15
        y-planes = -15 15
        z-planes = {source_z:.4f} 0 12
        :start media input:
            media = AIR_1KEV {medium_name}
            set medium = 1 1
        :stop media input:
    :stop geometry:
    simulation geometry = spectral_phantom
:stop geometry definition:

:start media definition:
    ae = 0.512
    ap = 0.001
    ue = 0.811
    up = 0.300

    :start AIR_1KEV:
        elements = C, N, O, Ar
        mass fractions = 0.000124, 0.7552, 0.2318, 0.01283
        bulk density = 1.2048e-3
        bremsstrahlung correction = NRC
    :stop AIR_1KEV:

    :start WATER_1KEV:
        density correction file = water_icru90
        bremsstrahlung correction = NRC
    :stop WATER_1KEV:
{rw3_block}
:stop media definition:

:start source definition:
    :start source:
        name = terad_source
        library = egs_collimated_source
        charge = 0
        :start source shape:
            type = point
            position = 0 0 {source_z:.4f}
        :stop source shape:
        :start target shape:
            library = egs_rectangle
            rectangle = {-hx:.8f} {-hy:.8f} {hx:.8f} {hy:.8f}
        :stop target shape:
        :start spectrum:
            type = tabulated spectrum
            spectrum file = $EGS_HOME/tutor7pp/{args.beam}.ensrc
        :stop spectrum:
    :stop source:
    simulation source = terad_source
:stop source definition:

:start rng definition:
    type = ranmar
    initial seeds = {args.seed1} {args.seed2}
:stop rng definition:

:start MC transport parameter:
    Global PCUT = 0.001
    Global ECUT = 0.512
    Photon cross sections = mcdf-xcom
    Rayleigh scattering = On
    Photoelectron angular sampling = On
    Atomic relaxations = On
    Bound Compton scattering = On
    Radiative Compton corrections = On
    Brems cross sections = NIST
    Brems angular sampling = KM
    Spin effects = On
    Electron Impact Ionization = ik
    ESTEPE = 0.25
    XIMAX = 0.5
    Boundary crossing algorithm = exact
    Skin depth for BCA = 3
    Electron-step algorithm = EGSnrc
:stop MC transport parameter:

:start run control:
    ncase = {args.ncase}
:stop run control:

:start scoring options:
:stop scoring options:

:start ausgab object definition:
    :start ausgab object:
        name = spectral_plane
        library = egs_fluence_scoring
        type = planar
        scoring particle = photon
        score spectrum = yes
        score primaries = no
        verbose = no
        normalization = 1
        :start energy grid:
            number of bins = 250
            minimum kinetic energy = 0.001
            maximum kinetic energy = 0.251
            scale = linear
        :stop energy grid:
        :start planar scoring:
            contributing regions = ALL
            scoring circle = 0 0 {args.depth_cm:.6f} {args.radius_cm:.6f}
            scoring plane normal = 0 0 1
        :stop planar scoring:
    :stop ausgab object:
:stop ausgab object definition:
'''

    checks = [
        'library = egs_fluence_scoring',
        'score spectrum = yes',
        f'scoring circle = 0 0 {args.depth_cm:.6f} {args.radius_cm:.6f}',
        f'position = 0 0 {source_z:.4f}',
        f'rectangle = {-hx:.8f} {-hy:.8f} {hx:.8f} {hy:.8f}',
        f'spectrum file = $EGS_HOME/tutor7pp/{args.beam}.ensrc',
        'Radiative Compton corrections = On',
    ]
    for check in checks:
        if check not in text:
            raise SystemExit(f'Stage 8S2 self-check failed: {check}')

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f'Wrote {out}')
    print(f'beam={args.beam}; medium={args.medium}; depth={args.depth_cm:.4f} cm; SSD={args.ssd_cm:g} cm; surface field={args.field_x_cm:g}x{args.field_y_cm:g} cm2')


if __name__ == '__main__':
    main()
