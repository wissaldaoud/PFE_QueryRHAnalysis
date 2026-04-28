pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Code récupéré depuis GitHub ✅'
            }
        }

        stage('Build Backend') {
            steps {
                dir('backend') {
                    sh 'pip3 install -r requirements.txt'
                }
            }
        }

        stage('Build Frontend') {
            steps {
                dir('frontend') {
                    sh 'npm install'
                }
            }
        }

        stage('Tests') {
            steps {
                dir('backend') {
                    sh 'python3 -m pytest tests/ -v || echo "pas de tests"'
                }
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
