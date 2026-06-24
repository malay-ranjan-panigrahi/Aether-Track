# 🌩️ Aether-Track

### Self-Taught DevOps & GitOps Pipeline with AI-Assisted Failure Diagnosis

A hands-on portfolio project demonstrating an end-to-end GitOps delivery lifecycle on Kubernetes — with an **AI agent that diagnoses build failures and suggests fixes**. Built on a local cluster to demonstrate the full workflow.

![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=jenkins&logoColor=white)
![ArgoCD](https://img.shields.io/badge/ArgoCD-EF7B4D?style=for-the-badge&logo=argo&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-0F1689?style=for-the-badge&logo=helm&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_API-8E75B2?style=for-the-badge&logo=google&logoColor=white)

---

<!-- TODO: Record a short GIF of the pipeline running + the AI healer output, embed here.
     A screen-capture GIF is the most effective "animation" GitHub allows (it strips JS/CSS).
     Recommended: capture the Jenkins failure then ai_healer.py printing its remediation block. -->
<!-- ![Demo](docs/demo.gif) -->

## 📖 Table of Contents
- [Overview](#-overview)
- [Architecture](#-architecture)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Repository Structure](#-repository-structure)
- [Quick Start](#-quick-start)
- [Monitoring](#-monitoring)
- [Engineering Decisions](#-engineering-decisions)
- [Roadmap](#-roadmap)
- [Author](#-author)

---

## 🎯 Overview

Aether-Track deploys a simple Flask weather app — but **the app is the vehicle, not the point.** The real project is the automated delivery pipeline around it, and what happens when a build breaks.

It demonstrates three things I wanted to learn end-to-end:

| Focus | How Aether-Track addresses it |
|---|---|
| 🔄 Keeping cluster state in sync with Git | Pull-based GitOps with ArgoCD auto-sync |
| 🐛 Faster failure triage | An AI agent reads build logs and proposes a root cause + fix |
| 📊 Kubernetes-native monitoring | Prometheus + Grafana, with a ServiceMonitor for app metrics |

---

## 🏗️ Architecture

\`\`\`mermaid
flowchart LR
    DEV[Developer Push] --> JENKINS[Jenkins CI]
    JENKINS -->|build & push image| REG[(Docker Hub)]
    JENKINS -->|helm package| HELM[Helm Chart]
    JENKINS -->|update values.yaml + commit| GIT[(Git Repo)]
    GIT -->|watches & syncs| ARGO[ArgoCD]
    ARGO -->|deploy| K8S[Kubernetes Cluster]
    K8S --> PROM[Prometheus]
    PROM --> GRAF[Grafana]
    JENKINS -.->|on failure| AI[ai_healer.py]
    AI -.->|logs to Gemini| REPORT[Root-Cause Suggestion]
\`\`\`

The pipeline is **pull-based** — ArgoCD reconciles the cluster from Git, rather than Jenkins pushing directly to the cluster. This keeps Git as the single source of truth, so rollbacks are a \`git revert\` and the cluster state is always recoverable from version control.

---

## ⚙️ Key Features

### 1. 🔁 Automated GitOps Workflow
- **CI (Jenkins):** builds the Docker image, pushes to Docker Hub, packages the Helm chart, applies build-number versioning.
- **CD (ArgoCD):** watches \`k8s/aether-app/\` and reconciles the cluster to match Git.
- **Closed loop:** on a successful build, Jenkins updates the image tag in \`values.yaml\` and commits it back to Git — no manual manifest edits.

### 2. 🤖 AI-Assisted Failure Diagnosis
A custom Python agent (\`ai_healer.py\`) that runs on build failure.

| Stage | What happens |
|---|---|
| **Trigger** | Fires automatically in the Jenkins \`post { failure }\` block |
| **Context** | Reads \`build_error.log\` and extracts the failure output |
| **Analysis** | Sends the log to the Google Gemini API with an SRE-oriented prompt |
| **Output** | Prints a structured root cause, suggested fix, and prevention tip |

> **Diagnosis-only by design.** The agent *suggests* fixes — it does not apply them. It only sees the build log, not the full application context, so a human reviews and approves any change. This human-in-the-loop guardrail prevents the AI from confidently shipping a wrong fix.

### 3. 📡 Monitoring
- Prometheus + Grafana (via \`kube-prometheus-stack\`) for cluster and namespace-level metrics.
- The Flask app exposes custom metrics on \`/metrics\` via \`prometheus-flask-exporter\`.
- A \`ServiceMonitor\` is defined to scrape the app's metrics endpoint. *(See Roadmap — the scrape-label wiring is being finalized.)*

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Application | Python, Flask, prometheus-flask-exporter, Gunicorn |
| Containerization | Docker |
| CI | Jenkins (declarative pipeline) |
| CD / GitOps | ArgoCD, Helm |
| Orchestration | Kubernetes |
| Observability | Prometheus, Grafana, ServiceMonitor |
| AI Layer | Google Gemini API |
| Registry | Docker Hub |

---

## 📁 Repository Structure

\`\`\`
aether-track/
├── app/                      # Python Flask weather application
├── cicd/
│   ├── Jenkinsfile           # CI/CD pipeline definition
│   └── ai_healer.py          # AI agent for build-failure analysis
├── k8s/
│   └── aether-app/           # Helm chart
│       ├── templates/        # Deployment, Service, ServiceMonitor
│       ├── values.yaml       # Image tag auto-updated by Jenkins
│       └── Chart.yaml
├── Dockerfile
└── README.md
\`\`\`

---

## 🚀 Quick Start

### Prerequisites
- A Kubernetes cluster (this was built and tested on a local KIND cluster)
- Jenkins with \`github-creds\`, \`docker-hub-creds\`, \`gemini-api-key\`, and \`weather-api-key\` configured in the Credentials store
- ArgoCD installed in the cluster
- \`kubectl\` and \`helm\` available locally

### 1. Create the namespace
\`\`\`bash
kubectl create namespace aether-prod
\`\`\`

### 2. Provision secrets
\`\`\`bash
kubectl create secret generic aether-secrets \\
  --from-literal=weather-api-key=\${WEATHER_KEY} \\
  --from-literal=gemini-api-key=\${GEMINI_KEY} \\
  -n aether-prod
\`\`\`

### 3. Configure Jenkins
Create a pipeline job pointing at this repository; it uses the \`Jenkinsfile\` under \`cicd/\`.

### 4. Register the ArgoCD application
Point an ArgoCD Application at the \`k8s/aether-app/\` path with auto-sync enabled. Each commit Jenkins pushes then triggers a reconciliation.

---

## 📈 Monitoring

- **Cluster & node metrics:** provided out-of-the-box by \`kube-prometheus-stack\` (pre-built Grafana dashboards for nodes, pods, and namespaces).
- **App metrics:** the Flask app exposes Prometheus metrics at \`/metrics\`; a \`ServiceMonitor\` is defined to scrape them.

> Note: the cluster-level dashboards are live and working. Wiring the app's custom metrics into Prometheus (correcting the ServiceMonitor's release label) is in progress — see Roadmap.

---

## 🧠 Engineering Decisions

A few deliberate choices, and why:

- **No \`:latest\` tags.** Every image is tagged with the Jenkins build number, so rollbacks are deterministic and deploys are traceable.
- **Helm over raw manifests.** Versioned charts make rollbacks a single command instead of a hunt through Git history.
- **Pull-based (ArgoCD) over push-based CD.** The cluster reconciles itself from Git rather than Jenkins pushing to it — so state survives a Jenkins outage and is always recoverable from version control.
- **\`cleanup\` post-condition for teardown, not \`always\`.** In Jenkins, \`always\` runs *before* the \`failure\` block — so putting workspace cleanup in \`always\` would delete the log the AI healer needs. Cleanup lives in a \`cleanup\` block, which runs last.
- **Secrets via Kubernetes Secrets + Jenkins credentials, never in the repo.** Keys are injected at runtime through \`secretKeyRef\` and the Jenkins credential store.

---

## 🗺️ Roadmap

- [ ] Fix the ServiceMonitor release label and confirm custom Flask metrics are scraped end-to-end
- [ ] Build Grafana dashboards for app-level latency / error-rate / throughput
- [ ] Convert the Jenkins job to a Multibranch Pipeline with branch-gated deploys
- [ ] Multi-environment promotion (dev → staging → prod) via ArgoCD ApplicationSets
- [ ] Progressive delivery (canary / blue-green) with Argo Rollouts
- [ ] Migrate the healer from the deprecated \`google.generativeai\` package to \`google.genai\`
- [ ] Extend the AI agent to act on runtime alerts, not just build failures

---

## 👨‍💻 Author

**Malay Ranjan Panigrahi**
Technical Support Engineer → transitioning to DevOps / SRE
📍 Bangalore, India

[LinkedIn](https://www.linkedin.com/) · [GitHub](https://github.com/malay-ranjan-panigrahi)

---

*If this project was useful or interesting to you, a ⭐ is appreciated.*
