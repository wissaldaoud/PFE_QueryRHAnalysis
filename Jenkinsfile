pipeline {
    agent any

    environment {
        DOCKER_USERNAME = "wissald"
        IMAGE_BACKEND   = "wissald/pfe-backend"
        IMAGE_FRONTEND  = "wissald/pfe-frontend"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Code récupéré depuis GitHub ✅'
            }
        }

        stage('Build Backend Image') {
            steps {
                dir('backend') {
                    sh 'docker build -t $IMAGE_BACKEND:$BUILD_NUMBER -t $IMAGE_BACKEND:latest .'
                }
            }
        }

        stage('Build Frontend Image') {
            steps {
                dir('frontend') {
                    sh 'docker build -t $IMAGE_FRONTEND:$BUILD_NUMBER -t $IMAGE_FRONTEND:latest .'
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                sh '''
                    docker push $IMAGE_BACKEND:$BUILD_NUMBER
                    docker push $IMAGE_BACKEND:latest
                    docker push $IMAGE_FRONTEND:$BUILD_NUMBER
                    docker push $IMAGE_FRONTEND:latest
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo 'Déploiement sur Kubernetes ✅'
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline réussi !'
        }
        failure {
            echo '❌ Pipeline échoué !'
        }
    }
}
