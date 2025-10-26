pipeline {
    agent any

    environment {
        IMAGE_NAME = "lab2-app"
        CONTAINER_NAME = "lab2-app"
    }

    stages {

        /* -------------------------------
           1️⃣ CHECKOUT REPOSITORY
        --------------------------------*/
        stage('Checkout') {
            steps {
                echo "📥 Cloning repository..."
                checkout scm
            }
        }

        /* -------------------------------
           2️⃣ SETUP PYTHON ENVIRONMENT
        --------------------------------*/
        stage('Setup Python Environment') {
            steps {
                sh '''
                    echo "🐍 Setting up Python virtual environment..."
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest bandit safety
                '''
            }
        }

        /* -------------------------------
           3️⃣ RUN UNIT TESTS
        --------------------------------*/
        stage('Run Unit Tests') {
            steps {
                sh '''
                    echo "🧪 Running unit tests..."
                    . venv/bin/activate
                    pytest --maxfail=1 --disable-warnings -q || true
                '''
            }
        }

        /* -------------------------------
           4️⃣ STATIC CODE ANALYSIS (BANDIT)
        --------------------------------*/
        stage('Static Code Analysis (Bandit)') {
            steps {
                sh '''
                    echo "🔍 Running Bandit security scan..."
                    . venv/bin/activate
                    bandit -r . -x venv,__pycache__,.pytest_cache --skip B101 \
                        -f txt -o bandit-report.txt || true
                    echo "✅ Bandit completed"
                    ls -lh bandit-report.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bandit-report.txt', allowEmptyArchive: true
                }
            }
        }

        /* -------------------------------
           5️⃣ DEPENDENCY SCAN (SAFETY)
        --------------------------------*/
        stage('Dependency Scan (Safety)') {
            steps {
                sh '''
                    echo "🧾 Running Safety dependency check..."
                    . venv/bin/activate
                    safety check -r requirements.txt --full-report > safety-report.txt || true
                    echo "✅ Safety completed"
                    ls -lh safety-report.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'safety-report.txt', allowEmptyArchive: true
                }
            }
        }

        /* -------------------------------
           6️⃣ BUILD DOCKER IMAGE
        --------------------------------*/
        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "🐳 Building Docker image..."
                    # Remove old image if it exists
                    if docker images -q $IMAGE_NAME:latest > /dev/null; then
                        echo "⚠️ Old image found, removing..."
                        docker rmi -f $IMAGE_NAME:latest || true
                    fi
                    docker build -t $IMAGE_NAME:latest .
                '''
            }
        }

        /* -------------------------------
           7️⃣ CONTAINER IMAGE SCAN (TRIVY)
        --------------------------------*/
        stage('Container Scan (Trivy)') {
            steps {
                sh '''
                    echo "🧯 Scanning Docker image with Trivy..."
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                        aquasec/trivy:latest image --no-progress --severity HIGH,CRITICAL \
                        $IMAGE_NAME:latest > trivy-report.txt || true
                    echo "✅ Trivy completed"
                    ls -lh trivy-report.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-report.txt', allowEmptyArchive: true
                }
            }
        }

        /* -------------------------------
           8️⃣ DEPLOY USING DOCKER COMPOSE
        --------------------------------*/
        stage('Deploy (docker compose)') {
            steps {
                sh '''
                    echo "🚀 Deploying application..."

                    # Stop and remove old container if running
                    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
                        echo "🛑 Stopping old container..."
                        docker stop $CONTAINER_NAME || true
                        docker rm $CONTAINER_NAME || true
                    fi

                    # Deploy with docker compose
                    docker compose up -d

                    echo "✅ Deployment completed successfully!"
                '''
            }
        }
    }

    /* -------------------------------
       🔚 POST ACTIONS
    --------------------------------*/
    post {
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed! Check console logs and reports."
        }
        always {
            echo "🧹 Cleaning workspace..."
            cleanWs()
        }
    }
}
