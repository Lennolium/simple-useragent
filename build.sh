#!/bin/bash

# Script will exit if exit code is not 0.
set -e

# Define colors for log.
_info()    { printf " \033[1m[INFO]\033[0m $1 " ; }
_ok()      { printf " \033[1m\033[32m[OK]\033[0m $1 " ; }
_error()   { printf " \033[1m\033[31m[ERROR]\033[0m $1 " ; }
_logo()    { printf " \033[1m $1\033[0m \n" ; }
_success()    { printf "\033[0m\033[32mSUCCESS\033[0m \n" ; }
_warn()    { printf "\033[1m\033[33mWARNING\033[0m \n" ; }
_failed()    { printf "\033[1m\033[31mFAILED\033[0m \n" ; exit 1; }


# Define rainbow colors
RB_RED=$(printf '\033[1;38;5;196m')
RB_ORANGE=$(printf '\033[1;38;5;202m')
RB_YELLOW=$(printf '\033[1;38;5;226m')
RB_GREYEL=$(printf '\033[1;38;5;184m')
RB_GREEN=$(printf '\033[1;38;5;082m')
RB_BLUGRE=$(printf '\033[1;38;5;033m')
RB_BLUE=$(printf '\033[1;38;5;021m')
RB_INDIGO=$(printf '\033[1;38;5;093m')
RB_VIOLET=$(printf '\033[1;38;5;163m')
RB_RESET=$(printf '\033[0m')


# Get os and architecture.
case $(uname -s) in
    Linux) os="Linux" ;;
    Darwin) os="macOS" ;;
    CYGWIN*|MINGW*|MSYS*) os="Windows" ;;
    *) os="Unknown" ;;
esac

case $(uname -m) in
    x86_64) arch="x64" ;;
    arm64) arch="arm64" ;;
    arm32) arch="arm32" ;;
    *) arch="Unknown" ;;
esac


# Save name and version of the package from __init__.py in src folder.
package_directory=$(find src -mindepth 2 -maxdepth 2 -type f -name '__init__.py' -exec dirname {} \;)
package_name=$(basename "$package_directory")
version=$(grep '__version__ =' "$package_directory/__init__.py" | sed -E 's/^.*"([^"]+)".*$/\1/')

# Get the minimum required Python version from setup.cfg.
min_py_version="python$(grep 'python_requires' setup.cfg | sed -E 's/^.*>=//')"
min_py_version_num="${min_py_version:6}"

if which "${min_py_version}" &> /dev/null; then
    py_inst="$("$min_py_version" --version)"
else
    py_inst="$(python3 --version)"
fi


# Header.
_logo "--------------------------------------------------------------------------  \n"
printf "\n"
printf "\n"
printf "  %s  █▌  %s   ▀▀▀▀▀▀%s ║█    ╫█%s ▐█µ   ▐█%s  ▄██▀▀██▌%s  ██  %s   ▀└%s █▌   ╒█▌%s █µ      █▌%s  \n" $RB_RED $RB_ORANGE $RB_YELLOW $RB_GREYEL $RB_GREEN $RB_BLUGRE $RB_BLUE $RB_INDIGO $RB_VIOLET $RB_RESET
printf "  %s ▐█   %s         %s ███▌  ██%s ████  ██%s ██     ╟█%s ▐█   %s  ▐█%s ║█    ╫█%s ║██▌  ╓███ %s  \n" $RB_RED $RB_ORANGE $RB_YELLOW $RB_GREYEL $RB_GREEN $RB_BLUGRE $RB_BLUE $RB_INDIGO $RB_VIOLET $RB_RESET
printf "  %s ██   %s  ▀▀▀▀▀▀%s ╒█Γ└██▓█%s  █▌ ██▓█▌%s▐█      ██%s ██   %s  ██%s ██    █▌%s ██ ███▀ ██ %s  \n" $RB_RED $RB_ORANGE $RB_YELLOW $RB_GREYEL $RB_GREEN $RB_BLUGRE $RB_BLUE $RB_INDIGO $RB_VIOLET $RB_RESET
printf "  %s┌▀    %s        %s ██   ▀██%s ║█   ╙██%s └██   ╓██%s  █▌   %s ╒█▌%s ██   ██%s ╒█▌  ╙  ╒█Γ %s  \n" $RB_RED $RB_ORANGE $RB_YELLOW $RB_GREYEL $RB_GREEN $RB_BLUGRE $RB_BLUE $RB_INDIGO $RB_VIOLET $RB_RESET
printf "  %s -▀▀▀▀%s ╝▀▀▀▀▀▀%s ▀▀     ▀%s ▀▀     ▀%s   ▀▀█▀▀ %s  ╘▀▀▀▀▀%s ╝▀ %s  ▀██▀  %s ╝▀      ╝▀  %s  \n" $RB_RED $RB_ORANGE $RB_YELLOW $RB_GREYEL $RB_GREEN $RB_BLUGRE $RB_BLUE $RB_INDIGO $RB_VIOLET $RB_RESET
_logo " "
_logo "             P Y T H O N    B  U  I  L  D     S  C  R  I  P  T              \n"
printf "\n"


# General information.
_logo "S y s t e m   I n f o r m a t i o n :"
_logo "-------------------------------------"
_logo "Hostname: $(hostname)"
_logo "Operating System: $os"
_logo "Architecture: $arch"
_logo "Shell: $SHELL"
_logo "Python version: $py_inst"
_logo "PWD: $(pwd)"
_logo "Log file location: ./trace.log"
_logo "Execution time: $(date +'%y/%m/%d %H:%M:%S')"
_logo "-------------------------------------------------------------------------- \n\n"


# Check if Python 3 is installed and install it if not.
_info "Checking and installing system dependencies (${min_py_version}) ..."
if test ! "$(which "${min_py_version}")" && test $os = "Linux"; then
    _warn
    _info "P${min_py_version:1} is not installed! Installing with apt-get ..."
    sudo apt-get update 2>&1 | tee -a trace.log
    sudo apt-get install "${min_py_version}" 2>&1 | tee -a trace.log && _success || _failed
    # From python version 3.3 and above, venv is included in the standard library.
    # sudo apt-get install "${min_py_version}"-venv 2>&1 | tee -a trace.log && _success || _failed
elif test ! "$(which "${min_py_version}")" && test $os = "macxOS";
then
    _warn
    _info "P${min_py_version:1} is not installed! Installing with Homebrew ..."
    /bin/bash -c \
    "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)" 2>&1 | tee -a trace.log
    brew update 2>&1 | tee -a trace.log
    brew install "${min_py_version}" 2>&1 | tee -a trace.log && _success || _failed
elif test ! "$(which "${min_py_version}")" && test $os = "Windows";
then
    _warn
    _info "P${min_py_version:1} is not installed! Installing with Chocolatey ..."
    if ! command -v choco &> /dev/null; then
        _info "\nDownloading and installing Chocolatey ..."
        powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
    fi
    choco install "${min_py_version}" 2>&1 | tee -a trace.log && _success || _failed
else
    _success
fi


# Creating dist folder and delete the content of it (to remove old .app builds).
_info "Deleting old builds and logs ..."
rm -f ./trace.log
mkdir -p ./dist/
rm -Rf ./dist/* && _success || _failed


# Create temporary build venv and delete old venv.
_info "Creating temporary virtual environment ..."
if [ -d "./.buildvenv" ] ; then
    rm -r -f ./.buildvenv
fi
${min_py_version} -m venv .buildvenv >> trace.log 2>&1 && _success || _failed


# Activate virtual environment, update and install requirements.
_info "Installing and updating requirements ..."
source ./.buildvenv/bin/activate >> trace.log 2>&1
pip"$min_py_version_num" install --upgrade pip >> trace.log 2>&1
${min_py_version} -m pip install pip-tools >> trace.log 2>&1
pip"$min_py_version_num" install -r requirements-dev.txt >> trace.log 2>&1 && _success || _failed


# Running tests, but first check if tests folder exists.
if [ ! -d "./tests" ]; then
    _info "No tests folder found. Skipping tests ..."; _warn
else
    _info "Running unit tests now ..."
    cd src || exit
    ${min_py_version} -m unittest discover -s ../tests >> ../trace.log 2>&1 && _success || _failed
    cd .. || exit
fi

# Override the version variable of setup.cfg with the version number of __init__.py.
_info "Updating the version variable in 'setup.cfg' to $version ..."
tmpfile=$(mktemp)
sed "s/^version =.*/version = $version/" setup.cfg > "$tmpfile"
mv "$tmpfile" setup.cfg && _success || _failed

# Update the version badge in README.md.
_info "Updating the version badge in 'README.md' to $version ..."
tmpfile=$(mktemp)
sed "s|https://img.shields.io/badge/Version-.*-brightgreen|https://img.shields.io/badge/Version-$version-brightgreen|" README.md > "$tmpfile"
mv "$tmpfile" README.md && _success || _failed


# Build dist and verify.
_info "Building the distribution files. This can take a while ..."
${min_py_version} -m build >> trace.log 2>&1 && _success || _failed
_info "Verifying the distribution files ...\n"
twine check ./dist/*.tar.gz ./dist/*.whl


# Generate sha256 hash files.
_info "Generating SHA256 checksum files..."
cd ./dist || exit
for file in *; do
    if [ -f "$file" ]; then
        shasum -a 256 "$file" > "$file.sha256"
    fi
done
if [ $? -eq 0 ]; then _success; else _failed; fi

_info "Validating the checksum files ...\n"
for file in *.sha256; do
    if sha256sum -c "$file" >> ../trace.log 2>&1; then
        printf " Checking $file: \033[0m\033[32mPASSED\033[0m \n"
    else
        printf " Checking $file:" && _failed
    fi
done
cd .. || exit


# Upload build to PyPI. Credentials are in '~.pypirc'.
_info "Uploading to the built package PyPI ..."
twine upload --repository pypi ./dist/*.tar.gz ./dist/*.whl && _success || _failed


# Exit out of virtual environment, cleanup egg files and delete venv.
_info "Cleaning up ..."
deactivate
sleep 2
rm -rf ./.buildvenv
rm -rf "./src/${package_name}.egg-info" && _success || _failed


_info "Exiting ..."
sleep 1
echo "Bye!"
exit 0