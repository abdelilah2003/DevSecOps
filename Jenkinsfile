pipeline {
  agent any
  options { timestamps() }
  environment {
    IMAGE_NAME = 'python-devsecops-jenkins_app'
    PY_VERSION = '3.11'
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Set up Python venv & deps') {
      steps {
        sh '''
          python${PY_VERSION} -m venv venv || python3 -m venv venv
          ./venv/bin/pip install --upgrade pip
          ./venv/bin/pip install -r requirements.txt
          ./venv/bin/pip install pytest bandit safety
        '''
      }
    }

    stage('Run Tests') {
      steps {
        sh '''
          mkdir -p test-results
          BASE_URL=http://localhost:5000 docker compose up -d app
          # Give container a moment to start
          sleep 3
          ./venv/bin/pytest -q --junitxml=test-results/pytest.xml
        '''
      }
      post {
        always {
          junit 'test-results/pytest.xml'
          sh 'docker compose down || true'
        }
      }
    }

    stage('Static Code Analysis (Bandit)') {
      steps {
        sh '''
            # Ignore the virtual environment and hidden folders
            bandit -r . -x venv,__pycache__,.pytest_cache --skip B101 -f txt -o bandit-report.txt || true
        '''
      }
    }
    

    stage('Dependency Scan (Safety)') {
      steps {
        sh './venv/bin/safety check --full-report || true'
      }
    }

    stage('Build Docker Image') {
      steps {
        sh '''
          docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest .
        '''
      }
    }

    stage('Container Scan (Trivy)') {
      steps {
        sh '''
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock             aquasec/trivy:latest image --no-progress --exit-code 0 ${IMAGE_NAME}:latest
        '''
      }
    }

    stage('Deploy (docker compose)') {
      when { branch 'main' }
      steps {
        sh '''
          docker compose up -d --build
        '''
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'test-results/*.xml', allowEmptyArchive: true
      cleanWs()
    }
  }
}
