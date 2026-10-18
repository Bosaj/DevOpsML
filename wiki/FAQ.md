# FAQ

**Is this one application or a collection of exercises?**
A collection. Each `tpX` folder is self-contained with its own dependencies and, where applicable, its own test suite. There's no shared entry point across labs.

**Why does CI only run `tp2` and `tp4`'s test suites?**
Those are the two labs with real, hermetic pytest suites that don't need external infrastructure. `tp3` needs a Jenkins server, `tp5` needs Docker to run its full stack meaningfully, `tp6` is a written spec with no code, and `tp7` needs a full DVC/MLflow environment and a dataset download. CI instead runs a syntax/import check on `tp1`, `tp5`, and `tp7` so broken code is still caught without requiring that infrastructure.

**Is `tp6` actually implemented?**
No — it's a lab specification describing the Kubernetes exercise (minikube, kubectl, namespaces, pods) as reference material. There's no manifest or deployment code in the repository.

**What does the `tp7` pipeline actually train?**
A model on the UCI Adult Income dataset, orchestrated as DVC stages (download → preprocess → split) with training and inference scripts tracked via MLflow. The logged run reached about 85% test accuracy.

**Do I need Poetry for every lab?**
No, only `tp2` and `tp4`, which ship a `pyproject.toml`. `tp5` uses a plain `requirements.txt`, and `tp7` lists its dependencies directly in the README's install command.

**Can I run the Jenkins or SonarQube integrations without setting up those servers?**
You can still run the underlying pytest suites locally (`poetry run pytest`) — that's what CI does. Actually exercising the `Jenkinsfile` or getting a SonarQube quality report requires pointing a real Jenkins/SonarQube instance at the repo, which is outside the scope of what's checked into it.
