pipeline {
    agent any

    environment {
        GITHUB_URL = 'https://github.com/lafamila/scheduler-full.git'
        GITHUB_CRED_ID = 'github-token'
        GITHUB_BRANCH = 'main'
        REPO_TAG = 'scheduler-full'
        CONTAINER_NAME = 'scheduler-full'
        DB_USER = credentials('console-db-user')
        DB_PASSWORD = credentials('console-db-password')
        DB_SCHEME = credentials('dad-db-scheme')
        DB_PORT = credentials('console-db-port')
        DB_HOST = credentials('console-db-host')
    }
    stages {
        stage('Clone') {
            steps {
                echo 'Clone start'
                // git plugin을 사용하여 레포지토리 코드를 클론
                git branch: GITHUB_BRANCH, credentialsId: GITHUB_CRED_ID, url: GITHUB_URL
                sh 'ls'
                echo 'Clone end'
            }
        }


        stage('Build') {
            steps {
                echo 'Build start'
                sh 'docker image build -t $REPO_TAG:latest .'
                sh 'docker image tag $REPO_TAG:latest $REPO_TAG:$BUILD_NUMBER'
                echo 'Build end'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploy start'
                script{
                    try{
                        sh 'docker stop $CONTAINER_NAME'
                        sh 'docker rm $CONTAINER_NAME'
                    } catch (Exception e) {
                        echo 'No container name: $CONTAINER_NAME'
                    }

                    sh 'docker run --name $CONTAINER_NAME -d --network host -e DB_USER=$DB_USER -e DB_PASSWORD=$DB_PASSWORD -e DB_HOST=$DB_HOST -e DB_PORT=$DB_PORT -e DB_SCHEME=$DB_SCHEME -p 20023:20023 $REPO_TAG'
                }
                echo 'Deploy end'
            }
        }
    }
}