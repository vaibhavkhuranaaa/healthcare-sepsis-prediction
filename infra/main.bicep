@minLength(5)
@maxLength(15)
param appName string
param image string
param location string = 'eastus2'
param sourceSha string

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
    sourceSha: sourceSha
  }
}

output appUrl string = app.outputs.appUrl
