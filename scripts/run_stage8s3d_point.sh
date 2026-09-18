#!/usr/bin/env bash
set -euo pipefail

: "${BEAM:?}" "${MEDIUM:?}" "${GEOM_ID:?}" "${APPLICATOR:?}" "${SSD:?}" "${FIELD_X:?}" "${FIELD_Y:?}" "${SEED1:?}" "${SEED2:?}"
NCASE="${NCASE:-300000000}"
NBATCH="${NBATCH:-30}"
XCSE="${XCSE:-64}"
RR="${RR:-64}"
EGSRUN="${EGSRUN:-/tmp/EGSnrc}"
SPECTRUM_VARIANT="${SPECTRUM_VARIANT:-hw_be0p8_a20}"

if [[ "$MEDIUM" != water && "$MEDIUM" != rw3 ]]; then
  echo "Invalid MEDIUM=$MEDIUM" >&2; exit 2
fi

sudo rm -f /etc/apt/sources.list.d/google-chrome.list || true
sudo apt-get update
sudo apt-get install -y git gcc g++ gfortran make tk grace libmotif-dev expect qtbase5-dev

rm -rf "$EGSRUN"
git clone https://github.com/nrc-cnrc/EGSnrc.git "$EGSRUN"
cd "$EGSRUN"
git checkout f4d029f625a6c96ef3456e0b6d91d46ffce613e7
test "$(git rev-parse HEAD)" = "f4d029f625a6c96ef3456e0b6d91d46ffce613e7"
export USER=runner EGS_BASE="$PWD"
./HEN_HOUSE/scripts/configure.expect gha.conf 3

export EGS_HOME="$EGSRUN/egs_home/"
export EGS_CONFIG="$EGSRUN/HEN_HOUSE/specs/gha.conf"
export HEN_HOUSE="$EGSRUN/HEN_HOUSE/"
export PATH="$HEN_HOUSE/scripts/bin:$HEN_HOUSE/bin/gha:$EGS_HOME/bin/gha:$PATH"
cd "$EGS_HOME/egs_chamber"
python - <<'PY'
from pathlib import Path
p=Path('Makefile')
t=p.read_text()
old='CPP_SOURCES = $(C_ADVANCED_SOURCES)'
new=('CPP_SOURCES = $(subst $(EGS_SOURCEDIR)get_inputs.mortran,'
     '$(EGS_SOURCEDIR)rad_compton1.mortran '
     '$(EGS_SOURCEDIR)get_inputs.mortran,$(C_ADVANCED_SOURCES))')
if old not in t:
    raise SystemExit('Could not patch egs_chamber Makefile')
p.write_text(t.replace(old,new,1))
PY
make
test -x "$EGS_HOME/bin/gha/egs_chamber"

cd "$GITHUB_WORKSPACE"
mkdir -p stage8s3d_inputs stage8s3d_logs
spec="$(find stage8s3d_spectra -type f -path "*/${SPECTRUM_VARIANT}/${BEAM}.ensrc" | head -n1)"
test -n "$spec" && test -s "$spec"
cp "$spec" "$EGS_HOME/egs_chamber/${BEAM}.ensrc"

name="stage8s3d_${GEOM_ID}_${BEAM}_${MEDIUM}"
python scripts/build_stage8s3_input.py \
  --template inputs/stage3b_czarnecki_modelA_vrt.template.egsinp \
  --output "stage8s3d_inputs/${name}.egsinp" \
  --medium "$MEDIUM" --source-model finite_7p5mm \
  --beam "$BEAM" --ssd "$SSD" --field-x "$FIELD_X" --field-y "$FIELD_Y" \
  --ncase "$NCASE" --nbatch "$NBATCH" --xcse "$XCSE" --rr "$RR" \
  --seed1 "$SEED1" --seed2 "$SEED2"

input="stage8s3d_inputs/${name}.egsinp"
grep -Fq "spectrum file = \$EGS_HOME/egs_chamber/${BEAM}.ensrc" "$input"
grep -Fq 'library = egs_circle' "$input"
grep -Fq 'radius = 0.375000' "$input"
grep -Fq 'translation = 0 0 -2.000000' "$input"
python - "$input" "$FIELD_X" "$FIELD_Y" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); fx=float(sys.argv[2]); fy=float(sys.argv[3])
expected=f"rectangle = {-fx/2:.8f} {-fy/2:.8f} {fx/2:.8f} {fy/2:.8f}"
t=p.read_text()
if expected not in t:
    raise SystemExit(f"Missing surface aperture: {expected}")
PY
if [[ "$MEDIUM" == water ]]; then
  grep -Fq 'name = chamber_in_water' "$input"
  grep -Fq 'name = dose_to_water' "$input"
else
  grep -Fq 'name = chamber_in_rw3' "$input"
  grep -Fq 'name = dose_to_rw3' "$input"
fi

cp "$input" "$EGS_HOME/egs_chamber/${name}.egsinp"
cd "$EGS_HOME/egs_chamber"
set -o pipefail
"$EGS_HOME/bin/gha/egs_chamber" -i "$name" 2>&1 | tee "$GITHUB_WORKSPACE/stage8s3d_logs/${name}.log"
cd "$GITHUB_WORKSPACE"
log="stage8s3d_logs/${name}.log"
grep -Eq 'Global Pcut[[:space:]]+0\.001' "$log"
grep -Eq 'Global Ecut[[:space:]]+0\.512' "$log"
grep -Eq 'Radiative Compton corrections[[:space:]]+On' "$log"
grep -Fq 'Range rejection = Russian Roullette (RR)' "$log"
grep -Eq "last case[[:space:]]*=[[:space:]]*${NCASE}" "$log"
grep -Eq 'finishSimulation\(egs_chamber\)[[:space:]]+0' "$log"
if grep -Eqi 'segmentation fault|fatal error|geometry error|Turning radiative Compton corrections OFF' "$log"; then exit 1; fi

python scripts/summarize_stage8s3d_point.py \
  --log "$log" \
  --output "stage8s3d_point_${GEOM_ID}_${BEAM}_${MEDIUM}.csv" \
  --beam "$BEAM" --medium "$MEDIUM" --geometry "$GEOM_ID" --applicator "$APPLICATOR" \
  --ssd "$SSD" --field-x "$FIELD_X" --field-y "$FIELD_Y" \
  --spectrum-variant "$SPECTRUM_VARIANT" --ncase "$NCASE" \
  --seed1 "$SEED1" --seed2 "$SEED2"
