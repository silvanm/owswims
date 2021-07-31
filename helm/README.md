# Installing via Helm

## 1. Add namespace:

```console
$ kubectl create namespace owswims
```

## 2. Deploy secrets
```console
$ kubectl create -f secret-owswims.yaml
```

## 3. Install using the values.yaml and secret.yaml files:

```console
$ helm install owswims --namespace owswims -f values.yaml .
```

# Updating via Helm

## 1. Change the values.yaml or/and secret.yaml file/files via a text editor

## 2. Upgrade ussing the values.yaml and secret.yaml files:

```console
$ helm upgrade owswims --namespace owswims -f values.yaml .
```

# Uninstalling via Helm

```console
$ helm delete owswims --namespace owswims
```
