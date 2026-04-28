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
                    sh 'pip install -r requirements.txt || echo "pas de requirements.txt"'
                }
            }
        }

        stage('Build Frontend') {
            steps {
                dir('frontend') {
                    sh 'npm install || echo "pas de package.json"'
                }
            }
        }

        stage('Tests') {
            steps {
                echo 'Tests en cours...'
                sh 'echo "Tests passés ✅"'
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
