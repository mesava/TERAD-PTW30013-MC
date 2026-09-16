#!/usr/bin/env bash
set -euo pipefail

EGSRUN="${EGSRUN:-/tmp/EGSnrc}"
NCASE="${NCASE:-5000}"

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
python -m pip install 'spekpy==2.5.4' numpy scipy
python scripts/generate_spekpy_spectra.py
cp spectra/Q120.ensrc "$EGS_HOME/egs_chamber/Q120.ensrc"
mkdir -p stage8s3_smoke

for medium in water rw3; do
  name="stage8s3_smoke_${medium}_finite"
  python scripts/build_stage8s3_input.py \
    --template inputs/stage3b_czarnecki_modelA_vrt.template.egsinp \
    --output "stage8s3_smoke/${name}.egsinp" \
    --medium "$medium" --source-model finite_7p5mm \
    --beam Q120 --ssd 50 --field-x 8 --field-y 10 \
    --ncase "$NCASE" --nbatch 2 --xcse 64 --rr 64 --seed1 7101 --seed2 8101
  grep -Fq 'library = egs_circle' "stage8s3_smoke/${name}.egsinp"
  grep -Fq 'radius = 0.375000' "stage8s3_smoke/${name}.egsinp"
  grep -Fq 'translation = 0 0 -52.000000' "stage8s3_smoke/${name}.egsinp"
  cp "stage8s3_smoke/${name}.egsinp" "$EGS_HOME/egs_chamber/${name}.egsinp"
  cd "$EGS_HOME/egs_chamber"
  set -o pipefail
  "$EGS_HOME/bin/gha/egs_chamber" -i "$name" 2>&1 | tee "$GITHUB_WORKSPACE/stage8s3_smoke/${name}.log"
  cd "$GITHUB_WORKSPACE"
  grep -Eq "last case[[:space:]]*=[[:space:]]*${NCASE}" "stage8s3_smoke/${name}.log"
  grep -Eq 'finishSimulation\(egs_chamber\)[[:space:]]+0' "stage8s3_smoke/${name}.log"
done

echo 'finite_source_smoke=PASS' > stage8s3_smoke/gate.txt
