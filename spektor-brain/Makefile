src/service/data/nn4.small2.v1.t7: src/service/data/nn4.small2.v1.t7.bz2
	bunzip2 -k src/service/data/nn4.small2.v1.t7.bz2

src/service/data/shape_predictor_68_face_landmarks.dat: src/service/data/shape_predictor_68_face_landmarks.dat.bz2
	bunzip2 -k src/service/data/shape_predictor_68_face_landmarks.dat.bz2


docker-build: src/service/data/nn4.small2.v1.t7 src/service/data/shape_predictor_68_face_landmarks.dat
	docker build --no-cache --rm -t spektor/brain .

docker-run:
	docker run -p 5000:5000 --cap-add=NET_ADMIN -d --cpus 2 --name spektor spektor/brain

docker-sh:
	sudo docker exec -i -t spektor /bin/bash

mrproper:
	docker stop spektor
	docker rm spektor
	docker rmi spektor/brain
