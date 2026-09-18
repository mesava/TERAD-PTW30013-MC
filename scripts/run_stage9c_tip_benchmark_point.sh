#!/usr/bin/env bash
set -euo pipefail
: "${CASE:?}" "${TIP_CM:?}" "${TIP_MM:?}" "${BEAM:?}" "${SEED1:?}" "${SEED2:?}"
NCASE="${NCASE:-300000000}"; NBATCH="${NBATCH:-30}"; XCSE="${XCSE:-64}"; RR="${RR:-64}"
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

export EGS_HOME="$EGSRUN/egs_home/" EGS_CONFIG="$EGSRUN/HEN_HOUSE/specs/gha.conf" HEN_HOUSE="$EGSRUN/HEN_HOUSE/"
export PATH="$HEN_HOUSE/scripts/bin:$HEN_HOUSE/bin/gha:$EGS_HOME/bin/gha:$PATH"
cd "$EGS_HOME/egs_chamber"
python - <<'PY'
from pathlib import Path
p=Path('Makefile'); t=p.read_text()
old='CPP_SOURCES = $(C_ADVANCED_SOURCES)'
new=('CPP_SOURCES = $(subst $(EGS_SOURCEDIR)get_inputs.mortran,'
     '$(EGS_SOURCEDIR)rad_compton1.mortran '
     '$(EGS_SOURCEDIR)get_inputs.mortran,$(C_ADVANCED_SOURCES))')
if old not in t: raise SystemExit('Could not patch egs_chamber Makefile')
p.write_text(t.replace(old,new,1))
PY
make
test -x "$EGS_HOME/bin/gha/egs_chamber"

cd "$GITHUB_WORKSPACE"
mkdir -p stage9c_inputs stage9c_logs
spec="$(find stage9c_benchmark_spectra -type f -path "*/spekcalc/${BEAM}.ensrc" | head -n1)"
test -n "$spec" && test -s "$spec"
cp "$spec" "$EGS_HOME/egs_chamber/${BEAM}.ensrc"

name="stage9c_${CASE}_${BEAM}"
python scripts/build_stage9c_tip_benchmark.py \
  --template inputs/stage3b_czarnecki_modelA_vrt.template.egsinp \
  --output "stage9c_inputs/${name}.egsinp" --beam "$BEAM" --tip-cm "$TIP_CM" \
  --ncase "$NCASE" --nbatch "$NBATCH" --xcse "$XCSE" --rr "$RR" --seed1 "$SEED1" --seed2 "$SEED2"
grep -Fq 'set label = chamber_cavity 10 16 20' "stage9c_inputs/${name}.egsinp"
grep -Fq 'z-planes = -50 -2 18' "stage9c_inputs/${name}.egsinp"
grep -Fq 'cavity mass = 7.832972283369083e-04' "stage9c_inputs/${name}.egsinp"

cp "stage9c_inputs/${name}.egsinp" "$EGS_HOME/egs_chamber/${name}.egsinp"
cd "$EGS_HOME/egs_chamber"
set -o pipefail
"$EGS_HOME/bin/gha/egs_chamber" -i "$name" 2>&1 | tee "$GITHUB_WORKSPACE/stage9c_logs/${name}.log"
cd "$GITHUB_WORKSPACE"
log="stage9c_logs/${name}.log"
grep -Eq 'Global Pcut[[:space:]]+0\.001' "$log"
grep -Eq 'Global Ecut[[:space:]]+0\.512' "$log"
grep -Eq 'Radiative Compton corrections[[:space:]]+On' "$log"
grep -Fq 'Range rejection = Russian Roullette (RR)' "$log"
grep -Eq "last case[[:space:]]*=[[:space:]]*${NCASE}" "$log"
grep -Eq 'finishSimulation\(egs_chamber\)[[:space:]]+0' "$log"
if grep -Eqi 'segmentation fault|fatal error|geometry error|Turning radiative Compton corrections OFF' "$log"; then exit 1; fi

python scripts/summarize_stage9c_tip_benchmark_point.py \
  --log "$log" --output "stage9c_point_${CASE}_${BEAM}.csv" \
  --case "$CASE" --tip-mm "$TIP_MM" --beam "$BEAM" --ncase "$NCASE" --seed1 "$SEED1" --seed2 "$SEED2"
