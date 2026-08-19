@minLength(5)
@maxLength(15)
param appName string
param location string = 'eastus2'
param image string
param environmentId string
param sourceSha string

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${appName}-api'
  location: location
  tags: {
    application: 'sepsis-early-warning'
    dataClass: 'synthetic-only'
    environment: 'demo'
  }
  properties: {
    managedEnvironmentId: environmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: { external: true, targetPort: 8000, transport: 'auto' }
    }
    template: {
      containers: [{
        name: 'api'
        image: image
        resources: { cpu: json('0.25'), memory: '0.5Gi' }
        env: [{ name: 'SOURCE_SHA', value: sourceSha }]
      }]
      scale: {
        minReplicas: 0
        maxReplicas: 2
        rules: [{ name: 'http', http: { metadata: { concurrentRequests: '10' } } }]
      }
    }
  }
}

output appUrl string = 'https://${app.properties.configuration.ingress.fqdn}'
