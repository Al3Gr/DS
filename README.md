# Progetto di Sistemi Distribuiti e Big Data
## Gravagno - Di Mauro

### Istruzioni per il build del docker compose
Per effettuare il build del progetto basta utilizzare il file docker-compose.yaml:  

avendo docker engine aperto, posizionarsi nella root directory del progetto e 
digitare nel terminale il seguente comando:

***docker compose up***

verranno costruite le immagini dei container a partire dal dockerfile,
verranno costruiti ed avviati i container; inoltre, verrano creati i volumi dei database e di prometheus,
così come verranno create delle reti interne, in modo da isolare le parti di frontend, backend e QoS


### Istruzioni per il deploy su K8S
Per effettuare il deploy su K8S in locale utilizzare Kind ed installare Kubectl: 
su MacOS è possibile installare entrambi utilizzando il gestore dei pacchetti HomeBrew.
Fatto ciò, posizionarsi all'interno della directory k8s e digitare il seguente comando:

***kubectl apply -f \_\_filename\_\_.yml***

in questo modo verrà fatto il deploy su kubernates dei diversi microservizi.
In particolare, il file di ingress.yml definisce un Ingress basato su NGINX,
per cui è necessario effettuarne il deploy tramite il seguente comando:

***kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml***

Fatto ciò, sarà possibile interaggire con i microservizi presenti all'interno del cluster.
