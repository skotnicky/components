{{- define "ccf.netbox.name" -}}
{{- printf "%s" .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "ccf.netbox.fullname" -}}
{{- printf "%s" (include "ccf.netbox.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "ccf.netbox.labels" -}}
app.kubernetes.io/name: {{ include "ccf.netbox.name" . }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | trunc 63 | trimSuffix "-" }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "ccf.netbox.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ccf.netbox.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "ccf.netbox.authSecretName" -}}
{{ printf "%s-auth" (include "ccf.netbox.fullname" .) }}
{{- end -}}

{{- define "ccf.netbox.dbSecretName" -}}
{{- default (include "ccf.netbox.authSecretName" .) .Values.netbox.externalDatabase.existingSecretName -}}
{{- end -}}

{{- define "ccf.netbox.dbSecretKey" -}}
{{- default "db_password" .Values.netbox.externalDatabase.existingSecretKey -}}
{{- end -}}

{{- define "ccf.netbox.tasksSecretName" -}}
{{- default (include "ccf.netbox.authSecretName" .) .Values.netbox.tasksDatabase.existingSecretName -}}
{{- end -}}

{{- define "ccf.netbox.tasksSecretKey" -}}
{{- default "tasks_password" .Values.netbox.tasksDatabase.existingSecretKey -}}
{{- end -}}

{{- define "ccf.netbox.cacheSecretName" -}}
{{- default (include "ccf.netbox.authSecretName" .) .Values.netbox.cachingDatabase.existingSecretName -}}
{{- end -}}

{{- define "ccf.netbox.cacheSecretKey" -}}
{{- default "cache_password" .Values.netbox.cachingDatabase.existingSecretKey -}}
{{- end -}}

{{- define "ccf.netbox.superuserSecretName" -}}
{{- default (include "ccf.netbox.authSecretName" .) .Values.netbox.superuser.existingSecretName -}}
{{- end -}}
