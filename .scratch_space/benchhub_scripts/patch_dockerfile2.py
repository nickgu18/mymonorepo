with open("worker/Dockerfile", "r") as f:
    content = f.read()

# gsutil is missing in the slim container! We need to install google-cloud-cli.
# Wait, let's just add it to the apt-get update line. Wait, gcloud cli requires adding a source or downloading.
# Let's download the gcloud tar.gz, but wait, maybe we can just install it via curl

new_install = """# System basics & Docker (for DinD)
RUN apt-get update && apt-get install -y git curl zip
RUN curl -fsSL https://get.docker.com | sh

# Install Google Cloud CLI for gsutil
RUN curl -sSL https://sdk.cloud.google.com | bash -s -- --disable-prompts
ENV PATH=$PATH:/root/google-cloud-sdk/bin
"""

content = content.replace("""# System basics & Docker (for DinD)
RUN apt-get update && apt-get install -y git curl zip
RUN curl -fsSL https://get.docker.com | sh""", new_install)

with open("worker/Dockerfile", "w") as f:
    f.write(content)
