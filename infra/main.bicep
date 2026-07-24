@minLength(5)
@maxLength(15)
param appName string
param image string
param location string = 'eastus2'

module foundation './foundation.bicep' = {
  name: 'foundation'
  params: { appName: appName, location: location }
}

module app './app.bicep' = {
  name: 'app'
  params: {
    appName: appName
    location: location
    image: image
    environmentId: foundation.outputs.environmentId
    registryServer: foundation.outputs.registryLoginServer
    appInsightsConnectionString: foundation.outputs.appInsightsConnectionString
  }
}

output appUrl string = app.outputs.appUrl
