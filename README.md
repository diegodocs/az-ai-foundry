# Azure AI Foundry - Use cases and examples

## 🚀 Features

- Create Evaluation Jobs
- Download Evaluation Metrics

## 🛠️ Tech Stack

- Visual Studio Code
- Git Bash
- GitHub(Repos, Actions)
- Python >= 3.13


## 🛠️ 3rd party dependencies

- azure-ai-projects
- azure-ai-evaluation
- azure-ai-ml

## 💡 All contributions are welcome

- create your fork
- add new features or improvements
- send your pull request


## ▶️ How to run locally

1. Clone this repo: git clone https://github.com/diegodocs/az-ai-foundry.git
1. rename file .env.template to .env and update all variable values based on your azure infra (steps below)
1. open your terminal and run: python evaluation_cloud.py

## Create your Azure Infra

### Defining variables

```powershell

# Naming conventions
$resourceAcronymRg = "rg"
$resourceAcronymSa = "sa"
$resourceAcronymKv = "kv"
$resourceAcronymHub = "hub"
$resourceAcronymProj = "proj"
# Global vars
$subscriptionId = "<your-subscriptionId>"
$appName = "genai"
$env = "lab"
$count = "001"
$location = "eastus"
# Resource vars
$rgName = "${env}-${count}-${appName}-${resourceAcronymRg}"
$saName = "${env}${count}${appName}${resourceAcronymSa}"
$kvName = "${env}-${count}-${appName}-${resourceAcronymKv}"
$hubName = "${env}-${count}-${appName}-${resourceAcronymHub}"
$projName = "${env}-${count}-${appName}-${resourceAcronymProj}"
$modelName = "gpt4-o"
$modelDeployName = "gpt4-o-deployment-002"
$saResourceId = "/subscriptions/${subscriptionId}/resourceGroups/${rgName}/providers/Microsoft.Storage/storageAccounts/${saName}"
$kvResourceId = "/subscriptions/${subscriptionId}/resourceGroups/${rgName}/providers/Microsoft.KeyVault/vaults/${kvName}"
$hubResourceId = "/subscriptions/${subscriptionId}/resourceGroups/${rgName}/providers/Microsoft.MachineLearningServices/workspaces/$hubName"

```

### Create a resource group

```powershell
az group create --name $rgName --location $location
```

### Create a storage account

```powershell
az storage account create --name $saName --resource-group $rgName --location $location --sku Standard_LRS
```

### Create a key vault

```powershell
az keyvault create --name $kvName --resource-group $rgName --location $location
```

### Create a hub using Azure Machine Learning SDK and CLI

```powershell
az ml workspace create --name $hubName --resource-group $rgName --location $location --storage-account $saName --key-vault $kvName --kind hub
```

### Create an AI Foundry project

```powershell
az ml workspace create --name $projName --resource-group $rgName --location $location --kind project --hub-id $hubResourceId
```

### Deploy the LLM model

```powershell
az ml model-deployment create --name $modelDeployName --workspace-name $projName --resource-group $rgName
```

### Retrieve the connection string for the AI Foundry project

```powershell
az ml connection list --workspace-name $projName --resource-group $rgName --query "[].{Name:name}"  --output table
```