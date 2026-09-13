pipeline {
    agent any

    environment {
        DOCKERHUB_USER = 'aymanis'
        IMAGE_NAME     = "${DOCKERHUB_USER}/todo-app"
        IMAGE          = "${IMAGE_NAME}:${env.BUILD_NUMBER}"
        IMAGE_LATEST   = "${IMAGE_NAME}:latest"
        K8S_NS         = 'todo'
    }

    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Tests unitaires') {
            steps {
                dir('app') {
                    sh '''
                        python3 -m venv .venv
                        . .venv/bin/activate
                        pip install --quiet --upgrade pip
                        pip install --quiet -r requirements-dev.txt
                        flake8 .
                        TODO_BACKEND=memory INIT_SCHEMA=0 pytest --cov=. --cov-report=term
                    '''
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'app/reports/tests.xml'
                }
            }
        }

        stage('Build image Docker') {
            steps {
                sh "docker build -t ${IMAGE} -t ${IMAGE_LATEST} app"
            }
        }

        stage('Push vers DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_PASS')]) {
                    sh """
                        echo "\$DH_PASS" | docker login -u "\$DH_USER" --password-stdin
                        docker push ${IMAGE}
                        docker push ${IMAGE_LATEST}
                        docker logout
                    """
                }
            }
        }

        stage('Deploiement sur Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh """
                        kubectl apply -f k8s/00-namespace.yaml
                        kubectl apply -f k8s/01-secret.yaml
                        kubectl apply -f k8s/02-configmap.yaml
                        kubectl apply -f k8s/03-postgres-pv.yaml
                        kubectl apply -f k8s/04-postgres.yaml
                        kubectl apply -f k8s/06-app-service.yaml

                        sed 's|__IMAGE__|${IMAGE}|' k8s/05-app-deployment.yaml | kubectl apply -f -

                        kubectl -n ${K8S_NS} rollout status deploy/todo-app --timeout=180s
                    """
                }
            }
        }

        stage('Verification') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh """
                        kubectl -n ${K8S_NS} get pods -o wide
                        kubectl -n ${K8S_NS} exec deploy/todo-app -- \\
                            curl -fs --retry 5 --retry-delay 3 http://localhost:5000/health
                        echo ""
                    """
                }
            }
        }
    }

    post {
        success { echo "Build ${env.BUILD_NUMBER} deploye : ${IMAGE}" }
        failure { echo "Build ${env.BUILD_NUMBER} en echec, voir le log ci-dessus." }
        always  {
            sh 'docker image prune -f || true'
            cleanWs()
        }
    }
}
