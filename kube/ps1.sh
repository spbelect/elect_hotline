#!/usr/bin/bash
echo -e "Source this file with:\n . ps1.sh"
export PS1='\u@\h \w $(kube_ps1)\$'
