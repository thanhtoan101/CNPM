targetScope = 'resourceGroup'

@description('Deployment environment name, for example dev, staging, or production.')
@allowed([
  'dev'
  'staging'
  'production'
])
param environmentName string = 'dev'

@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Fully qualified container image, preferably pinned to an immutable digest.')
param containerImage string

@description('Azure Container Registry login server, for example example.azurecr.io.')
@minLength(1)
param registryServer string

@description('Existing user-assigned identity resource ID with AcrPull on the registry.')
@minLength(1)
param registryPullIdentityResourceId string

@description('Minimum number of replicas. Production should use at least two.')
@minValue(0)
param minReplicas int = environmentName == 'production' ? 2 : 0

@description('Maximum number of replicas.')
@minValue(1)
param maxReplicas int = environmentName == 'production' ? 10 : 3

var suffix = uniqueString(resourceGroup().id, environmentName)
var serviceName = 'film-ai-${environmentName}-${suffix}'

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-film-ai-${environmentName}-${suffix}'
  location: location
  properties: {
    retentionInDays: 30
    sku: {
      name: 'PerGB2018'
    }
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

resource managedEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-film-ai-${environmentName}-${suffix}'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}

resource aiService 'Microsoft.App/containerApps@2024-03-01' = {
  name: serviceName
  location: location
  identity: {
    type: 'SystemAssigned,UserAssigned'
    userAssignedIdentities: {
      '${registryPullIdentityResourceId}': {}
    }
  }
  properties: {
    environmentId: managedEnvironment.id
    configuration: {
      activeRevisionsMode: 'Multiple'
      registries: [
        {
          server: registryServer
          identity: registryPullIdentityResourceId
        }
      ]
      ingress: {
        external: false
        targetPort: 8080
        transport: 'http'
        allowInsecure: false
      }
    }
    template: {
      containers: [
        {
          name: 'ai-service'
          image: containerImage
          env: [
            {
              name: 'AI_HOST'
              value: '0.0.0.0'
            }
            {
              name: 'AI_PORT'
              value: '8080'
            }
            {
              name: 'AI_ENVIRONMENT'
              value: environmentName
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 8080
                scheme: 'HTTP'
              }
              initialDelaySeconds: 10
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/ready'
                port: 8080
                scheme: 'HTTP'
              }
              initialDelaySeconds: 3
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

output serviceName string = aiService.name
output serviceUrl string = 'https://${aiService.properties.configuration.ingress.fqdn}'
output principalId string = aiService.identity.principalId
