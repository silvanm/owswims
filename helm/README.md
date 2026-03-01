# Installing via Helm

## 1. Add namespace:

```console
$ kubectl create namespace owswims
```

## 2. Deploy secrets

Secrets are encrypted with [SOPS](https://github.com/getsops/sops) using GCP KMS (`mpom-shared/europe-west6/sops/sops-key`). To apply them:

```console
$ sops --decrypt secrets.yaml | kubectl apply -f -
```

## 3. Install using the values.yaml file:

```console
$ helm install owswims --namespace owswims -f values.yaml .
```

# Updating via Helm

## 1. Change the values.yaml file via a text editor

## 2. Upgrade:

```console
$ helm upgrade owswims --namespace owswims -f values.yaml .
```

# Managing Secrets

## Prerequisites

- [SOPS](https://github.com/getsops/sops) installed (`brew install sops`)
- GCP credentials with KMS access to `mpom-shared` project
- SOPS config is in `/.sops.yaml` at the repo root

## Editing secrets

To edit `secrets.yaml` in your `$EDITOR`:

```console
$ sops secrets.yaml
```

This decrypts the file, opens it for editing, and re-encrypts on save. Values are base64-encoded Kubernetes secret data.

## Viewing current secrets

```console
$ sops --decrypt secrets.yaml
```

## Adding a new secret

1. Decrypt: `sops --decrypt secrets.yaml > /tmp/secrets-plain.yaml`
2. Add your key under `data:` with the base64-encoded value: `echo -n 'myvalue' | base64`
3. Re-encrypt: `sops --encrypt /tmp/secrets-plain.yaml > secrets.yaml`
4. Clean up: `rm /tmp/secrets-plain.yaml`

Or simply use `sops secrets.yaml` to edit in-place.

## CI/CD

The GitHub Actions deploy workflow automatically decrypts and applies secrets before the Helm upgrade. The `gitlab@mpom-shared.iam.gserviceaccount.com` service account has `cloudkms.cryptoKeyDecrypter` access to the KMS key.

# Uninstalling via Helm

```console
$ helm delete owswims --namespace owswims
```
