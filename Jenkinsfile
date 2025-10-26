pipeline {
    agent any

    environment {
        IMAGE_NAME = "devsecops_app"
        CONTAINER_NAME = "devsecops_app"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "📥 Cloning repository..."
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    echo "🐍 Setting up Python environment..."
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    echo "🧪 Running unit tests..."
                    . venv/bin/activate
                    pytest --maxfail=1 --disable-warnings -q || true
                '''
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                sh '''
                    echo "🔍 Running Bandit (Static Analysis)..."
                    . venv/bin/activate
                    bandit -r . -x venv,__pycache__,.pytest_cache --skip B101 \
                        -f txt -o bandit-report.txt || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bandit-report.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Dependency Scan (Safety)') {
            steps {
                sh '''
                    echo "🧾 Scanning dependencies (Safety)..."
                    . venv/bin/activate
                    safety check -r requirements.txt --full-report > safety-report.txt || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'safety-report.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "🐳 Building Docker image..."
                    
                    # Remove old image if it exists
                    if docker images -q $IMAGE_NAME:latest > /dev/null; then
                        echo "⚠️ Removing old image..."
                        docker rmi -f $IMAGE_NAME:latest || true
                    fi

                    docker build -t $IMAGE_NAME:latest .
                '''
            }
        }

        stage('Container Scan (Trivy)') {
            steps {
                sh '''
                    echo "🧯 Scanning Docker image with Trivy..."
                    trivy image --severity HIGH,CRITICAL --exit-code 0 $IMAGE_NAME:latest > trivy-report.txt || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-report.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Deploy (docker compose)') {
            steps {
                sh '''
                    echo "🚀 Deploying application..."
                    
                    # Stop and remove old container if running
                    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
                        echo "🛑 Stopping existing container..."
                        docker stop $CONTAINER_NAME || true
                        docker rm $CONTAINER_NAME || true
                    fi

                    # Deploy using docker compose
                    docker compose up -d
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed! Check logs and reports."
        }
        always {
            cleanWs()
        }
    }
}
