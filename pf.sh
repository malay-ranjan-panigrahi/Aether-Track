#!/bin/bash

echo "port forwarding for grafana and argocd !"

kubectl port-forward -n monitoring svc/kube-prom-stack-grafana 3000:80 &

kubectl port-forward svc/argocd-server -n argocd 8087:443 &

