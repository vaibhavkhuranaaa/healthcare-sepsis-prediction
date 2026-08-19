@description('Globally unique short application name')
@minLength(5)
@maxLength(15)
param appName string
param location string = 'eastus2'

var tags = {
  application: 'sepsis-early-warning'
  dataClass: 'synthetic-only'
  environment: 'demo'
}

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${appName}-env'
  location: location
  tags: tags
  properties: {}
}

output environmentId string = environment.id
