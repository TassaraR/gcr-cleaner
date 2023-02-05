FROM python:3.10-slim-buster

RUN apt-get update -y \
 && apt-get install sudo -y \
 && sudo apt-get install apt-transport-https ca-certificates gnupg curl -y \
 && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
 && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
 && sudo apt-get update -y
 && sudo apt-get install google-cloud-cli -y

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["python", "cleaner/main.py"]
