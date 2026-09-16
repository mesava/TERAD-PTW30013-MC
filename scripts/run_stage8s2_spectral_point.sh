#!/usr/bin/env bash
set -euo pipefail

: "${BEAM:?}" "${MEDIUM:?}" "${DEPTH_CM:?}" "${DEPTH_TAG:?}" "${SEED1:?}" "${SEED2:?}"
NCASE="${NCASE:-50000000}"
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

cd "$EGS_HOME/tutor7pp"
python - <<'PY'
from pathlib import Path
p=Path('Makefile')
t=p.read_text()
old='CPP_SOURCES = $(C_ADVANCED_SOURCES)'
new=('CPP_SOURCES = $(subst $(EGS_SOURCEDIR)get_inputs.mortran,'
     '$(EGS_SOURCEDIR)rad_compton1.mortran '
     '$(EGS_SOURCEDIR)get_inputs.mortran,$(C_ADVANCED_SOURCES))')
if old not in t:
    raise SystemExit('Could not patch tutor7pp Makefile for Radiative Compton support')
p.write_text(t.replace(old,new,1))
PY
make
test -x "$EGS_HOME/bin/gha/tutor7pp"

cd "$GITHUB_WORKSPACE"
mkdir -p stage8s2_inputs stage8s2_logs stage8s2_outputs
cp "stage8s2_spectra/${BEAM}.ensrc" "$EGS_HOME/tutor7pp/${BEAM}.ensrc"
name="stage8s2_${BEAM}_${MEDIUM}_${DEPTH_TAG}"
python scripts/build_stage8s2_spectral_input.py \
  --output "stage8s2_inputs/${name}.egsinp" \
  --beam "$BEAM" --medium "$MEDIUM" --depth-cm "$DEPTH_CM" \
  --ssd-cm 50 --field-x-cm 8 --field-y-cm 10 --radius-cm 0.5 \
  --ncase "$NCASE" --seed1 "$SEED1" --seed2 "$SEED2"
cp "stage8s2_inputs/${name}.egsinp" "$EGS_HOME/tutor7pp/${name}.egsinp"

cd "$EGS_HOME/tutor7pp"
set -o pipefail
"$EGS_HOME/bin/gha/tutor7pp" -i "$name" 2>&1 | tee "$GITHUB_WORKSPACE/stage8s2_logs/${name}.log"
cd "$GITHUB_WORKSPACE"
log="stage8s2_logs/${name}.log"
grep -Eq 'Global Pcut[[:space:]]+0\.001' "$log"
grep -Eq 'Global Ecut[[:space:]]+0\.512' "$log"
grep -Eq 'Radiative Compton corrections[[:space:]]+On' "$log"
grep -Fq 'Fluence Scoring (spectral_plane)' "$log"
grep -Eq "last case = ${NCASE}" "$log"

agr="$EGS_HOME/tutor7pp/${name}_photon.agr"
test -s "$agr"
cp "$agr" "stage8s2_outputs/${name}_photon.agr"
python scripts/summarize_stage8s2_spectrum.py \
  --agr "$agr" \
  --output-spectrum "stage8s2_spectrum_${BEAM}_${MEDIUM}_${DEPTH_TAG}.csv" \
  --output-summary "stage8s2_summary_${BEAM}_${MEDIUM}_${DEPTH_TAG}.csv" \
  --beam "$BEAM" --medium "$MEDIUM" --depth-cm "$DEPTH_CM" --ncase "$NCASE"
