pipeline {
  agent any
  environment {
    DB_CREDENTIALS = credentials('DB_USER_MAKEUOFT')
    DB_NAME = credentials('DB_NAME_MAKEUOFT')
    DB_SERVER = credentials('DB_SERVER_MAKEUOFT')
    SECRET_KEY = credentials('SECRET_KEY_MAKEUOFT')
    ENVIRONMENT = credentials('ENVIRONMENT')
  }
  stages {
    stage('Build') {
      steps {
//          #Delete existing docking image
          sh 'docker rmi --force makeuoft-site:latest'
//          #Build new image
          sh 'docker-compose -f deployment/docker-compose.yml build'
      }
    }
    stage('Deploy') {
      when {
        branch "master"
      }
      steps {
        sh '''
          #!/bin/bash
          # Copy static files
          rm -r /var/www/makeuoft/public_html/static/
          cp -r application/static /var/www/makeuoft/public_html/static
          '''

        sh '''
          #!/bin/bash
          # Bring down the old container
          docker-compose -f deployment/docker-compose.yml down
          '''

        sh '''
          #!/bin/bash
          # Migrate and bring up the new container
          docker-compose -f deployment/docker-compose.yml run --rm --entrypoint "" web flask db upgrade
          docker-compose -f deployment/docker-compose.yml -p makeuoft up -d
          '''
      }
    }
  }
}
