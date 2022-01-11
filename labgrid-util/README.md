# Deploy to Labgrid

## GitHub Actions

Auto deply is in the repo under `.github/workflows/main.yml`.
The workflow has a login with the username `gitrunner` and a password set in the github secrets. After login the runner executes a script (deploy.sh) on the server with the current branch as an argument.

## Setup LED-Detection from github actions

Make sure the user `gitrunner` has it's home directory set at the directory where you want to have youre entry point if the LED-Detection.

The sample script to execute is found in `labfrid-util/deploy.sh`.

In this file you can see that the script navigates into a directory named `leddet` make sure this directory exist. 
```bash
# pull new repo
cd leddet && git clone https://github.com/morgenmuesli/LED-Detection.git
```

## Update Labgrid Client/Exporter
