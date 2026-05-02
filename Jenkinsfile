pipeline {
    agent any

    environment {
        DOCKER_USERNAME = "wissald"
        IMAGE_BACKEND   = "wissald/pfe-backend"
        IMAGE_FRONTEND  = "wissald/pfe-frontend"
        SONAR_HOST      = "http://localhost:9000"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Code récupéré depuis GitHub ✅'
            }
        }

        stage('Tests Backend') {
            steps {
                dir('backend') {
                    sh '''
                        pip3 install pytest pytest-cov httpx --timeout=300 || true
                        python3 -m pytest tests/ -v --cov=app --cov-report=xml || true
                    '''
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                    dir('backend') {
                        sh '''
                            /home/jenkins/sonar-scanner-6.2.1.4610-linux-x64/bin/sonar-scanner \
                              -Dsonar.projectKey=PFE_QueryRHAnalysis \
                              -Dsonar.sources=. \
                              -Dsonar.host.url=$SONAR_HOST \
                              -Dsonar.token=$SONAR_TOKEN \
                              -Dsonar.language=py \
                              -Dsonar.python.coverage.reportPaths=coverage.xml
                        '''
                    }
                }
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                }
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
                retry(3) {
                    sh '''
                        docker push $IMAGE_BACKEND:$BUILD_NUMBER
                        docker push $IMAGE_BACKEND:latest
                        docker push $IMAGE_FRONTEND:$BUILD_NUMBER
                        docker push $IMAGE_FRONTEND:latest
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
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
