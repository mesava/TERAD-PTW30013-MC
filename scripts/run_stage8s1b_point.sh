#!/usr/bin/env bash
set -euo pipefail

: "${CONFIG:?}" "${BEAM:?}" "${APPLICATOR:?}" "${SSD:?}" "${FIELD_X:?}" "${FIELD_Y:?}" "${VARIANT:?}" "${TIO2:?}" "${SEED1:?}" "${SEED2:?}"
NCASE="${NCASE:-300000000}"
NBATCH="${NBATCH:-30}"
XCSE="${XCSE:-64}"
RR="${RR:-64}"
EGSRUN="${EGSRUN:-/tmp/EGSnrc}"

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
mkdir -p stage8s1b_inputs stage8s1b_logs
cp "stage8s1b_spectra/${BEAM}.ensrc" "$EGS_HOME/egs_chamber/${BEAM}.ensrc"
name="stage8s1b_${CONFIG}_${VARIANT}"
python scripts/build_stage6_rw3_tio2_sensitivity.py \
  --template inputs/stage3b_czarnecki_modelA_vrt.template.egsinp \
  --output "stage8s1b_inputs/${name}.egsinp" \
  --beam "$BEAM" --ssd "$SSD" --field-x "$FIELD_X" --field-y "$FIELD_Y" \
  --ncase "$NCASE" --nbatch "$NBATCH" --xcse "$XCSE" --rr "$RR" \
  --seed1 "$SEED1" --seed2 "$SEED2" --tio2-mass-fraction "$TIO2"

grep -Fq 'bulk density = 1.045000' "stage8s1b_inputs/${name}.egsinp"
grep -Fq 'name = chamber_in_rw3' "stage8s1b_inputs/${name}.egsinp"
cp "stage8s1b_inputs/${name}.egsinp" "$EGS_HOME/egs_chamber/${name}.egsinp"

cd "$EGS_HOME/egs_chamber"
set -o pipefail
"$EGS_HOME/bin/gha/egs_chamber" -i "$name" 2>&1 | tee "$GITHUB_WORKSPACE/stage8s1b_logs/${name}.log"
cd "$GITHUB_WORKSPACE"
log="stage8s1b_logs/${name}.log"
grep -Eq 'Global Pcut[[:space:]]+0\.001' "$log"
grep -Eq 'Global Ecut[[:space:]]+0\.512' "$log"
grep -Eq 'Radiative Compton corrections[[:space:]]+On' "$log"
grep -Fq 'Range rejection = Russian Roullette (RR)' "$log"
grep -Eq "last case[[:space:]]*=[[:space:]]*${NCASE}" "$log"
grep -Eq 'finishSimulation\(egs_chamber\)[[:space:]]+0' "$log"

python scripts/summarize_stage8s1b_tio2.py \
  --log "$log" \
  --output "stage8s1b_point_${CONFIG}_${VARIANT}.csv" \
  --config "$CONFIG" --beam "$BEAM" --applicator "$APPLICATOR" \
  --ssd "$SSD" --field-x "$FIELD_X" --field-y "$FIELD_Y" \
  --variant "$VARIANT" --tio2 "$TIO2" \
  --ncase "$NCASE" --seed1 "$SEED1" --seed2 "$SEED2"
