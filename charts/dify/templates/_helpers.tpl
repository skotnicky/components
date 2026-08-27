{{- define "ccf-dify.storagePermissionsFix.apiClaimName" -}}
{{- $claim := .Values.storagePermissionsFix.apiClaimName -}}
{{- if $claim -}}
{{- $claim -}}
{{- else -}}
{{- .Release.Name | trunc 58 -}}
{{- end -}}
{{- end -}}

{{- define "ccf-dify.storagePermissionsFix.pluginClaimName" -}}
{{- $claim := .Values.storagePermissionsFix.pluginClaimName -}}
{{- if $claim -}}
{{- $claim -}}
{{- else -}}
{{- printf "%s-plugin-daemon" (.Release.Name | trunc 43) -}}
{{- end -}}
{{- end -}}
