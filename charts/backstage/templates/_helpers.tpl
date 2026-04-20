{{- define "ccf.backstage.name" -}}
{{- default .Chart.Name .Values.backstage.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "ccf.backstage.fullname" -}}
{{- if .Values.backstage.fullnameOverride -}}
{{- .Values.backstage.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s" (include "ccf.backstage.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "ccf.backstage.labels" -}}
app.kubernetes.io/name: {{ include "ccf.backstage.name" . }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | trunc 63 | trimSuffix "-" }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "ccf.backstage.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ccf.backstage.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "ccf.backstage.serviceAccountName" -}}
{{- if .Values.backstage.serviceAccount.create -}}
{{- default (include "ccf.backstage.fullname" .) .Values.backstage.serviceAccount.name -}}
{{- else -}}
default
{{- end -}}
{{- end -}}
