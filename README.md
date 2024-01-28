# Progetto di Sistemi Distribuiti e Big Data
## Gravagno - Di Mauro

### Istruzioni per il build del docker compose
Per effettuare il build del progetto basta utilizzare il file docker-compose.yaml:  
avendo docker engine avviato, posizionarsi nella root directory del progetto e  
digitare nel terminale il seguente comando:  
***docker compose up***  
in questo modo non solo verranno costruite le immagini dei microservizi a partire dai dockerfile  
definiti nelle diverse directory, ma la costruzione e l'avvio dei container avverrà rispettando una catena di dipendenza  
specificata nel file in questione.  
Da sottolineare è la presenza di un dockerfile nella root directory che
contiene  operazioni comuni a microuser, microphoto e microtagger: questi si distinguono solo per i diversi requirements da dover installare per il loro funzionamento,   
per cui si è deciso di creare questo dockerfile comune che viene, di volta in volta,  contestualizzato all'interno del docker compose per costruire il microservizio opportuno.  
Inoltre, verranno creati anche i volumi per le componenti stateful del progetto (i database e prometheus)  
e le diverse reti in cui si collocano i microservizi.

Qualora, invece, si volesse effettuare il build del singolo microservizio, posizionarsi nella root specifica  
e digitare il seguente comando, specificando nome dell'immagine e tag:  
***docker build -t <image_name>:<image_tag>***

Per creare ed avviare un container basterà digitare il seguente comando:  
***docker run --name <container_name> -p <local_port>:<container_port> -v <volume_mapping> -e <env_variable> <image_name>:<image_tag>***

### Istruzioni per il deploy su K8S
Per effettuare il deploy su K8S in locale utilizzare Kind ed installare Kubectl: 
su MacOS è possibile installare entrambi utilizzando il gestore dei pacchetti HomeBrew.
Posizionarsi all'interno della directory k8s e creare il cluster usando il seguente comando:  
***kind create cluster --config=config-yml***  
in questo modo verrà creato un cluster costituito da due nodi: un control plane node e  
un worker node. Il cluster sarà raggiungibile tramite localhost, usando le porte 80 (HTTP) e  
443 (HTTPS).  
Creato il cluster effettuare il deploy dei microservizi col seguente comando:  
***kubectl apply -f \_\_filename\_\_.yml***  
Nello specifico, l'ordine in cui fare il deploy è il seguente:
- NGINX - ingress.yml:  
  effettuare prima il deploy del modulo NGINX col comando:  
  ***kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml***  
  e poi applicare il file di configurazione ingress.yml;
- DATABASE:  
  effettuare il deploy dei database (userDB.yml, photoDB.yml e slaDB.yml), in quanto i relativi microservizi,
  una volta avviati, proveranno subito a connettersi con essi. Se non ci fossero restituirebbero un errore;
- MINIO:  
  effettuare il deploy del bucket minio (minio.yml) per la stessa motivazione esposta prima;
- KAFKA:  
  effetuare il deploy del broker Kafka in quanto essenziale alla comunicazione tra microphoto e microtagger;
- MICROSERVIZI:  
  infine, sarà possibile effettuare il deploy di tutti i microservizi che gestiranno backend (microuser.yml,
  microphoto.yml e microtagger.yml) e QoS (prometheus.yml e slamanager.yml).

