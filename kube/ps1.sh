#!/usr/bin/bash
echo -e "Source this file with:\n . ps1.sh"

if [ -f ~/bin/kube-ps1.sh ]; then
   echo "Sourcing ~/bin/kube-ps1.sh"
else
   echo "File ~/bin/kube-ps1.sh does not exist. Downloading now."
    wget -O ~/bin/kube-ps1.sh https://raw.githubusercontent.com/jonmosco/kube-ps1/refs/heads/master/kube-ps1.sh
fi

source ~/bin/kube-ps1.sh
export PS1='\u@\h \w $(kube_ps1)\$'
